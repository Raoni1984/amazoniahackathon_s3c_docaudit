"""
Batch test of image preprocessing across all 4 pilot municipalities (20 documents).
Generates enhanced previews to verify deskew and shadow removal quality.
"""

import os
import sys
import glob

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sc3_docaudit.core.image_preprocessing import DocumentPreprocessor


def run_batch_preprocessing():
    base_dir = os.path.join(PROJECT_ROOT, "participant-package", "challenges-1-2")
    output_dir = os.path.join(PROJECT_ROOT, "temp", "batch_preprocessing_preview")
    os.makedirs(output_dir, exist_ok=True)

    municipalities = ["altamira", "paragominas", "tailandia", "ulianopolis"]
    processed_count = 0

    print("=" * 70)
    print("[SC3 DocAudit] - Batch Image Preprocessing Test (20 Documents)")
    print("=" * 70)

    for muni in municipalities:
        muni_docs_path = os.path.join(base_dir, muni, "documents", "*.jpg")
        image_files = glob.glob(muni_docs_path)

        print(f"\n[+] Processing {muni.upper()} ({len(image_files)} documents):")

        for img_path in image_files:
            file_name = os.path.basename(img_path)
            out_path = os.path.join(output_dir, f"{muni}_{file_name}")

            enhanced_rgb, binarized, angle = DocumentPreprocessor.process_pipeline(
                img_path, output_path=out_path
            )
            processed_count += 1
            h, w = enhanced_rgb.shape[:2]
            print(f"  OK: {file_name[:45]:<45} | Size: {w}x{h} | Skew Angle: {angle:+.2f} deg")

    print("\n" + "=" * 70)
    print(f"[SUCCESS] Successfully processed {processed_count} document images!")
    print(f"[OUTPUT] Enhanced previews saved in: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    run_batch_preprocessing()
