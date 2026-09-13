"""
Unit and Integration Tests for Epic 2: Zero-Shot Layout-Agnostic Extractor Engine
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from sc3_docaudit.core.schema import EnforcementDocument, DocumentType
from sc3_docaudit.core.extractor_engine import ExtractorEngine, SemanticLayoutParser


class TestEpic2(unittest.TestCase):

    def setUp(self):
        self.engine = ExtractorEngine(use_gpu=False)

    def test_semantic_parser_classification(self):
        sample_text = "PREFEITURA MUNICIPAL DE ALTAMIRA\nSECRETARIA DE MEIO AMBIENTE - SEMMA\nAUTO DE CONSTATAÇÃO Nº 00318/2026"
        doc_type, conf = SemanticLayoutParser.classify_document_type(sample_text)
        self.assertEqual(doc_type, DocumentType.FINDING_NOTICE)
        self.assertTrue(conf >= 0.90)

    def test_semantic_parser_number_and_date(self):
        sample_text = "AUTO DE INFRAÇÃO Nº 00831/2026\nData: 17/03/2026 às 14:30"
        num, series, yr, conf_num = SemanticLayoutParser.extract_document_number_and_year(sample_text)
        date_str, time_str, conf_dt = SemanticLayoutParser.extract_dates_and_times(sample_text)

        self.assertEqual(num, "00831")
        self.assertEqual(yr, "2026")
        self.assertEqual(date_str, "17/03/2026")
        self.assertEqual(time_str, "14:30")

    def test_full_extraction_from_image(self):
        sample_img = os.path.join(
            PROJECT_ROOT,
            "participant-package",
            "challenges-1-2",
            "altamira",
            "documents",
            "01-auto-de-constatacao-00318__finding-notice-00318.jpg"
        )
        if not os.path.exists(sample_img):
            self.skipTest("Sample image not found in participant package")

        doc = self.engine.extract_from_image(sample_img)
        self.assertIsInstance(doc, EnforcementDocument)
        self.assertEqual(doc.document_type, DocumentType.FINDING_NOTICE)
        self.assertEqual(doc.number, "00318")
        self.assertEqual(doc.municipality, "Altamira")
        self.assertEqual(doc.agency, "SEMMA")
        self.assertIn("document_type", doc.confidence)
        self.assertIn("number", doc.confidence)
        print(f"\n[OK] Extracted document successfully: {doc.document_type.value} #{doc.number} ({doc.municipality})")


if __name__ == "__main__":
    unittest.main()
