"""
Unit Tests for OccurrenceDatabase 1:N Hierarchy & Append-Only Document Vault.
"""

import os
import sys
import unittest
import tempfile

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sc3_docaudit.core.database import OccurrenceDatabase


class TestDatabase1N(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
        OccurrenceDatabase.init_db(self.temp_db)

    def tearDown(self):
        if os.path.exists(self.temp_db):
            try:
                os.remove(self.temp_db)
            except Exception:
                pass

    def test_occurrence_crud_and_child_documents(self):
        # 1. Create Parent Occurrence
        occ_id = "OC-2026-TEST-01"
        occ_data = {
            "id": occ_id,
            "title": "Operação Teste Amazônia",
            "municipality": "Altamira",
            "officer_name": "Agente Silva",
            "issued_date": "2026-09-12",
            "summary_text": "Fiscalização de área desmatada.",
            "field_notes": "Área de difícil acesso.",
            "photos_count": 3,
            "audios_count": 2,
            "audit_status": "CONCILIADO"
        }
        res_id = OccurrenceDatabase.save_occurrence(occ_data, self.temp_db)
        self.assertEqual(res_id, occ_id)

        # 2. Attach Child Document 1 (Finding Notice)
        doc1_id = "DOC-TEST-001"
        doc1_data = {
            "id": doc1_id,
            "occurrence_id": occ_id,
            "document_number": "001",
            "document_type": "finding_notice",
            "document_type_label": "Auto de Constatação",
            "issued_date": "2026-09-12",
            "municipality": "Altamira",
            "area_ha": 23.5,
            "fine_brl": 0.0,
            "sha256_hash": "a1b2c3d4e5f6",
            "discrepancies": []
        }
        OccurrenceDatabase.save_document(doc1_data, self.temp_db)

        # 3. Attach Child Document 2 (Infraction Notice with discrepancy)
        doc2_id = "DOC-TEST-002"
        doc2_data = {
            "id": doc2_id,
            "occurrence_id": occ_id,
            "document_number": "002",
            "document_type": "infraction_notice",
            "document_type_label": "Auto de Infração",
            "issued_date": "2026-09-12",
            "municipality": "Altamira",
            "area_ha": 30.0,
            "fine_brl": 150000.0,
            "sha256_hash": "f6e5d4c3b2a1",
            "discrepancies": [{"field": "area_ha", "severity": "CRÍTICO", "details": "Área diverge do auto 001"}]
        }
        OccurrenceDatabase.save_document(doc2_data, self.temp_db)

        # 4. Fetch Occurrence and verify 1:N relations
        occ = OccurrenceDatabase.get_occurrence_by_id(occ_id, self.temp_db)
        self.assertIsNotNone(occ)
        self.assertEqual(occ["documents_count"], 2)
        self.assertEqual(len(occ["documents"]), 2)
        self.assertEqual(occ["discrepancies_count"], 1)
        self.assertEqual(occ["audit_status"], "DIVERGENTE")

        # 5. Resolve discrepancy on Document 2
        OccurrenceDatabase.update_document_extracted_field(doc2_id, "area_ha", 23.5, self.temp_db)
        occ_after = OccurrenceDatabase.get_occurrence_by_id(occ_id, self.temp_db)
        self.assertEqual(occ_after["discrepancies_count"], 0)
        self.assertEqual(occ_after["audit_status"], "CONCILIADO")

        # 6. Test Query and Search
        search_results = OccurrenceDatabase.get_all_occurrences(search_query="Silva", db_path=self.temp_db)
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["id"], occ_id)


if __name__ == "__main__":
    unittest.main()
