import time
import threading
import numpy as np

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

class CameraDetector:
    """
    100% Offline Local Camera Vision Service.
    Monitors room activity (Cleaning room, Moving around, User away, Sitting at desk)
    to trigger situation-based physical complaints!
    """
    def __init__(self, plant_state):
        self.plant_state = plant_state
        self.enabled = False
        self.camera = None
        self.is_running = False
        self.last_activity = "at_desk"
        self.last_activity_desc = "User at Desk"
        self.motion_level = 0.0
        self.thread = None

    def start_camera(self):
        if not HAS_OPENCV:
            print("[CameraDetector] OpenCV not installed.")
            return False
        if self.is_running:
            return True

        self.is_running = True
        self.thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.thread.start()
        return True

    def stop_camera(self):
        self.is_running = False
        if self.camera:
            try:
                self.camera.release()
            except Exception:
                pass
            self.camera = None

    def _camera_loop(self):
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("[CameraDetector] Webcam not accessible.")
                self.is_running = False
                self.last_activity_desc = "Camera Not Available"
                return

            prev_frame = None

            while self.is_running:
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    time.sleep(0.5)
                    continue

                # Resize frame for fast processing
                small = cv2.resize(frame, (320, 240))
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if prev_frame is None:
                    prev_frame = gray
                    time.sleep(0.5)
                    continue

                # Compute frame difference
                frame_delta = cv2.absdiff(prev_frame, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)

                # Motion area score
                motion_area = np.sum(thresh > 0)
                self.motion_level = motion_area / (320.0 * 240.0)

                prev_frame = gray

                # Classify physical activity
                if self.motion_level > 0.15:
                    self.last_activity = "cleaning_room"
                    self.last_activity_desc = "Moving Around / Cleaning Room"
                elif self.motion_level < 0.005:
                    self.last_activity = "user_away"
                    self.last_activity_desc = "User Away / Left Desk"
                else:
                    self.last_activity = "at_desk"
                    self.last_activity_desc = "User Present at Desk"

                time.sleep(0.5)
        except Exception as e:
            print(f"[CameraDetector] Error in camera loop: {e}")
            self.last_activity_desc = f"Camera Error ({e})"
        finally:
            if self.camera:
                self.camera.release()
                self.camera = None
            self.is_running = False

    def detect_physical_context(self):
        """Returns active physical activity context tag and human readable description."""
        if not self.is_running:
            return None, "Camera Offline"
        return self.last_activity, self.last_activity_desc
