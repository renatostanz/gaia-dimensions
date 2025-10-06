import cv2
import numpy as np
import copy
from shapely.geometry import Polygon


def get_ball_mask(hsv_image):
    lower_ball = (126, 72, 224)
    upper_ball = (179, 210, 255)
    return cv2.inRange(hsv_image, lower_ball, upper_ball)


def get_ball_image(source_image, mask):
    blured_mask = cv2.GaussianBlur(mask, (5,5), 0)
    return cv2.bitwise_and(
        source_image,
        source_image,
        mask=blured_mask
    )


def get_grid_mask(hsv_image):
    lower_grid = (32, 9, 55)
    upper_grid = (91, 120, 255)
    return cv2.inRange(hsv_image, lower_grid, upper_grid)


def apply_mask(source_image, mask):
    blured_mask = cv2.medianBlur(mask, 5)
    blured_mask = cv2.GaussianBlur(blured_mask, (5,5), 0)
    return cv2.bitwise_and(
        source_image,
        source_image,
        mask=blured_mask
    )


def get_grid_edges(grid):
    lines_image = np.zeros(grid[:,:,0].shape, dtype=np.uint8)
    window_name = ('Sobel Demo - Simple Edge Detector')
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S

    gray = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY)
    
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    
    
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    
    
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

    _, thresh_image = cv2.threshold(grad, 25, 255, cv2.THRESH_BINARY)
    thresh_image = apply_mask(thresh_image, thresh_image)
    _, thresh_image = cv2.threshold(thresh_image, 250, 255, cv2.THRESH_BINARY)

    return thresh_image


def get_grid_divisions(source_grid, edges):
    edges_with_lines = copy.deepcopy(edges)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi/180,
        threshold=50,
        minLineLength=20,
        maxLineGap=50
    )
    for points in lines:
        x1,y1,x2,y2=points[0]
        cv2.line(
            edges_with_lines,
            (x1,y1),
            (x2,y2),
            255,
            2
        )

    return edges_with_lines


def get_grid_divisions_edges(lines):
    blured_mask = cv2.medianBlur(lines, 3)
    blured_lines = cv2.bitwise_and(
        lines,
        lines,
        mask=blured_mask
    )

    threshold_lower = 50
    threshold_upper = 150

    return cv2.Canny(
        blured_lines,
        threshold_lower,
        threshold_upper,
        L2gradient=True
    )


def get_grid_spaces(edges, source_grid):
    grid = copy.deepcopy(source_grid)
    contours, hierarchy = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    boxes = []
    for c in contours:
        rot_rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rot_rect)
        box = np.intp(box)
        boxes.append(box)

    sorted_boxes = np.array(sorted(boxes, key=lambda box: Polygon(box).area))
    for box in sorted_boxes:
        cv2.drawContours(grid, [box], 0, (0,0,255), 2)
    #print(sorted_boxes)
    #print(box, Polygon(box).area, box[0], (box[0, 0], box[0, 1]))
    return grid
