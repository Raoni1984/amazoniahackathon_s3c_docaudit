"""
Unit and Integration Tests for Epic 1: Schema and Image Preprocessing.
Uses Python's standard unittest and handles sys.path resolution automatically.
"""

import os
import sys

# Ensure repository root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
import numpy as np
from sc3_docaudit.core.schema import EnforcementDocument, DocumentType, Party, PartyRole, DocumentReference
from sc3_docaudit.core.image_preprocessing import DocumentPreprocessor


class TestEpic1(unittest.TestCase):

    def test_schema_valid_document(self):
        doc_data = {
            "document_type": "finding_notice",
            "number": "00318",
            "series": None,
            "year": "2026",
            "issued_date": "12/03/2026",
            "issued_time": "10:35",
            "municipality": "Altamira",
            "agency": "SEMMA",
            "parties": [
                {
                    "role": "cited_party",
                    "name": "João da Silva",
                    "document_id": "123.456.789-00",
                    "address": "Travessão da 27, km 14"
                },
                {
                    "role": "issuer",
                    "name": "Fiscal de Campo",
                    "document_id": None
                }
            ],
            "property_name": "Fazenda Nova Aliança",
            "car": "PA-1500602-000000000000",
            "area_ha": "14,5 ha",
            "coordinates": ["2°58'36,2\"S 52°14'12,8\"W", "2°58'40,1\"S 52°14'15,0\"W"],
            "legal_basis": ["Art. 50 do Decreto Federal 6.514/2008"],
            "fine_brl": "R$ 72.500,00",
            "references": [
                {
                    "document_type": "complaint_record",
                    "number": "05",
                    "year": "2026"
                }
            ],
            "officer_registration": "MAT-9821",
            "signatures": {
                "issuer": "signed",
                "cited_party": "refused"
            },
            "confidence": {
                "document_type": 1.0,
                "number": 0.98,
                "area_ha": 0.95,
                "fine_brl": 0.90
            }
        }

        doc = EnforcementDocument(**doc_data)
        self.assertEqual(doc.document_type, DocumentType.FINDING_NOTICE)
        self.assertEqual(doc.number, "00318")
        self.assertEqual(doc.area_ha, 14.5)
        self.assertEqual(doc.fine_brl, 72500.0)
        self.assertEqual(len(doc.parties), 2)
        self.assertEqual(doc.signatures["cited_party"], "refused")
        self.assertEqual(doc.confidence["number"], 0.98)

    def test_image_preprocessing_pipeline(self):
        sample_img_path = os.path.abspath(
            "participant-package/challenges-1-2/altamira/documents/01-auto-de-constatacao-00318__finding-notice-00318.jpg"
        )
        if not os.path.exists(sample_img_path):
            self.skipTest("Sample image not found in participant package")

        output_preview_dir = os.path.abspath("temp/preprocessing_preview")
        os.makedirs(output_preview_dir, exist_ok=True)
        preview_output_path = os.path.join(output_preview_dir, "altamira_01_enhanced.jpg")

        enhanced_rgb, binarized, angle = DocumentPreprocessor.process_pipeline(
            sample_img_path, output_path=preview_output_path
        )
        
        self.assertIsInstance(enhanced_rgb, np.ndarray)
        self.assertIsInstance(binarized, np.ndarray)
        self.assertEqual(enhanced_rgb.shape[2], 3)
        self.assertEqual(len(binarized.shape), 2)
        self.assertTrue(enhanced_rgb.shape[0] > 100 and enhanced_rgb.shape[1] > 100)
        self.assertTrue(os.path.exists(preview_output_path))
        print(f"\n[OK] Preprocessing test passed! Angle detected: {angle:.2f} deg. Enhanced image saved to: {preview_output_path}")


if __name__ == "__main__":
    unittest.main()
