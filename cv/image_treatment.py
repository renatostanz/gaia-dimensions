import cv2
import sys
import numpy as np
from utils import *

def nothing(x):
    pass

file_name = sys.argv[1]
image = cv2.imread(file_name)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

ball_mask = get_ball_mask(hsv_image)
ball = get_ball_image(image, ball_mask)

grid_mask = get_grid_mask(hsv_image)
grid = apply_mask(image, grid_mask)
grid_edges = get_grid_edges(grid)
grid_divisions = get_grid_divisions(grid, grid_edges)
grid_divisions_edges = get_grid_divisions_edges(grid_divisions)
grid_spaces = get_grid_spaces(grid_divisions_edges, grid)


cv2.imshow("Original", image)
cv2.imshow("Grid's Mask", grid_mask)
cv2.imshow("Grid", grid)
cv2.imshow("Grid's Edges", grid_edges)
cv2.imshow("Grid's Divisions", grid_divisions)
cv2.imshow("Grid's Divisions Edges", grid_divisions_edges)
cv2.imshow("Grid's Spaces", grid_spaces)
cv2.imshow("Ball's mask", ball_mask)
cv2.imshow("Ball", ball)

if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()

