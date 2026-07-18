#!/usr/bin/env python3
"""
prep_photo.py — Prepare a source photo for ASCII conversion.

Steps:
  1. Remove background with rembg
  2. Boost local contrast with CLAHE (OpenCV)
  3. Composite onto pure white background
  4. Output grayscale source-prepped.png

Usage:
  python scripts/prep_photo.py source-photo.jpg
"""

import sys
import numpy as np
import cv2
from rembg import remove
from PIL import Image
from io import BytesIO
from pathlib import Path


def remove_background(input_path: str) -> np.ndarray:
    """Remove background using rembg."""
    print("[1/3] Removing background...")
    with open(input_path, "rb") as f:
        input_data = f.read()
    output_data = remove(input_data)
    img = Image.open(BytesIO(output_data)).convert("RGBA")
    return np.array(img)


def apply_clahe(img_array: np.ndarray) -> np.ndarray:
    """Apply CLAHE for local contrast enhancement."""
    print("[2/3] Applying CLAHE contrast boost...")
    # Convert to grayscale for CLAHE
    if len(img_array.shape) == 3 and img_array.shape[2] == 4:
        # Has alpha channel — use it as mask
        alpha = img_array[:, :, 3]
        bgr = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2BGR)
    else:
        alpha = None
        bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR) if len(img_array.shape) == 3 else img_array

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    return enhanced, alpha


def composite_on_white(gray: np.ndarray, alpha: np.ndarray = None) -> np.ndarray:
    """Composite grayscale image onto white background using alpha mask."""
    print("[3/3] Compositing on white background...")
    h, w = gray.shape
    white = np.full((h, w), 255, dtype=np.uint8)

    if alpha is not None:
        # Normalize alpha to 0-1
        mask = alpha.astype(np.float32) / 255.0
        # Blend: where alpha is 1, use gray; where alpha is 0, use white
        result = (gray.astype(np.float32) * mask + white.astype(np.float32) * (1 - mask)).astype(np.uint8)
    else:
        result = gray

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo>")
        print("Example: python scripts/prep_photo.py hardik.jpg")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = Path("data/source-prepped.png")

    if not Path(input_path).exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    # Step 1: Remove background
    img_array = remove_background(input_path)

    # Step 2: Apply CLAHE
    gray, alpha = apply_clahe(img_array)

    # Step 3: Composite on white
    result = composite_on_white(gray, alpha)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), result)
    print(f"Done! Output: {output_path}")
    print(f"Size: {result.shape[1]}x{result.shape[0]}px")


if __name__ == "__main__":
    main()
