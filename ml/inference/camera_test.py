import os
import sys
import cv2
import time
from typing import Dict, Any

class CameraVerifier:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index

    def verify_camera(self) -> Dict[str, Any]:
        """Tests webcam availability, captures test frames, measures FPS, and returns diagnostic metrics."""
        result = {
            "camera_index": self.camera_index,
            "is_available": False,
            "resolution": None,
            "fps_estimate": 0.0,
            "frame_channels": None,
            "error_message": None
        }

        try:
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(self.camera_index)
            
            if not cap.isOpened():
                result["error_message"] = f"Camera device {self.camera_index} could not be opened or is in use by another application."
                return result

            # Set preferred resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            # Capture test frames
            start_time = time.time()
            frames_captured = 0
            test_frame = None

            for _ in range(5):
                ret, frame = cap.read()
                if ret and frame is not None:
                    frames_captured += 1
                    test_frame = frame

            elapsed = time.time() - start_time
            cap.release()

            if frames_captured > 0 and test_frame is not None:
                h, w, c = test_frame.shape
                result["is_available"] = True
                result["resolution"] = {"width": w, "height": h}
                result["frame_channels"] = c
                result["fps_estimate"] = round(frames_captured / max(0.001, elapsed), 2)
            else:
                result["error_message"] = "Camera opened but failed to capture video frames."

        except Exception as e:
            result["error_message"] = str(e)

        return result

def test_webcam(camera_index: int = 0, show_window: bool = True) -> Dict[str, Any]:
    """
    Webcam Verification Script:
    - Opens camera device
    - Displays live video feed
    - Listens for 'q' or 'Q' key to exit
    - Gracefully handles camera failure
    - Initially no AI processing
    """
    verifier = CameraVerifier(camera_index=camera_index)
    diag = verifier.verify_camera()

    if not diag["is_available"]:
        print(f"[Error] Camera index {camera_index} unavailable: {diag['error_message']}")
        return diag

    res_str = f"{diag['resolution']['width']}x{diag['resolution']['height']}" if diag['resolution'] else "640x480"
    print("==================================================")
    print("           WEBCAM HARDWARE VERIFICATION           ")
    print("==================================================")
    print(f"Camera Device : Index {camera_index}")
    print(f"Status        : Operational (200 OK)")
    print(f"Resolution    : {res_str} ({diag['frame_channels']} channels)")
    print("Controls      : Press 'Q' inside window to exit live stream.")
    print("==================================================")

    if show_window:
        try:
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(camera_index)
            frame_count = 0
            start_time = time.time()
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                fps = frame_count / max(0.001, time.time() - start_time)

                cv2.putText(frame, f"ASL Webcam Test - FPS: {fps:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'Q' to Exit", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                cv2.imshow("Webcam Live Feed Verification", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("User pressed 'Q'. Exiting live feed.")
                    break
            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"[Info] Window streaming ended: {e}")

    return diag

if __name__ == "__main__":
    interactive = "--gui" in sys.argv
    test_webcam(camera_index=0, show_window=interactive)
