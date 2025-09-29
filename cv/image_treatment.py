import cv2
import sys
import numpy as np

def nothing(x):
    pass

file_name = sys.argv[1]
image = cv2.imread(file_name)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower_ball = (126, 72, 224)
upper_ball = (179, 210, 255)
ball_mask = cv2.inRange(hsv_image, lower_ball, upper_ball)
blured_ball_mask = cv2.GaussianBlur(ball_mask, (5,5), 0)
ball = cv2.bitwise_and(
    image,
    image,
    mask=blured_ball_mask
)

lower_grid = (32, 9, 55)
upper_grid = (91, 120, 255)
grid_mask = cv2.inRange(hsv_image, lower_grid, upper_grid)
blured_grid_mask = cv2.medianBlur(grid_mask, 5)
grid = cv2.bitwise_and(
    image,
    image,
    mask=blured_grid_mask
)


cv2.imshow("Original", image)
cv2.imshow("Grid's mask", grid_mask)
cv2.imshow("Grid", grid)
cv2.imshow("Ball's mask", ball_mask)
cv2.imshow("Ball", ball)

if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()

