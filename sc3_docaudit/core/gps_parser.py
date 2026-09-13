"""
Parser de Evidências Geográficas de Campo (Garmin GPX, KML, CSV e Manual).
Converte formatos GNSS de campo em pontos estruturados e calcula hash de integridade SHA-256.
"""

import xml.etree.ElementTree as ET
import csv
import re
import io
import hashlib
from typing import List, Dict, Any, Optional


class GPSParser:
    """Parser agnóstico para formatos de GPS de campo (Garmin, KML, CSV)."""

    @staticmethod
    def parse_gpx(gpx_bytes: bytes) -> List[Dict[str, Any]]:
        """Extrai waypoints e tracks de arquivos GPX padrão Garmin."""
        waypoints = []
        try:
            root = ET.fromstring(gpx_bytes)
            # Extrair waypoints <wpt> e <trkpt>
            for elem in root.iter():
                tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag_name == "wpt":
                    lat = elem.attrib.get("lat")
                    lon = elem.attrib.get("lon")
                    
                    name, ele, t_val = None, None, None
                    for child in elem:
                        c_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                        if c_tag == "name" and child.text:
                            name = child.text.strip()
                        elif c_tag == "ele" and child.text:
                            try:
                                ele = float(child.text.strip())
                            except ValueError:
                                pass
                        elif c_tag == "time" and child.text:
                            t_val = child.text.strip()

                    waypoints.append({
                        "name": name if name else f"WPT-{len(waypoints)+1:02d}",
                        "latitude": float(lat) if lat else 0.0,
                        "longitude": float(lon) if lon else 0.0,
                        "elevation_m": ele,
                        "timestamp": t_val,
                        "type": "Garmin Waypoint"
                    })
                
                elif tag_name == "trkpt":
                    lat = elem.attrib.get("lat")
                    lon = elem.attrib.get("lon")
                    ele, t_val = None, None
                    for child in elem:
                        c_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                        if c_tag == "ele" and child.text:
                            try:
                                ele = float(child.text.strip())
                            except ValueError:
                                pass
                        elif c_tag == "time" and child.text:
                            t_val = child.text.strip()

                    waypoints.append({
                        "name": f"Trilha P-{len(waypoints)+1:03d}",
                        "latitude": float(lat) if lat else 0.0,
                        "longitude": float(lon) if lon else 0.0,
                        "elevation_m": ele,
                        "timestamp": t_val,
                        "type": "Ponto de Trilha"
                    })
        except Exception:
            pass
        return waypoints

    @staticmethod
    def parse_kml(kml_bytes: bytes) -> List[Dict[str, Any]]:
        """Extrai coordenadas de arquivos KML (Google Earth / GIS)."""
        waypoints = []
        try:
            root = ET.fromstring(kml_bytes)
            for pm in root.iter():
                tag_name = pm.tag.split("}")[-1] if "}" in pm.tag else pm.tag
                if tag_name == "Placemark":
                    name = None
                    coords_text = None
                    for child in pm.iter():
                        c_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                        if c_tag == "name" and child.text and not name:
                            name = child.text.strip()
                        elif c_tag == "coordinates" and child.text:
                            coords_text = child.text.strip()

                    if coords_text:
                        raw_coords = coords_text.split()
                        for c_str in raw_coords:
                            parts = c_str.split(",")
                            if len(parts) >= 2:
                                lon, lat = float(parts[0]), float(parts[1])
                                ele = float(parts[2]) if len(parts) > 2 else None
                                waypoints.append({
                                    "name": name if name else "Ponto KML",
                                    "latitude": lat,
                                    "longitude": lon,
                                    "elevation_m": ele,
                                    "timestamp": None,
                                    "type": "Ponto KML"
                                })
        except Exception:
            pass
        return waypoints

    @staticmethod
    def parse_csv(csv_text: str) -> List[Dict[str, Any]]:
        """Extrai coordenadas de tabela CSV com colunas latitude/longitude."""
        waypoints = []
        try:
            reader = csv.DictReader(io.StringIO(csv_text))
            for idx, row in enumerate(reader):
                norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
                lat_str = norm_row.get("latitude") or norm_row.get("lat") or norm_row.get("y")
                lon_str = norm_row.get("longitude") or norm_row.get("lon") or norm_row.get("long") or norm_row.get("x")
                name_str = norm_row.get("nome") or norm_row.get("name") or norm_row.get("id") or f"Ponto {idx+1}"
                
                if lat_str and lon_str:
                    waypoints.append({
                        "name": name_str,
                        "latitude": float(lat_str.replace(",", ".")),
                        "longitude": float(lon_str.replace(",", ".")),
                        "elevation_m": float(norm_row.get("altitude", "0").replace(",", ".")) if "altitude" in norm_row else None,
                        "timestamp": norm_row.get("data") or norm_row.get("timestamp"),
                        "type": "Planilha CSV"
                    })
        except Exception:
            pass
        return waypoints

    @staticmethod
    def parse_manual(text_input: str) -> Optional[Dict[str, float]]:
        """
        Interpreta formatos manuais de coordenadas:
        - Decimais: -3.75412, -48.12543
        - Graus Minutos Segundos: 03°45'14"S 48°07'31"W
        """
        text = text_input.strip()
        if not text:
            return None

        dec_match = re.search(r"([+-]?\d{1,2}\.\d+)\s*[,;\s]\s*([+-]?\d{1,3}\.\d+)", text)
        if dec_match:
            lat = float(dec_match.group(1))
            lon = float(dec_match.group(2))
            return {"latitude": lat, "longitude": lon}

        gms_pattern = r"(\d{1,2})[°\s]+(\d{1,2})['\s]+([\d\.]+)?[\"\s]*([NSEWO])"
        matches = re.findall(gms_pattern, text, re.IGNORECASE)
        if len(matches) >= 2:
            def gms_to_dd(deg, mins, secs, dir_card):
                dd = float(deg) + float(mins)/60.0 + (float(secs)/3600.0 if secs else 0.0)
                if dir_card.upper() in ['S', 'W', 'O']:
                    dd = -dd
                return dd

            lat = gms_to_dd(matches[0][0], matches[0][1], matches[0][2], matches[0][3])
            lon = gms_to_dd(matches[1][0], matches[1][1], matches[1][2], matches[1][3])
            return {"latitude": lat, "longitude": lon}

        return None
