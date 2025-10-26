import cv2
import sys
import numpy as np
from utils import *

def add_image(images: list[dict], name: str, image: np.array):
    images.append({
        "name": name,
        "image": image
    })

def nothing(x):
    pass

file_name = sys.argv[1]
images = []

image = cv2.imread(file_name)
add_image(images, "Original", image)

hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

ball_mask = get_ball_mask(hsv_image)
add_image(images, "Ball's Mask", ball_mask)
ball = get_ball_image(image, ball_mask)
add_image(images, "Ball", ball)


grid_mask = get_grid_mask(hsv_image)
add_image(images, "Grid's Mask", grid_mask)
grid = apply_mask(image, grid_mask)
add_image(images, "Grid", grid)
grid_edges = get_grid_edges(grid)
add_image(images, "Grid's Edges", grid_edges)
grid_divisions = get_grid_divisions(grid_edges)
add_image(images, "Grid's Divisions", grid_divisions)
grid_divisions_edges = get_grid_divisions_edges(grid_divisions)
add_image(images, "Grid's Divisions Edges", grid_edges)
grid_spaces = get_grid_spaces(grid_divisions_edges, grid)
add_image(images, "Grid's Divisions Spaces", grid_spaces)


for infos in images:
    name, image = infos.values()
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, 900, 600)
    cv2.imshow(name, image)

if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()

