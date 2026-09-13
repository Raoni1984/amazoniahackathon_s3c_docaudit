"""
Unit and Integration Tests for Epic 3: Confidence Calibration and Cost Optimization
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
import time
from sc3_docaudit.core.schema import EnforcementDocument, DocumentType, Party, PartyRole
from sc3_docaudit.core.confidence_evaluator import ConfidenceEvaluator
from sc3_docaudit.core.cost_tracker import CostTracker


class TestEpic3(unittest.TestCase):

    def test_cpf_validation_calibration(self):
        # Valid CPF checksum
        is_valid, conf = ConfidenceEvaluator.validate_cpf("111.444.777-35")
        self.assertTrue(is_valid)
        self.assertGreaterEqual(conf, 0.95)

        # Invalid CPF checksum (tampered last digit)
        is_invalid, conf_bad = ConfidenceEvaluator.validate_cpf("111.444.777-99")
        self.assertFalse(is_invalid)
        self.assertLess(conf_bad, 0.40)

    def test_car_validation_calibration(self):
        valid_car = "PA-1500602-A4F1C93B77E24E2FB3D6A05C8E4419D7"
        is_valid, conf = ConfidenceEvaluator.validate_car(valid_car)
        self.assertTrue(is_valid)
        self.assertEqual(conf, 0.98)

        invalid_car = "CAR-INVALIDO-123"
        is_invalid, conf_bad = ConfidenceEvaluator.validate_car(invalid_car)
        self.assertFalse(is_invalid)
        self.assertLess(conf_bad, 0.40)

    def test_anti_hallucination_nullification(self):
        doc = EnforcementDocument(
            document_type=DocumentType.FINDING_NOTICE,
            number="00318",
            car="INVALIDO",  # Should be nullified
            parties=[Party(role=PartyRole.CITED_PARTY, name="Infrator", document_id="000.000.000-00")], # Invalid CPF
            coordinates=["COORD_QUEBRADA"], # Invalid coordinate
            confidence={"car": 0.20, "coordinates": 0.20, "parties": 0.20}
        )

        calibrated = ConfidenceEvaluator.calibrate_document(doc)
        self.assertIsNone(calibrated.car)
        self.assertEqual(len(calibrated.coordinates), 0)
        self.assertIsNone(calibrated.parties[0].document_id)
        print("\n[OK] Anti-hallucination successfully nullified unreliable fields!")

    def test_cost_tracker_zero_cost(self):
        t0 = time.time()
        cost_info = CostTracker.measure_execution_cost(t0, memory_before_mb=50.0)
        self.assertEqual(cost_info["external_api_cost_usd"], 0.00)
        self.assertIn("R$ 0,00", cost_info["cost_per_page_brl"])
        print(f"[OK] Cost report verified: {cost_info['cost_per_page_brl']} | Latency: {cost_info['processing_time_seconds']}s")


if __name__ == "__main__":
    unittest.main()
