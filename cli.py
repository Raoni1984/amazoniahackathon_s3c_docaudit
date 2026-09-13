"""
SC3 DocAudit - Command Line Interface (CLI)
Automated Batch Processor for Environmental Enforcement Documents.
Generates compliant schema.md JSON files and executes SC3 Spatiotemporal Reconciliation.
"""

import os
import sys
import glob
import json
import argparse
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from sc3_docaudit.core.schema import EnforcementDocument
from sc3_docaudit.core.extractor_engine import ExtractorEngine
from sc3_docaudit.core.confidence_evaluator import ConfidenceEvaluator
from sc3_docaudit.core.reconciler import ReconcilerEngine
from sc3_docaudit.core.cost_tracker import CostTracker


def process_single_image(
    image_path: str,
    output_dir: str,
    engine: ExtractorEngine,
    occurrence_path: Optional[str] = None,
    photos_dir: Optional[str] = None,
    audios_dir: Optional[str] = None,
    notes_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Processes one image through Preprocessing -> Extractor -> Confidence Calibrator -> SC3 Reconciler.
    Saves JSON with exact matching basename.
    """
    t0 = time.time()
    file_basename = os.path.basename(image_path)
    base_name_no_ext, _ = os.path.splitext(file_basename)
    out_json_path = os.path.join(output_dir, f"{base_name_no_ext}.json")

    # 1. Extraction
    doc = engine.extract_from_image(image_path)

    # 2. Uncertainty Calibration & Anti-Hallucination
    calibrated_doc = ConfidenceEvaluator.calibrate_document(doc)

    # 3. Collect field evidence files for SC3 Seal
    photo_files = glob.glob(os.path.join(photos_dir, "*.jpg")) if photos_dir and os.path.exists(photos_dir) else []
    audio_files = glob.glob(os.path.join(audios_dir, "*.mp3")) if audios_dir and os.path.exists(audios_dir) else []

    # 4. Spatiotemporal Reconciliation & SC3 Protocol
    audit_results = ReconcilerEngine.reconcile(
        doc=calibrated_doc,
        occurrence_summary_path=occurrence_path,
        photo_paths=photo_files,
        audio_paths=audio_files,
        field_notes_path=notes_path
    )

    # Attach forensic audit to document if SC3 seal was generated
    if audit_results.get("sc3_seal"):
        from sc3_docaudit.core.schema import ForensicAuditSC3
        calibrated_doc.forensic_audit = ForensicAuditSC3(
            evidence_hash=audit_results["sc3_seal"]["merkle_root_hash"],
            temporal_match=audit_results["audits"].get("temporal_audit", {}).get("status"),
            spatial_match=audit_results["audits"].get("area_audit", {}).get("status"),
            car_audit_status=audit_results["audits"].get("car_audit", {}).get("status"),
            blockchain_ready=True
        )

    # 5. Export JSON strictly compliant with schema.md
    doc_dict = calibrated_doc.model_dump(mode="json")
    os.makedirs(output_dir, exist_ok=True)
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(doc_dict, f, indent=2, ensure_ascii=False)

    cost_metrics = CostTracker.measure_execution_cost(t0, memory_before_mb=50.0)

    return {
        "file": file_basename,
        "json_path": out_json_path,
        "document_type": calibrated_doc.document_type.value if hasattr(calibrated_doc.document_type, "value") else str(calibrated_doc.document_type),
        "number": calibrated_doc.number,
        "verdict": audit_results.get("verdict", "PASSED"),
        "sc3_hash": audit_results["sc3_seal"]["merkle_root_hash"] if audit_results.get("sc3_seal") else None,
        "discrepancies_count": len(audit_results.get("discrepancies", [])),
        "latency_sec": cost_metrics["processing_time_seconds"]
    }


def main():
    parser = argparse.ArgumentParser(description="SC3 DocAudit - Environmental Enforcement CLI")
    parser.add_argument("--input", required=True, help="Input directory of document images or single image path")
    parser.add_argument("--output", required=True, help="Output directory to save schema.md JSON files")
    parser.add_argument("--occurrence", default=None, help="Path to occurrence-summary.txt for SC3 reconciliation")
    parser.add_argument("--photos", default=None, help="Path to photos directory for SC3 Merkle proof")
    parser.add_argument("--audios", default=None, help="Path to audios directory for SC3 Merkle proof")
    parser.add_argument("--notes", default=None, help="Path to field-notes.md")

    args = parser.parse_args()

    print("=" * 75)
    print("[SC3 DocAudit] - CLI Batch Extraction & Forensic Audit Engine")
    print("=" * 75)

    if os.path.isfile(args.input):
        image_files = [args.input]
    else:
        image_files = sorted(glob.glob(os.path.join(args.input, "*.jpg")) + glob.glob(os.path.join(args.input, "*.png")))

    if not image_files:
        print(f"[ERROR] No document images found in {args.input}")
        return

    engine = ExtractorEngine(use_gpu=False)
    results = []

    for img in image_files:
        print(f"\n[+] Processing: {os.path.basename(img)}...")
        res = process_single_image(
            image_path=img,
            output_dir=args.output,
            engine=engine,
            occurrence_path=args.occurrence,
            photos_dir=args.photos,
            audios_dir=args.audios,
            notes_path=args.notes
        )
        results.append(res)
        print(f"    Type: {res['document_type']} | Number: #{res['number']} | SC3: {res['sc3_hash'][:16]}... | Latency: {res['latency_sec']}s")

    print("\n" + "=" * 75)
    print(f"[SUCCESS] Successfully extracted and audited {len(results)} documents!")
    print(f"[OUTPUT] JSON outputs saved to: {os.path.abspath(args.output)}")
    print(f"[COST] Financial Cost: $0.00 / R$ 0,00 (100% On-Premise Local Inference)")
    print("=" * 75)


if __name__ == "__main__":
    from typing import Dict, Any, Optional
    main()
