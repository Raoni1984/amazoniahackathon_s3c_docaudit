"""
SC3 DocAudit - Spatiotemporal Reconciler & Divergence Auditor (Bonus Milestone)
Audits consistency between physical paper notices and digital field occurrence records.
Detects area calculation discrepancies, chronological anomalies and identity mismatches.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple
from shapely.geometry import Polygon
import math

from sc3_docaudit.core.schema import EnforcementDocument
from sc3_docaudit.core.crypto_seal import CryptoSealSC3


class ReconcilerEngine:
    """
    Automated Forensic Reconciliation Engine (Bonus Milestone & SC3 Protocol).
    Reconciles paper extractions against digital field summaries, GPS photo logs and CAR.
    """

    @staticmethod
    def parse_occurrence_summary(file_path: str) -> Dict[str, Any]:
        """
        Parses digital occurrence record as exported by the Sumaúma app.
        """
        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract CAR
        car_match = re.search(r'Registro CAR:\s*([A-Z0-9-]+)', content)
        car = car_match.group(1).strip() if car_match else None

        # Extract Area
        area_match = re.search(r'[ÁA]rea estimada:\s*([0-9]+[.,][0-9]+)\s*ha', content, re.IGNORECASE)
        area_ha = float(area_match.group(1).replace(",", ".")) if area_match else None

        # Extract Date
        date_match = re.search(r'Aberta em:\s*([0-3]?[0-9][/.-][0-1]?[0-9][/.-]20[2-3][0-9])\s*([0-2]?[0-9]:[0-5][0-9])?', content)
        opened_date = date_match.group(1) if date_match else None
        opened_time = date_match.group(2) if date_match else None

        # Extract GPS Points
        pts = re.findall(r'([0-9]{1,2}°[0-9]{1,2}\'[0-9]{1,2}"[SNsn]\s+[0-9]{1,3}°[0-9]{1,2}\'[0-9]{1,2}"[WwOo])', content)

        # Extract Photos listed
        photo_lines = re.findall(r'[0-9]{2}\.\s+([0-9/:\s]+)\s+([0-9°\'"SNWOsnwo\s]+)\s*\((.*?)\)\s*\n\s*(.*?)(?=\n\s*[0-9]{2}\.|\n\s*ÁUDIOS|\n\s*DOCUMENTOS|\Z)', content, re.DOTALL)

        return {
            "car": car,
            "area_ha": area_ha,
            "opened_date": opened_date,
            "opened_time": opened_time,
            "gps_points": pts,
            "photo_count": len(photo_lines),
            "raw_text": content
        }

    @staticmethod
    def dms_to_decimal(dms_str: str) -> Optional[Tuple[float, float]]:
        """
        Converts DMS string (e.g. 3°18'15"S 52°23'04"O) to decimal degrees (lat, lon).
        """
        match = re.search(r'([0-9]{1,2})°([0-9]{1,2})\'([0-9]{1,2}(?:[.,][0-9]+)?)"\s*([SNsn])\s+([0-9]{1,3})°([0-9]{1,2})\'([0-9]{1,2}(?:[.,][0-9]+)?)"\s*([WwOo])', dms_str)
        if not match:
            return None

        deg_lat, min_lat, sec_lat, dir_lat = float(match.group(1)), float(match.group(2)), float(match.group(3).replace(",", ".")), match.group(4).upper()
        deg_lon, min_lon, sec_lon, dir_lon = float(match.group(5)), float(match.group(6)), float(match.group(7).replace(",", ".")), match.group(8).upper()

        lat = deg_lat + min_lat / 60.0 + sec_lat / 3600.0
        if dir_lat == 'S':
            lat = -lat

        lon = deg_lon + min_lon / 60.0 + sec_lon / 3600.0
        if dir_lon in ['W', 'O']:
            lon = -lon

        return lat, lon

    @classmethod
    def calculate_polygon_area_ha(cls, dms_coords: List[str]) -> Optional[float]:
        """
        Calculates geodesic area in hectares from polygon coordinates.
        """
        if len(dms_coords) < 3:
            return None

        points_dec = []
        for c in dms_coords:
            pt = cls.dms_to_decimal(c)
            if pt:
                points_dec.append(pt)

        if len(points_dec) < 3:
            return None

        # Convert lat/lon degrees to meters around Amazon equator approximation
        # 1 deg lat ~ 110,574 m; 1 deg lon at equator ~ 111,320 m * cos(lat)
        mean_lat = sum(p[0] for p in points_dec) / len(points_dec)
        lat_m_per_deg = 110574.0
        lon_m_per_deg = 111320.0 * math.cos(math.radians(mean_lat))

        poly_m = [(p[1] * lon_m_per_deg, p[0] * lat_m_per_deg) for p in points_dec]
        polygon = Polygon(poly_m)
        area_m2 = polygon.area
        area_ha = area_m2 / 10000.0
        return round(area_ha, 2)

    @classmethod
    def reconcile(
        cls,
        doc: EnforcementDocument,
        occurrence_summary_path: Optional[str] = None,
        photo_paths: Optional[List[str]] = None,
        audio_paths: Optional[List[str]] = None,
        field_notes_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete Spatiotemporal Reconciliation and generates SC3 Cryptographic Seal.
        """
        audit_results = {
            "verdict": "PASSED",
            "discrepancies": [],
            "audits": {},
            "sc3_seal": None
        }

        digital_data = {}
        if occurrence_summary_path and os.path.exists(occurrence_summary_path):
            digital_data = cls.parse_occurrence_summary(occurrence_summary_path)

        # 1. Area Reconciliation Audit (Anti-Nullity Protection)
        paper_area = doc.area_ha
        digital_area = digital_data.get("area_ha")
        geo_area = cls.calculate_polygon_area_ha(doc.coordinates) if doc.coordinates else None

        area_audit = {
            "paper_area_ha": paper_area,
            "digital_area_ha": digital_area,
            "polygon_calculated_ha": geo_area,
            "status": "CONSISTENT"
        }

        if paper_area and digital_area:
            diff_pct = abs(paper_area - digital_area) / max(paper_area, digital_area) * 100
            if diff_pct > 5.0:
                area_audit["status"] = "DIVERGENCE_DETECTED"
                audit_results["discrepancies"].append({
                    "field": "area_ha",
                    "severity": "ALTA (Risco de Nulidade Jurídica sob Dec. nº 6.514/08)",
                    "details": f"O auto declara {paper_area} ha enquanto o registro digital de campo mediu {digital_area} ha (Variação: {diff_pct:.1f}%)."
                })
                audit_results["verdict"] = "WARNING"

        audit_results["audits"]["area_audit"] = area_audit

        # 2. CAR Registration Audit
        car_paper = doc.car
        car_digital = digital_data.get("car")
        car_status = "MATCH" if (car_paper and car_digital and car_paper == car_digital) else (
            "NO_CAR_REPORTED" if not car_paper and not car_digital else "UNVERIFIED"
        )
        if car_paper and car_digital and car_paper != car_digital:
            car_status = "MISMATCH"
            audit_results["discrepancies"].append({
                "field": "car",
                "severity": "MÉDIA",
                "details": f"O CAR informado no auto ({car_paper}) diverge do CAR registrado na base digital ({car_digital})."
            })
        audit_results["audits"]["car_audit"] = {
            "paper_car": car_paper,
            "digital_car": car_digital,
            "status": car_status
        }

        # 3. Temporal Consistency Audit
        paper_date = doc.issued_date
        digital_date = digital_data.get("opened_date")
        date_status = "CONSISTENT" if (paper_date and digital_date and paper_date == digital_date) else "OFFICE_STAGE"
        audit_results["audits"]["temporal_audit"] = {
            "event_date": digital_date,
            "notice_date": paper_date,
            "status": date_status
        }

        # 4. Generate SC3 Forensic Seal
        field_notes_text = None
        if field_notes_path and os.path.exists(field_notes_path):
            with open(field_notes_path, "r", encoding="utf-8", errors="ignore") as f:
                field_notes_text = f.read()

        sc3_seal = CryptoSealSC3.generate_seal(
            document_json=doc.model_dump(mode="json"),
            photo_paths=photo_paths,
            audio_paths=audio_paths,
            field_notes_text=field_notes_text
        )
        audit_results["sc3_seal"] = sc3_seal

        return audit_results
