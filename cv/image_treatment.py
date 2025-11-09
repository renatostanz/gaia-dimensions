import cv2
import sys
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


file_name = sys.argv[1]

image = cv2.imread(file_name)
add_image("Original", image)

hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

try:
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
        add_image("Grid's Edges", mask_edges)


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
        hsv_image = apply_mask(hsv_image, mask)
    except Exception as e: 
        raise RuntimeError(f"Error while applying contour mask!")


    try:
        ball_mask = get_ball_mask(hsv_image)
    except Exception as e: 
        raise RuntimeError(f"Error while getting ball mask!")
    else:
        add_image("Ball's Mask", ball_mask)


    try:
        ball_contours = get_contours(ball_mask)
    except Exception as e: 
        raise RuntimeError(f"Error while getting ball mask contour!")
    else:
        ball_contours_draw = draw_contours(image, ball_contours)
        add_image("All Possible Ball Contours", ball_contours_draw)


    try:
        ball_centroid = get_max_area_contour_centroid(ball_contours)
    except Exception as e: 
        raise RuntimeError(f"Error while getting ball mask contour centroid!")
    else:
        ball_centroid_draw = draw_centroids_ordered(image, [{'coord': ball_centroid}])
        add_image("Ball Centroid", ball_centroid_draw)


    try:
        grid_center_points_mask = get_center_points_mask(hsv_image)
    except Exception as e: 
        raise RuntimeError(f"Error while getting center pointts mask!")
    else:
        add_image("Grid Center Points Mask", grid_center_points_mask)


    try:
        grid_center_points_contours = get_contours(grid_center_points_mask)
    except Exception as e: 
        raise RuntimeError(f"Error while getting center points contours!")
    else:
        grid_center_points_contours_draw = draw_contours(image, grid_center_points_contours)
        add_image("Grid Center Points Circles", grid_center_points_contours_draw)


    try:
        grid_center_points_infos = get_contours_infos(grid_center_points_contours)
        grid_center_points_centroids = merge_split_centroids(grid_center_points_infos)
        grid_center_points_centroids = get_ordered_centroids_infos(grid_center_points_centroids)
    except Exception as e: 
        raise RuntimeError(f"Error while handling the grid center points!")
    else:
        grid_center_points_draw = draw_centroids_ordered(
            image,
            grid_center_points_centroids
        )
        add_image("Grid Center Points Ordered", grid_center_points_draw)


    try:
        grid_boundaries = get_grid_boundaries(*image.shape[:-1], grid_center_points_centroids)
    except Exception as e: 
        raise RuntimeError(f"Error while getting grid boundaries!")
    else:
        grid_areas_draw = draw_grid_areas(image, grid_boundaries)
        add_image("Grid Areas", grid_areas_draw)

finally:
    render_images()



#def test_notations(image):
#    images = []
#    def add_image(name: str, image: np.array):
#        images.append({
#            "name": name,
#            "image": image
#        })
#
#    add_image("Original", image)
#
#    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#
#    grid_mask = get_grid_mask(hsv_image)
#    add_image("Grid's Mask", grid_mask)
#
#    mask_edges = get_edges(grid_mask)
#    add_image("Grid's Edges", mask_edges)
#
#    all_grid_contours = get_contours(mask_edges)
#    all_grid_contours_draw = draw_contours(image, all_grid_contours)
#    add_image("All Possible Grid Contours", all_grid_contours_draw)
#
#    mask = get_max_contour_mask(all_grid_contours, image.shape[:2])
#    add_image("Mask", mask)
#
#    hsv_image = apply_mask(hsv_image, mask)
#
#
#    ball_mask = get_ball_mask(hsv_image)
#    add_image("Ball's Mask", ball_mask)
#
#    ball_contours = get_contours(ball_mask)
#    ball_contours_draw = draw_contours(image, ball_contours)
#    add_image("All Possible Ball Contours", ball_contours_draw)
#
#    #print(ball_contours)
#    #ball_centroid = get_max_area_contour_centroid(ball_contours)
#    #ball_centroid_draw = draw_centroids_ordered(image, [{'coord': ball_centroid}])
#    #add_image("Ball Centroid", ball_centroid_draw)
#
#
#    #grid_center_points_mask = get_center_points_mask(hsv_image)
#    #add_image("Grid Center Points Mask", grid_center_points_mask)
#
#    #grid_center_points_contours = get_contours(grid_center_points_mask)
#    #grid_center_points_contours_draw = draw_contours(image, grid_center_points_contours)
#    #add_image("Grid Center Points Circles", grid_center_points_contours_draw)
#
#    #grid_center_points_infos = get_contours_infos(grid_center_points_contours)
#    #grid_center_points_centroids = merge_split_centroids(grid_center_points_infos)
#    #grid_center_points_centroids = get_ordered_centroids_infos(grid_center_points_centroids)
#    #grid_center_points_draw = draw_centroids_ordered(
#    #    image,
#    #    grid_center_points_centroids
#    #)
#    #add_image("Grid Center Points Ordered", grid_center_points_draw)
#
#    #grid_boundaries = get_grid_boundaries(*image.shape[:-1], grid_center_points_centroids)
#    #grid_areas_draw = draw_grid_areas(image, grid_boundaries)
#    #add_image("Grid Areas", grid_areas_draw)
#
#    return images
