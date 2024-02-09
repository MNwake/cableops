import threading
import cv2

class DSLRCamera:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.is_running = False
        self.frame = None
        self.thread = None

    def start_camera(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.update_frame)
        self.thread.start()

    def stop_camera(self):
        self.is_running = False
        if self.thread is not None:
            self.thread.join()

    def update_frame(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def get_frame(self):
        return self.frame

    def __del__(self):
        self.stop_camera()
        self.cap.release()
