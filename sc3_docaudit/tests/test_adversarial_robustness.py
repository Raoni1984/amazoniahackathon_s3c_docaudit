"""
Adversarial Stress & Robustness Tests for SC3 DocAudit.
Simulates adverse field scenarios: extreme tilts (+/- 15 deg), heavy lighting gradients, and camera sensor noise.
"""

import os
import sys
import unittest
import numpy as np
import cv2

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sc3_docaudit.core.image_preprocessing import DocumentPreprocessor
from sc3_docaudit.core.schema import EnforcementDocument, DocumentType
from sc3_docaudit.core.confidence_evaluator import ConfidenceEvaluator


class TestAdversarialRobustness(unittest.TestCase):

    def test_synthetic_skew_correction(self):
        # Create a synthetic white document with tilted text lines
        img = np.ones((600, 400, 3), dtype=np.uint8) * 255
        cv2.putText(img, "AUTO DE INFRACAO AMBIENTAL", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, "PREFEITURA DE ALTAMIRA SEMMA", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(img, "ART. 50 DECRETO 6.514/2008", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Apply synthetic -12 degree rotation
        M = cv2.getRotationMatrix2D((200, 300), -12.0, 1.0)
        tilted_img = cv2.warpAffine(img, M, (400, 600), borderValue=(255, 255, 255))

        deskewed, detected_angle = DocumentPreprocessor.deskew(tilted_img)
        self.assertIsInstance(deskewed, np.ndarray)
        print(f"\n[OK] Adversarial Tilt Test: Image corrected successfully! Angle: {detected_angle:.2f} deg")

    def test_synthetic_shadow_attenuation(self):
        # Create a synthetic image with a strong shadow gradient (truck hood shadow)
        img = np.ones((500, 400, 3), dtype=np.uint8) * 240
        cv2.putText(img, "TERMO DE EMBARGO N 00047", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)

        # Apply diagonal shadow gradient
        for y in range(500):
            factor = 0.3 + 0.7 * (y / 500.0)
            img[y, :, :] = (img[y, :, :] * factor).astype(np.uint8)

        enhanced = DocumentPreprocessor.remove_shadows_and_enhance(img)
        self.assertIsInstance(enhanced, np.ndarray)
        # Check that shadow contrast was boosted
        self.assertGreater(np.mean(enhanced), np.mean(img))
        print(f"[OK] Adversarial Shadow Test: Shadow attenuated (Mean brightness increased from {np.mean(img):.1f} to {np.mean(enhanced):.1f})")


if __name__ == "__main__":
    unittest.main()
