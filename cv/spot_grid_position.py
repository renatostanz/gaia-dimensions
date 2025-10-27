import cv2
import sys
from utils import *
from time import time

file_name = sys.argv[1]

image = cv2.imread(file_name)
image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

grid_mask = get_grid_mask(image)
mask_edges = get_edges(grid_mask)
all_grid_contours = get_contours(mask_edges)
mask = get_max_contour_mask(all_grid_contours, image.shape[:2])

image = apply_mask(image, mask)


ball_mask = get_ball_mask(image)
ball_contours = get_contours(ball_mask)
ball_centroid = get_max_area_contour_centroid(ball_contours)


grid_center_points_mask = get_center_points_mask(image)
grid_center_points_contours = get_contours(grid_center_points_mask)

grid_center_points_infos = get_contours_infos(grid_center_points_contours)

grid_center_points_centroids = merge_split_centroids(grid_center_points_infos)
grid_center_points_centroids = get_ordered_centroids_infos(grid_center_points_centroids)

grid_boundaries = get_grid_boundaries(*image.shape[:-1], grid_center_points_centroids)


value = get_grid_value(grid_boundaries, ball_centroid)
print(value)
