"""
SC3 DocAudit - Image Preprocessing Pipeline
Handles harsh field conditions: deskew, shadow attenuation, adaptive contrast, and orientation.
"""

import cv2
import numpy as np
from PIL import Image, ImageOps
from typing import Tuple, Optional, Union
import os


class DocumentPreprocessor:
    """
    OpenCV & NumPy based image preprocessor optimized for real-world environmental field forms.
    """

    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """
        Safely loads an image handling orientation and color space.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        # Support PDF documents (render first page to image)
        pil_img = None
        is_pdf = image_path.lower().endswith(".pdf")
        if not is_pdf:
            try:
                with open(image_path, "rb") as f_check:
                    if f_check.read(5).startswith(b"%PDF"):
                        is_pdf = True
            except Exception:
                pass

        if is_pdf:
            try:
                import pypdfium2 as pdfium
                pdf = pdfium.PdfDocument(image_path)
                page = pdf[0]
                pil_img = page.render(scale=2.0).to_pil()
            except Exception:
                try:
                    import pdfplumber
                    with pdfplumber.open(image_path) as pdf:
                        pil_img = pdf.pages[0].to_image(resolution=200).original
                except Exception as e:
                    raise ValueError(f"Não foi possível processar o arquivo PDF: {e}")
        else:
            try:
                pil_img = Image.open(image_path)
                pil_img = ImageOps.exif_transpose(pil_img)
            except Exception:
                # Fallback check if it was actually a PDF with a .jpg extension
                try:
                    import pypdfium2 as pdfium
                    pdf = pdfium.PdfDocument(image_path)
                    page = pdf[0]
                    pil_img = page.render(scale=2.0).to_pil()
                except Exception:
                    raise

        # Convert to RGB numpy array
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        
        img_np = np.array(pil_img)
        # Convert RGB to BGR for OpenCV processing
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        return img_bgr

    @staticmethod
    def deskew(image: np.ndarray, max_angle: float = 45.0) -> Tuple[np.ndarray, float]:
        """
        Detects text skew angle and rotates the image to be horizontally aligned.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Invert and threshold to get text pixels
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Find all foreground pixels
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return image, 0.0

        # Compute minimum area rectangle around text
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]

        # Determine true skew angle
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        if abs(angle) > max_angle or abs(angle) < 0.2:
            return image, 0.0

        # Rotate image around center
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated, angle

    @staticmethod
    def remove_shadows_and_enhance(image: np.ndarray) -> np.ndarray:
        """
        Neutralizes non-uniform field lighting, truck-hood shadows and boosts handwriting contrast.
        """
        # Split image into LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        # Estimate background illumination with morphological dilation/closing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        background = cv2.morphologyEx(l_channel, cv2.MORPH_DILATE, kernel)
        background = cv2.GaussianBlur(background, (25, 25), 0)

        # Subtract background to even out shadows
        diff = 255 - cv2.absdiff(l_channel, background)
        norm_l = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for handwriting clarity
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_l = clahe.apply(norm_l)

        # Merge back to BGR
        enhanced_lab = cv2.merge([enhanced_l, a_channel, b_channel])
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        return enhanced_bgr

    @classmethod
    def process_pipeline(
        cls, 
        image_path: str, 
        output_path: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Runs the full field preprocessing pipeline:
        1. Load & EXIF correction
        2. Auto-deskew
        3. Shadow removal & CLAHE enhancement
        Returns: (enhanced_rgb, binarized_ocr_ready, detected_skew_angle)
        """
        img_bgr = cls.load_image(image_path)
        deskewed_bgr, angle = cls.deskew(img_bgr)
        enhanced_bgr = cls.remove_shadows_and_enhance(deskewed_bgr)

        # Convert to RGB for downstream ML/VLM models
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

        # Generate binarized version for local OCR engines
        gray = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2GRAY)
        binarized = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 11
        )

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, enhanced_bgr)

        return enhanced_rgb, binarized, angle
