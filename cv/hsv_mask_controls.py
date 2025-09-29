import cv2
import sys
import numpy as np

def nothing(x):
    pass

file_name = sys.argv[1]

image = cv2.imread(file_name)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

cv2.namedWindow('controls')
cv2.createTrackbar('lower_h', 'controls', 0, 178, nothing)
cv2.createTrackbar('lower_s', 'controls', 0, 254, nothing)
cv2.createTrackbar('lower_v', 'controls', 0, 254, nothing)

cv2.createTrackbar('upper_h', 'controls', 1, 179, nothing)
cv2.createTrackbar('upper_s', 'controls', 1, 255, nothing)
cv2.createTrackbar('upper_v', 'controls', 1, 255, nothing)

while True:
    lower_h = cv2.getTrackbarPos('lower_h', 'controls')
    lower_s = cv2.getTrackbarPos('lower_s', 'controls')
    lower_v = cv2.getTrackbarPos('lower_v', 'controls')

    upper_h = cv2.getTrackbarPos('upper_h', 'controls')
    upper_s = cv2.getTrackbarPos('upper_s', 'controls')
    upper_v = cv2.getTrackbarPos('upper_v', 'controls')

    lower_limits = (lower_h, lower_s, lower_v)
    upper_limits = (upper_h, upper_s, upper_v)

    controls_mask = cv2.inRange(hsv_image, lower_limits, upper_limits)

    result = cv2.bitwise_and(image, image, mask=controls_mask)

    cv2.imshow("original", image)
    cv2.imshow("mask", controls_mask)
    cv2.imshow("new", result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

