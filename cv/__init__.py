from time import sleep, time
from utils import map_grid_value
#from image_treatment import test_notations
import cv2
import requests

class VideoTracker:
    def __init__(self, video_ip='10.141.130.105', frame_interval=0.5):
        self.video_source = f'http://{video_ip}:8080/video'
        self.central_url = 'http://localhost:8000/grid'
        self.frame_interval = frame_interval
        self.cap = cv2.VideoCapture(self.video_source)
        self.last_frame_time = 0
        self.missing_frame_count = 0

    def process_frame(self, frame):
        try:
            r = map_grid_value(frame)
            print(r)
            return r
        except Exception as e:
            print(e)
            return None

    def display_frame(self, frame):
        cv2.imshow('IP camera Stream', frame)
        #images = test_notations(frame)
        #for infos in images:
        #    name, image = infos.values()
        #    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        #    cv2.resizeWindow(name, 900, 600)
        #    cv2.imshow(name, image)

    def run(self, display=False):
        print(f"Starting video tracking from {self.video_source}")

        while True:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                if self.missing_frame_count > 4:
                    print("Taking too long to get a frame!")
                    break

                self.missing_frame_count += 1
                print("Waiting for frame.")
                sleep(0.1)
                continue

            self.missing_frame_count = 0

            current_time = time()
            if (current_time - self.last_frame_time) >= self.frame_interval:
                self.last_frame_time = current_time
                result = self.process_frame(frame)

                if result is not None:
                    try:
                        response = requests.post(
                            self.central_url,
                            json=result.model_dump()
                        )
                        response.raise_for_status()
                    except Exception as e:
                        print(f"Error sending data to central server: {e}")

                if display:
                    self.display_frame(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        print("Ending captures!")
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    tracker = VideoTracker()
    tracker.run()
