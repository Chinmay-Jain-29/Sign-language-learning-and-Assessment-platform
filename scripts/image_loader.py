import os
import sys
import cv2
import numpy as np
from typing import Optional, Tuple, List

class ASLImageLoader:
    def __init__(self, target_size: Tuple[int, int] = (224, 224), normalize: bool = True):
        self.target_size = target_size
        self.normalize = normalize

    def load_image(self, file_path: str) -> Optional[np.ndarray]:
        """Loads single image, converts to RGB, resizes, and optionally normalizes pixel values [0, 1]."""
        if not os.path.exists(file_path):
            print(f"[ASLImageLoader] Error: File does not exist -> {file_path}")
            return None

        try:
            img_bgr = cv2.imread(file_path)
            if img_bgr is None:
                print(f"[ASLImageLoader] Warning: Failed to decode image -> {file_path}")
                return None

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, self.target_size, interpolation=cv2.INTER_AREA)

            if self.normalize:
                return img_resized.astype(np.float32) / 255.0

            return img_resized
        except Exception as e:
            print(f"[ASLImageLoader] Exception processing image {file_path}: {e}")
            return None

    def load_batch(self, file_paths: List[str]) -> np.ndarray:
        """Batch loads multiple images, skipping any corrupted or unreadable files."""
        batch = []
        for path in file_paths:
            img = self.load_image(path)
            if img is not None:
                batch.append(img)

        if not batch:
            return np.empty((0, *self.target_size, 3), dtype=np.float32 if self.normalize else np.uint8)

        return np.stack(batch, axis=0)

def inspect_and_load_image(image_path: str, display: bool = False) -> bool:
    """
    Low-level image validation utility:
    - Reads image directly without preprocessing or model interference
    - Verifies successful loading
    - Prints Height, Width, Channels, and File Size
    """
    if not os.path.exists(image_path):
        print(f"[Error] Image file not found: {image_path}")
        return False

    file_size_bytes = os.path.getsize(image_path)
    file_size_kb = file_size_bytes / 1024.0

    img = cv2.imread(image_path)
    if img is None:
        print(f"[Error] Failed to decode image: {image_path}")
        return False

    if len(img.shape) == 3:
        height, width, channels = img.shape
    else:
        height, width = img.shape
        channels = 1

    print("==================================================")
    print("           LOW-LEVEL IMAGE VALIDATION             ")
    print("==================================================")
    print(f"File Path   : {image_path}")
    print(f"Status      : Successfully Loaded (200 OK)")
    print(f"Height      : {height} px")
    print(f"Width       : {width} px")
    print(f"Channels    : {channels}")
    print(f"Image Size  : {file_size_bytes} bytes ({file_size_kb:.2f} KB)")
    print("==================================================")

    if display:
        try:
            cv2.imshow("Image Loader - Raw Validation", img)
            print("Displaying image window. Press any key to close...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"[Info] GUI display skipped ({e}).")

    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "datasets", "asl_alphabet", "asl_alphabet_train", "asl_alphabet_train", "A", "A1.jpg"
        ))

    inspect_and_load_image(target_path, display=False)
