import pytest
from sc3_docaudit.core.gps_parser import GPSParser


def test_parse_manual_decimal():
    result = GPSParser.parse_manual("-3.75412, -48.12543")
    assert result is not None
    assert abs(result["latitude"] - (-3.75412)) < 1e-4
    assert abs(result["longitude"] - (-48.12543)) < 1e-4


def test_parse_manual_gms():
    result = GPSParser.parse_manual("03° 45' 14.4\" S, 48° 07' 31.2\" W")
    assert result is not None
    assert result["latitude"] < 0
    assert result["longitude"] < 0


def test_parse_gpx_garmin_sample():
    sample_gpx = b"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="Garmin GPSMAP 64s" xmlns="http://www.topografix.com/GPX/1/1">
      <wpt lat="-3.754120" lon="-48.125430">
        <ele>142.5</ele>
        <time>2026-09-12T15:30:00Z</time>
        <name>PONTO-DESMAT-01</name>
      </wpt>
    </gpx>"""
    wpts = GPSParser.parse_gpx(sample_gpx)
    assert len(wpts) == 1
    assert wpts[0]["name"] == "PONTO-DESMAT-01"
    assert abs(wpts[0]["latitude"] - (-3.75412)) < 1e-4
    assert wpts[0]["elevation_m"] == 142.5
