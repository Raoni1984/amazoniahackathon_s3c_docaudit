"""
SC3 DocAudit - Persistent Forensic SQLite Database Module (1:N Hierarchy).
Manages long-term local storage of Environmental Enforcement Occurrences (Macro Operations)
and their child documents (Notices, Infractions, Embargos, Seizures), multimodal evidence and Merkle proofs.
"""

import os
import json
import sqlite3
import datetime
import hashlib
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "occurrences.db")

DOC_TYPE_LABELS = {
    "finding_notice": "Auto de Constatação",
    "infraction_notice": "Auto de Infração",
    "embargo_notice": "Termo de Embargo e Interdição",
    "seizure_notice": "Termo de Apreensão e Depósito",
    "notification": "Notificação Ambiental",
    "inspection_order": "Ordem de Fiscalização",
    "complaint_record": "Registro de Denúncia",
    "inspection_report": "Relatório de Fiscalização",
    "case_file_cover": "Capa do Processo",
    "deforestation_validation": "Validação de Desmatamento"
}


class OccurrenceDatabase:
    """SQLite Database manager for SC3 Environmental Occurrences and Documents."""

    @staticmethod
    def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
        conn = sqlite3.connect(db_path, timeout=60.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=60000;")
        except Exception:
            pass
        return conn

    @classmethod
    def init_db(cls, db_path: str = DB_PATH):
        """Creates the occurrences and documents tables if they do not exist."""
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Occurrence Table (Parent: 1 Enforcement Case)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS occurrences (
                id TEXT PRIMARY KEY,
                title TEXT,
                municipality TEXT,
                officer_name TEXT,
                issued_date TEXT,
                summary_text TEXT,
                field_notes TEXT,
                photos_count INTEGER DEFAULT 0,
                audios_count INTEGER DEFAULT 0,
                documents_count INTEGER DEFAULT 0,
                merkle_root_hash TEXT,
                discrepancies_count INTEGER DEFAULT 0,
                discrepancies_json TEXT,
                audit_status TEXT DEFAULT 'CONCILIADO',
                created_at TEXT,
                removed_at TEXT DEFAULT NULL
            )
            """)

            # Migration: Ensure removed_at column exists in legacy databases
            try:
                cursor.execute("ALTER TABLE occurrences ADD COLUMN removed_at TEXT DEFAULT NULL")
            except Exception:
                pass

            # 2. Occurrence Documents Table (Child: N Paper Docs per Case)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS occurrence_documents (
                id TEXT PRIMARY KEY,
                occurrence_id TEXT,
                document_number TEXT,
                document_type TEXT,
                document_type_label TEXT,
                issued_date TEXT,
                municipality TEXT,
                agency TEXT,
                car TEXT,
                area_ha REAL,
                fine_brl REAL,
                officer_registration TEXT,
                cited_parties_json TEXT,
                image_path TEXT,
                full_extracted_json TEXT,
                discrepancies_json TEXT,
                sha256_hash TEXT,
                created_at TEXT,
                FOREIGN KEY (occurrence_id) REFERENCES occurrences(id) ON DELETE CASCADE
            )
            """)
            conn.commit()

    @classmethod
    def save_occurrence(cls, occ_data: Dict[str, Any], db_path: str = DB_PATH) -> str:
        """Inserts or updates an occurrence record."""
        cls.init_db(db_path)
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            occ_id = occ_data.get("id") or f"OC-2026-AMZ-{datetime.datetime.now().strftime('%H%M%S')}"
            
            cursor.execute("""
            INSERT INTO occurrences (
                id, title, municipality, officer_name, issued_date,
                summary_text, field_notes, photos_count, audios_count,
                documents_count, merkle_root_hash, discrepancies_count,
                discrepancies_json, audit_status, created_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                municipality=excluded.municipality,
                officer_name=excluded.officer_name,
                issued_date=excluded.issued_date,
                summary_text=excluded.summary_text,
                field_notes=excluded.field_notes,
                photos_count=excluded.photos_count,
                audios_count=excluded.audios_count,
                documents_count=excluded.documents_count,
                merkle_root_hash=excluded.merkle_root_hash,
                discrepancies_count=excluded.discrepancies_count,
                discrepancies_json=excluded.discrepancies_json,
                audit_status=excluded.audit_status,
                created_at=excluded.created_at
            """, (
                occ_id,
                occ_data.get("title") or f"Ocorrência em {occ_data.get('municipality', 'Amazônia')}",
                occ_data.get("municipality") or "Amazônia",
                occ_data.get("officer_name") or "Agente Fiscal",
                occ_data.get("issued_date") or datetime.date.today().isoformat(),
                occ_data.get("summary_text") or "",
                occ_data.get("field_notes") or "",
                int(occ_data.get("photos_count") or 0),
                int(occ_data.get("audios_count") or 0),
                int(occ_data.get("documents_count") or 0),
                occ_data.get("merkle_root_hash") or "",
                int(occ_data.get("discrepancies_count") or 0),
                json.dumps(occ_data.get("discrepancies", []), ensure_ascii=False),
                occ_data.get("audit_status") or "CONCILIADO",
                occ_data.get("created_at") or datetime.datetime.now().isoformat()
            ))
            conn.commit()
            return occ_id

    @classmethod
    def save_document(cls, doc_data: Dict[str, Any], db_path: str = DB_PATH) -> str:
        """Inserts or updates a document attached to an occurrence."""
        cls.init_db(db_path)
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            doc_id = doc_data.get("id") or f"DOC-{doc_data.get('occurrence_id', 'AMZ')}-{datetime.datetime.now().strftime('%f')[:6]}"
            
            raw_type = doc_data.get("document_type") or "unknown"
            label = doc_data.get("document_type_label") or DOC_TYPE_LABELS.get(raw_type, "Documento de Fiscalização")

            cursor.execute("""
            INSERT INTO occurrence_documents (
                id, occurrence_id, document_number, document_type, document_type_label,
                issued_date, municipality, agency, car, area_ha, fine_brl,
                officer_registration, cited_parties_json, image_path,
                full_extracted_json, discrepancies_json, sha256_hash, created_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT(id) DO UPDATE SET
                occurrence_id=excluded.occurrence_id,
                document_number=excluded.document_number,
                document_type=excluded.document_type,
                document_type_label=excluded.document_type_label,
                issued_date=excluded.issued_date,
                municipality=excluded.municipality,
                agency=excluded.agency,
                car=excluded.car,
                area_ha=excluded.area_ha,
                fine_brl=excluded.fine_brl,
                officer_registration=excluded.officer_registration,
                cited_parties_json=excluded.cited_parties_json,
                image_path=excluded.image_path,
                full_extracted_json=excluded.full_extracted_json,
                discrepancies_json=excluded.discrepancies_json,
                sha256_hash=excluded.sha256_hash,
                created_at=excluded.created_at
            """, (
                doc_id,
                doc_data.get("occurrence_id"),
                doc_data.get("document_number") or "S/N",
                raw_type,
                label,
                doc_data.get("issued_date") or "",
                doc_data.get("municipality") or "",
                doc_data.get("agency") or "SEMAS",
                doc_data.get("car") or "",
                float(doc_data.get("area_ha") or 0.0) if doc_data.get("area_ha") is not None else None,
                float(doc_data.get("fine_brl") or 0.0) if doc_data.get("fine_brl") is not None else None,
                doc_data.get("officer_registration") or "",
                json.dumps(doc_data.get("cited_parties", []), ensure_ascii=False),
                doc_data.get("image_path") or "",
                json.dumps(doc_data.get("full_extracted_json", {}), ensure_ascii=False),
                json.dumps(doc_data.get("discrepancies", []), ensure_ascii=False),
                doc_data.get("sha256_hash") or "",
                doc_data.get("created_at") or datetime.datetime.now().isoformat()
            ))
            conn.commit()

            # Update parent occurrence counters
            cls._refresh_occurrence_aggregates(doc_data.get("occurrence_id"), db_path)
            return doc_id

    @classmethod
    def _refresh_occurrence_aggregates(cls, occ_id: str, db_path: str = DB_PATH):
        """Recalculates document count, discrepancies, and Merkle root for an occurrence."""
        if not occ_id:
            return
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM occurrence_documents WHERE occurrence_id = ?", (occ_id,))
            docs = cursor.fetchall()
            
            doc_count = len(docs)
            total_discrepancies = []
            all_hashes = []
            
            for d in docs:
                disc_list = json.loads(d["discrepancies_json"]) if d["discrepancies_json"] else []
                total_discrepancies.extend(disc_list)
                if d["sha256_hash"]:
                    all_hashes.append(d["sha256_hash"])

            audit_status = "DIVERGENTE" if len(total_discrepancies) > 0 else "CONCILIADO"
            combined_merkle = hashlib.sha256("".join(sorted(all_hashes)).encode("utf-8")).hexdigest() if all_hashes else ""

            cursor.execute("""
            UPDATE occurrences SET
                documents_count = ?,
                discrepancies_count = ?,
                discrepancies_json = ?,
                audit_status = ?,
                merkle_root_hash = CASE WHEN merkle_root_hash IS NULL OR merkle_root_hash = '' THEN ? ELSE merkle_root_hash END
            WHERE id = ?
            """, (doc_count, len(total_discrepancies), json.dumps(total_discrepancies, ensure_ascii=False), audit_status, combined_merkle, occ_id))
            conn.commit()

    @classmethod
    def soft_delete_occurrence(cls, occ_id: str, db_path: str = DB_PATH) -> bool:
        """Sets removed_at timestamp (soft delete), keeping the record in database for forensic compliance."""
        if not occ_id:
            return False
        cls.init_db(db_path)
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cursor.execute("UPDATE occurrences SET removed_at = ? WHERE id = ?", (now_str, occ_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error soft deleting occurrence {occ_id}: {e}")
            return False

    @classmethod
    def get_all_occurrences(cls, search_query: Optional[str] = None, muni_filter: Optional[str] = None, status_filter: Optional[str] = None, include_removed: bool = False, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
        """Retrieves occurrences with optional search and filters."""
        cls.init_db(db_path)
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                if include_removed:
                    cursor.execute("SELECT * FROM occurrences ORDER BY created_at DESC, id ASC")
                else:
                    cursor.execute("SELECT * FROM occurrences WHERE (removed_at IS NULL OR removed_at = '') ORDER BY created_at DESC, id ASC")
                rows = cursor.fetchall()

                results = []
                for row in rows:
                    item = dict(row)
                    disc_json = item.get("discrepancies_json")
                    try:
                        item["discrepancies"] = json.loads(disc_json) if disc_json else []
                    except Exception:
                        item["discrepancies"] = []
                    
                    muni = item.get("municipality") or ""
                    # Filters
                    if muni_filter and muni_filter != "Todos os municípios":
                        if muni.lower() != muni_filter.lower():
                            continue
                    
                    status = item.get("audit_status") or "CONCILIADO"
                    if status_filter and status_filter != "Todos os status":
                        if status_filter == "Conciliado" and status != "CONCILIADO":
                            continue
                        if status_filter == "Com divergências" and status != "DIVERGENTE":
                            continue

                    if search_query:
                        sq = search_query.strip().lower()
                        haystack = f"{item.get('id', '')} {item.get('title', '')} {muni} {item.get('officer_name', '')} {item.get('summary_text', '')}".lower()
                        if sq not in haystack:
                            continue

                    results.append(item)
                return results
        except Exception as e:
            print(f"Error fetching occurrences: {e}")
            return []

    @classmethod
    def get_occurrence_by_id(cls, occ_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
        """Retrieves a single occurrence and all its attached documents."""
        if not occ_id:
            return None
        cls.init_db(db_path)
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM occurrences WHERE id = ?", (occ_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                item = dict(row)
                disc_json = item.get("discrepancies_json")
                try:
                    item["discrepancies"] = json.loads(disc_json) if disc_json else []
                except Exception:
                    item["discrepancies"] = []
                
                # Fetch attached documents
                cursor.execute("SELECT * FROM occurrence_documents WHERE occurrence_id = ? ORDER BY document_number ASC", (occ_id,))
                doc_rows = cursor.fetchall()
                
                documents = []
                for d in doc_rows:
                    d_dict = dict(d)
                    try:
                        d_dict["cited_parties"] = json.loads(d_dict["cited_parties_json"]) if d_dict.get("cited_parties_json") else []
                    except Exception:
                        d_dict["cited_parties"] = []
                    try:
                        d_dict["discrepancies"] = json.loads(d_dict["discrepancies_json"]) if d_dict.get("discrepancies_json") else []
                    except Exception:
                        d_dict["discrepancies"] = []
                    try:
                        d_dict["full_extracted_json"] = json.loads(d_dict["full_extracted_json"]) if d_dict.get("full_extracted_json") else {}
                    except Exception:
                        d_dict["full_extracted_json"] = {}
                    documents.append(d_dict)
                    
                item["documents"] = documents
                return item
        except Exception as e:
            print(f"Error fetching occurrence {occ_id}: {e}")
            return None

    @classmethod
    def get_document_by_id(cls, doc_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
        """Retrieves a single document by ID."""
        cls.init_db(db_path)
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM occurrence_documents WHERE id = ?", (doc_id,))
            d = cursor.fetchone()
            if not d:
                return None
            d_dict = dict(d)
            d_dict["cited_parties"] = json.loads(d_dict["cited_parties_json"]) if d_dict["cited_parties_json"] else []
            d_dict["discrepancies"] = json.loads(d_dict["discrepancies_json"]) if d_dict["discrepancies_json"] else []
            d_dict["full_extracted_json"] = json.loads(d_dict["full_extracted_json"]) if d_dict["full_extracted_json"] else {}
            return d_dict

    @classmethod
    def update_document_extracted_field(cls, doc_id: str, field_name: str, new_value: Any, db_path: str = DB_PATH):
        """Updates a field inside a document and recalculates reconciliation discrepancies."""
        cls.init_db(db_path)
        doc = cls.get_document_by_id(doc_id, db_path)
        if not doc:
            return

        extracted = doc["full_extracted_json"]
        extracted[field_name] = new_value

        # Update root column if it maps directly
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Clear resolved discrepancy
            current_discrepancies = [d for d in doc["discrepancies"] if d.get("field") != field_name]
            
            col_map = {
                "number": "document_number",
                "issued_date": "issued_date",
                "area_ha": "area_ha",
                "fine_brl": "fine_brl",
                "car": "car",
                "municipality": "municipality"
            }
            if field_name in col_map:
                col = col_map[field_name]
                cursor.execute(f"UPDATE occurrence_documents SET {col} = ?, full_extracted_json = ?, discrepancies_json = ? WHERE id = ?",
                               (new_value, json.dumps(extracted, ensure_ascii=False), json.dumps(current_discrepancies, ensure_ascii=False), doc_id))
            else:
                cursor.execute("UPDATE occurrence_documents SET full_extracted_json = ?, discrepancies_json = ? WHERE id = ?",
                               (json.dumps(extracted, ensure_ascii=False), json.dumps(current_discrepancies, ensure_ascii=False), doc_id))
            conn.commit()

        cls._refresh_occurrence_aggregates(doc["occurrence_id"], db_path)

    @classmethod
    def count_occurrences(cls, db_path: str = DB_PATH) -> int:
        cls.init_db(db_path)
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM occurrences")
            return cursor.fetchone()[0]

    @classmethod
    def seed_pilot_occurrences(cls, package_dir: str, db_path: str = DB_PATH):
        """Populates the 4 pilot enforcement operations and their respective documents."""
        import glob
        from sc3_docaudit.core.extractor_engine import ExtractorEngine
        from sc3_docaudit.core.confidence_evaluator import ConfidenceEvaluator
        from sc3_docaudit.core.reconciler import ReconcilerEngine
        from sc3_docaudit.core.crypto_seal import CryptoSealSC3

        engine = ExtractorEngine(use_gpu=False)
        municipalities = [
            ("altamira", "OC-2026-ALT-01", "Operação Castanheira - Desmatamento Ilegal"),
            ("paragominas", "OC-2026-PAR-01", "Operação Uraim - Fiscalização de Madeireiras"),
            ("tailandia", "OC-2026-TAI-01", "Operação Dendê - Embargo de Área em Regeneração"),
            ("ulianopolis", "OC-2026-ULI-01", "Operação Gurupi - Extração Ilegal de Minério")
        ]

        for muni_key, occ_id, occ_title in municipalities:
            muni_dir = os.path.join(package_dir, muni_key)
            docs_dir = os.path.join(muni_dir, "documents")
            occ_summary_path = os.path.join(muni_dir, "occurrence-summary.txt")
            field_notes_path = os.path.join(muni_dir, "field-notes.md")
            photos_dir = os.path.join(muni_dir, "photos")
            audios_dir = os.path.join(muni_dir, "audios")

            p_files = sorted(glob.glob(os.path.join(photos_dir, "*.jpg"))) if os.path.exists(photos_dir) else []
            a_files = sorted(glob.glob(os.path.join(audios_dir, "*.mp3"))) if os.path.exists(audios_dir) else []

            summary_text = ""
            if os.path.exists(occ_summary_path):
                with open(occ_summary_path, "r", encoding="utf-8", errors="ignore") as f:
                    summary_text = f.read()

            notes_text = ""
            if os.path.exists(field_notes_path):
                with open(field_notes_path, "r", encoding="utf-8", errors="ignore") as f:
                    notes_text = f.read()

            # Save Parent Occurrence first
            occ_data = {
                "id": occ_id,
                "title": occ_title,
                "municipality": muni_key.capitalize(),
                "officer_name": "Equipe de Fiscalização SEMAS",
                "issued_date": "2026-09-10",
                "summary_text": summary_text,
                "field_notes": notes_text,
                "photos_count": len(p_files),
                "audios_count": len(a_files),
                "documents_count": 0,
                "audit_status": "CONCILIADO"
            }
            cls.save_occurrence(occ_data, db_path)

            # Process & Save all documents under this occurrence
            if os.path.exists(docs_dir):
                doc_images = sorted(glob.glob(os.path.join(docs_dir, "*.jpg")))
                for img_p in doc_images:
                    base_f = os.path.basename(img_p)
                    doc_extracted = engine.extract_from_image(img_p)
                    calibrated = ConfidenceEvaluator.calibrate_document(doc_extracted)
                    
                    # Reconcile against occurrence summary
                    audit = ReconcilerEngine.reconcile(calibrated, occ_summary_path, p_files, a_files, field_notes_path)
                    
                    # Compute document SHA-256
                    with open(img_p, "rb") as f:
                        img_bytes = f.read()
                    doc_sha = hashlib.sha256(img_bytes).hexdigest()

                    raw_type = calibrated.document_type.value if hasattr(calibrated.document_type, "value") else str(calibrated.document_type)
                    label = DOC_TYPE_LABELS.get(raw_type, "Documento de Fiscalização")
                    doc_short = base_f.split("__")[0].replace(".jpg", "")
                    doc_id = f"DOC-{muni_key.upper()[:3]}-{doc_short}"

                    doc_record = {
                        "id": doc_id,
                        "occurrence_id": occ_id,
                        "document_number": calibrated.number or doc_short,
                        "document_type": raw_type,
                        "document_type_label": label,
                        "issued_date": calibrated.issued_date or "2026",
                        "municipality": calibrated.municipality or muni_key.capitalize(),
                        "agency": calibrated.agency or "SEMAS",
                        "car": calibrated.car or "",
                        "area_ha": calibrated.area_ha,
                        "fine_brl": calibrated.fine_brl,
                        "officer_registration": calibrated.officer_registration or "",
                        "cited_parties": [p.model_dump(mode="json") for p in calibrated.parties],
                        "image_path": img_p,
                        "full_extracted_json": calibrated.model_dump(mode="json"),
                        "discrepancies": audit.get("discrepancies", []),
                        "sha256_hash": doc_sha
                    }
                    cls.save_document(doc_record, db_path)

            # Generate SC3 Seal over the whole occurrence
            all_occ_docs = cls.get_occurrence_by_id(occ_id, db_path).get("documents", [])
            doc_jsons = [d["full_extracted_json"] for d in all_occ_docs]
            seal = CryptoSealSC3.generate_seal(
                document_json={"occurrence_id": occ_id, "documents": doc_jsons},
                photo_paths=p_files,
                audio_paths=a_files,
                field_notes_text=notes_text
            )
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE occurrences SET merkle_root_hash = ? WHERE id = ?", (seal.get("merkle_root_hash", ""), occ_id))
                conn.commit()

    @classmethod
    def seed_if_empty(cls, package_dir: str, db_path: str = DB_PATH):
        cls.init_db(db_path)
        # Check if occurrences table is properly populated with new hierarchy
        with cls.get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='occurrence_documents'")
            table_exists = cursor.fetchone()
        
        if not table_exists or cls.count_occurrences(db_path) == 0:
            # Drop old flat schema if present and seed cleanly
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS occurrences")
                cursor.execute("DROP TABLE IF EXISTS occurrence_documents")
                conn.commit()
            cls.init_db(db_path)
            cls.seed_pilot_occurrences(package_dir, db_path)
