import cv2
import subprocess
import numpy as np
import abc

class InputDevice(abc.ABC):

    @abc.abstractmethod
    def read_data(self):
        """Read data from the input device and return it."""
        pass

    @abc.abstractmethod
    def start_stream(self):
        """Start the video stream."""
        pass

    @abc.abstractmethod
    def stop_stream(self):
        """Stop the video stream."""
        pass

class DSLRCam(InputDevice):

    def init_camera(self):
        command = "gphoto2 --capture-movie --stdout".split()
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def read_mjpeg_stream(stream):
        # Reading frame from the camera
        buffer = b''
        while True:
            data = stream.read(2048)
            buffer += data
            jpg_start = buffer.find(b'\xff\xd8')
            jpg_end = buffer.find(b'\xff\xd9')

            if jpg_start != -1 and jpg_end != -1:
                jpg_data = buffer[jpg_start:jpg_end + 2]
                buffer = buffer[jpg_end + 2:]

                if jpg_data:  # Check if the JPEG data is not empty
                    frame = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    return frame

    def read_data(self):
        camera_process = self.init_camera()
        frame = self.read_mjpeg_stream(camera_process.stdout)
        frame = cv2.resize(frame, (1000, 1000))
        camera_process.terminate()
        return frame

    def start_stream(self):
        self.camera_process = self.init_camera()

    def stop_stream(self):
        self.camera_process.terminate()

class USBCam(InputDevice):

    def __init__(self, device_id):
        self.device_id = device_id
        self.cap = None

    def read_data(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(self.device_id)
        
        ret, frame = self.cap.read()

        if not ret:
            raise RuntimeError("Failed to read frame from the USB camera.")

        return frame

    def start_stream(self):
        self.cap = cv2.VideoCapture(self.device_id)

    def stop_stream(self):
        if self.cap:
            self.cap.release()
            self.cap = None