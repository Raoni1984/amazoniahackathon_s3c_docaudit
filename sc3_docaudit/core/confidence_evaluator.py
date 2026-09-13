"""
SC3 DocAudit - Confidence & Uncertainty Evaluator
Strict uncertainty calibration, anti-hallucination thresholds and syntactic validation (CPF, CAR, Coordinates, Fines).
Implements schema.md rule: "A field you could not read is null with low confidence, never a plausible guess."
"""

import re
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime

from sc3_docaudit.core.schema import EnforcementDocument, Party, PartyRole


class ConfidenceEvaluator:
    """
    Formal Uncertainty Calibrator and Anti-Hallucination Engine.
    Combines OCR raw likelihood with domain syntax verification (CPF/CNPJ, SICAR, Geodesics).
    """

    CONFIDENCE_THRESHOLD_NULLIFY = 0.35  # Below this, values are nullified to prevent hallucinations

    @staticmethod
    def validate_cpf(cpf_str: Optional[str]) -> Tuple[bool, float]:
        """
        Validates Brazilian CPF checksum digits.
        """
        if not cpf_str:
            return False, 0.0

        digits = [int(c) for c in re.sub(r'\D', '', cpf_str)]
        if len(digits) != 11:
            return False, 0.20

        # Check for known invalid sequences
        if len(set(digits)) == 1:
            return False, 0.10

        # Validate 1st check digit
        s1 = sum(digits[i] * (10 - i) for i in range(9))
        d1 = 11 - (s1 % 11)
        d1 = 0 if d1 >= 10 else d1
        if digits[9] != d1:
            return False, 0.30

        # Validate 2nd check digit
        s2 = sum(digits[i] * (11 - i) for i in range(10))
        d2 = 11 - (s2 % 11)
        d2 = 0 if d2 >= 10 else d2
        if digits[10] != d2:
            return False, 0.30

        return True, 0.98

    @staticmethod
    def validate_car(car_str: Optional[str]) -> Tuple[bool, float]:
        """
        Validates SICAR format: UF-IBGE(7)-HASH(12-32) (e.g. PA-1500602-A4F1C93B77E24E2FB3D6A05C8E4419D7).
        """
        if not car_str:
            return False, 0.0

        pattern = r'^[A-Z]{2}-[0-9]{7}-[A-Fa-f0-9]{12,32}$'
        if re.match(pattern, car_str.strip()):
            return True, 0.98
        elif re.match(r'^[A-Z]{2}-[0-9]{7}', car_str.strip()):
            return False, 0.60
        return False, 0.20

    @staticmethod
    def validate_coordinates(coords: List[str]) -> Tuple[bool, float]:
        """
        Validates geographical coordinates format and bounded sanity in Amazon basin.
        """
        if not coords:
            return False, 0.0

        valid_count = 0
        for coord in coords:
            # Check DMS pattern: Deg°Min'Sec"S Deg°Min'Sec"W
            if re.search(r'[0-9]{1,2}°[0-9]{1,2}\'[0-9]{1,2}.*[SNsn]\s+[0-9]{1,3}°[0-9]{1,2}\'[0-9]{1,2}.*[WwOo]', coord):
                valid_count += 1
            # Check Decimal pattern: -3.1815, -52.2304
            elif re.search(r'-\s*[0-1]?[0-9]\.[0-9]+.*-\s*[4-7][0-9]\.[0-9]+', coord):
                valid_count += 1

        if valid_count == len(coords) and len(coords) >= 1:
            return True, 0.95
        elif valid_count > 0:
            return True, 0.70
        return False, 0.30

    @staticmethod
    def validate_fine_and_area(area_ha: Optional[float], fine_brl: Optional[float]) -> Tuple[bool, float]:
        """
        Validates fine consistency under Brazilian Decree 6.514/2008 Art. 50 (R$ 5.000,00 per hectare).
        """
        if area_ha is None:
            return False, 0.50

        if fine_brl is not None and area_ha > 0:
            expected_fine = area_ha * 5000.0
            # Check if fine matches standard rate within 10% tolerance (or fixed legal bounds)
            if abs(fine_brl - expected_fine) / expected_fine < 0.15:
                return True, 0.98
            else:
                return True, 0.75  # Specific fine adjusted by aggravating/mitigating factors
        return True, 0.85

    @classmethod
    def calibrate_document(cls, doc: EnforcementDocument) -> EnforcementDocument:
        """
        Runs comprehensive uncertainty calibration over all fields in the EnforcementDocument.
        Applies anti-hallucination nullification for unreliable fields.
        """
        calibrated_conf = dict(doc.confidence)

        # 1. Calibrate CAR
        is_car_valid, car_conf = cls.validate_car(doc.car)
        if doc.car:
            calibrated_conf["car"] = car_conf
            if car_conf < cls.CONFIDENCE_THRESHOLD_NULLIFY:
                doc.car = None

        # 2. Calibrate Coordinates
        is_coords_valid, coords_conf = cls.validate_coordinates(doc.coordinates)
        if doc.coordinates:
            calibrated_conf["coordinates"] = coords_conf
            if coords_conf < cls.CONFIDENCE_THRESHOLD_NULLIFY:
                doc.coordinates = []

        # 3. Calibrate Parties (CPF validation)
        for party in doc.parties:
            if party.document_id:
                is_cpf_valid, cpf_conf = cls.validate_cpf(party.document_id)
                calibrated_conf["parties"] = min(calibrated_conf.get("parties", 0.8), cpf_conf)
                if not is_cpf_valid and cpf_conf < cls.CONFIDENCE_THRESHOLD_NULLIFY:
                    party.document_id = None  # Do not invent plausible CPFs

        # 4. Calibrate Area & Fine
        is_fine_valid, fine_conf = cls.validate_fine_and_area(doc.area_ha, doc.fine_brl)
        if doc.fine_brl:
            calibrated_conf["fine_brl"] = min(calibrated_conf.get("fine_brl", 0.85), fine_conf)

        # 5. Document Number Calibration
        if doc.number and not re.match(r'^[0-9]{2,7}$', str(doc.number)):
            calibrated_conf["number"] = 0.40

        # Update final calibrated confidence dictionary
        doc.confidence = calibrated_conf
        return doc
