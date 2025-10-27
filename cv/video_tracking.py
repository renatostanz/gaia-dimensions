import cv2
from time import sleep, time

cap = cv2.VideoCapture('http://192.168.0.5:8080/video')

last_frame_time = 0
missing_frame_count = 0
while(True):
    ret, frame = cap.read()
    if not ret or frame is None:
        if missing_frame_count > 4:
            print("Taking too long to get a frame!")
            break
        missing_frame_count += 1
        print("Waiting for frame.")
        sleep(0.1)
        continue

    missing_frame_count = 0

    current_time = time()
    if (current_time - last_frame_time) >= 0.5:
        last_frame_time = current_time
        cv2.imshow('IP camera Stream',frame)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break


print("Ending captures")
cap.release()
cv2.destroyAllWindows()
