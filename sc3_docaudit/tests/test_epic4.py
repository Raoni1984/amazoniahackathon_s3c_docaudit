"""
Unit and Integration Tests for Epic 4: Spatiotemporal Reconciliation & SC3 Protocol (Bonus Milestone)
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from sc3_docaudit.core.schema import EnforcementDocument, DocumentType
from sc3_docaudit.core.reconciler import ReconcilerEngine
from sc3_docaudit.core.crypto_seal import CryptoSealSC3


class TestEpic4(unittest.TestCase):

    def test_dms_to_decimal_and_area_calculation(self):
        # 4 corners in Assurini district, Altamira
        coords = [
            '3°18\'15"S 52°23\'04"O',
            '3°17\'56"S 52°22\'58"O',
            '3°17\'55"S 52°22\'43"O',
            '3°18\'11"S 52°22\'43"O'
        ]
        area_calc = ReconcilerEngine.calculate_polygon_area_ha(coords)
        self.assertIsNotNone(area_calc)
        self.assertGreater(area_calc, 10.0)
        self.assertLess(area_calc, 50.0)
        print(f"\n[OK] Polygon Geodesic Area calculated: {area_calc} ha")

    def test_reconciliation_altamira_case(self):
        occurrence_path = os.path.join(
            PROJECT_ROOT, "participant-package", "challenges-1-2", "altamira", "occurrence-summary.txt"
        )
        if not os.path.exists(occurrence_path):
            self.skipTest("Occurrence summary not found")

        doc = EnforcementDocument(
            document_type=DocumentType.FINDING_NOTICE,
            number="00318",
            issued_date="12/03/2026",
            car="PA-1500602-A4F1C93B77E24E2FB3D6A05C8E4419D7",
            area_ha=23.4,
            coordinates=['3°18\'15"S 52°23\'04"O', '3°17\'56"S 52°22\'58"O', '3°17\'55"S 52°22\'43"O'],
            confidence={"document_type": 1.0, "number": 0.98, "area_ha": 0.95}
        )

        audit_res = ReconcilerEngine.reconcile(
            doc=doc,
            occurrence_summary_path=occurrence_path
        )

        self.assertEqual(audit_res["verdict"], "PASSED")
        self.assertEqual(audit_res["audits"]["car_audit"]["status"], "MATCH")
        self.assertEqual(audit_res["audits"]["area_audit"]["status"], "CONSISTENT")
        self.assertIsNotNone(audit_res["sc3_seal"]["merkle_root_hash"])
        print(f"[OK] SC3 Merkle Root: {audit_res['sc3_seal']['merkle_root_hash']}")
        print(f"[OK] Audit Verdict: {audit_res['verdict']}")


if __name__ == "__main__":
    unittest.main()
