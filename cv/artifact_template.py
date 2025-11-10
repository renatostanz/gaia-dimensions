import cv2
import sys
import os
import numpy as np
from utils import *

images = []
def add_image(name: str, image: np.array):
    images.append({
        "name": name,
        "image": image
    })

def render_images():
    for infos in images:
        name, image = infos.values()
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, 900, 600)
        cv2.imshow(name, image)

    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()


try:
    file_name = sys.argv[1]
    image = cv2.imread(file_name)
    add_image("Original", image)

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    try:
        grid_mask = get_grid_mask(hsv_image)
    except Exception as e: 
        raise RuntimeError(f"No grid mask found!")
    else:
        add_image("Grid's Mask", grid_mask)


    try:
        mask_edges = get_edges(grid_mask)
    except Exception as e: 
        raise RuntimeError(f"No grid edges selected!")
    else:
        add_image("Grid Edges", mask_edges)


    try:
        all_grid_contours = get_contours(mask_edges)
    except Exception as e: 
        raise RuntimeError(f"No grid contour found!")
    else:
        all_grid_contours_draw = draw_contours(image, all_grid_contours)
        add_image("All Possible Grid Contours", all_grid_contours_draw)


    try:
        mask = get_max_contour_mask(all_grid_contours, image.shape[:2])
    except Exception as e: 
        raise RuntimeError(f"No grid contour mask found!")
    else:
        add_image("Mask", mask)


    try:
        segmented_image = apply_mask(image, mask)
        segmented_image = apply_mask(segmented_image, grid_mask)
        gray = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
    except Exception as e: 
        raise RuntimeError(f"No grid contour mask found!")
    else:
        add_image("Gray Grid", gray)


    gray_path, mask_path = sys.argv[2:4]
    if os.access(gray_path, os.W_OK) and os.access(mask_path, os.W_OK):
        cv2.imwrite(gray_path, gray)
        cv2.imwrite(mask_path, mask)
    else: 
        raise OSError(f"Something went wrong with writing in {mask_path} or {gray_path}.")


finally:
    render_images()

