import cv2
import numpy as np
from shapely.geometry import Polygon
from itertools import combinations


def get_ball_mask(hsv_image):
    lower_ball = (135, 50, 136)
    upper_ball = (179, 220, 255)
    return cv2.inRange(hsv_image, lower_ball, upper_ball)


def get_grid_mask(hsv_image):
    lower_grid = (20, 10, 56)
    upper_grid = (90, 100, 255)
    return cv2.inRange(hsv_image, lower_grid, upper_grid)


def get_max_contour_mask(contours, image_2d_shape):
    contour = get_contour_with_max_area(contours)
    mask = np.zeros(image_2d_shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, (255), -1)
    return mask


def apply_mask(source_image, mask):
    return cv2.bitwise_and(
        source_image,
        source_image,
        mask=mask
    )


def get_edges(grid):
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S

    gray = grid
    if len(gray.shape) > 2:
        gray = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY)
    
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    
    
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    
    
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

    _, thresh_image = cv2.threshold(grad, 25, 255, cv2.THRESH_BINARY)
    thresh_image = apply_mask(thresh_image, thresh_image)
    _, thresh_image = cv2.threshold(thresh_image, 250, 255, cv2.THRESH_BINARY)

    return grad



def get_center_points_mask(hsv_image):
    lower = (89, 72, 87)
    upper = (132, 255, 255)
    return cv2.inRange(hsv_image, lower, upper)


def get_contour_with_max_area(contours):
    return max(contours, key=lambda c: cv2.contourArea(c))


def get_contours_infos(contours):
    moments = [cv2.moments(c) for c in contours]
    # Centroid's M00 is its area
    moments = [m for m in moments if m['m00'] > 150]
    infos = []
    for m in moments:
        x = int(m['m10']/m['m00'])
        y = int(m['m01']/m['m00'])
        infos.append({
            'centroid': (x,y),
            'area': m['m00']
        })

    return infos


def get_contours(image):
    contours, hierarchy = cv2.findContours(
        image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    return contours


def draw_contours(input_image, contours):
    image = input_image.copy()

    if contours:
        cv2.drawContours(image, contours, -1, (0,0,255), 3)
        centroids = [i.get('centroid') for i in get_contours_infos(contours)]
        for c in centroids:
            cv2.circle(image, c, 2, (0,0,0), 2)

    return image


def get_euclidean_distance(p1, p2):
    return (
        (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2
    )**(1/2)


def get_ordered_centroids_infos(centroids):
    centroids_with_infos = [
        {
            'coord': c,
            'dist_to_origin': get_euclidean_distance(c, (0,0))
        }
        for c in centroids
    ]
    centroids_with_infos = sorted(
        centroids_with_infos,
        key=lambda c: c.get('dist_to_origin')
    )

    print("centroids", centroids)
    centroid_1_horizontal = centroids_with_infos[1].get('coord')[1]
    centroid_2_horizontal = centroids_with_infos[2].get('coord')[1]

    if centroid_1_horizontal > centroid_2_horizontal:
        tmp = centroids_with_infos[1]
        centroids_with_infos[1] = centroids_with_infos[2]
        centroids_with_infos[2] = tmp

    return centroids_with_infos


def merge_split_centroids(infos):
    if len(infos) != 5:
        return [i.get('centroid') for i in infos]

    pair_infos_and_distances = [
        {
            'dist': get_euclidean_distance(i[0].get('centroid'), i[1].get('centroid')),
            'infos': i
        }
        for i in combinations(infos, 2)
    ]
    min_distance_points = min(pair_infos_and_distances, key=lambda i: i.get('dist'))
    centroids = [i.get('centroid') for i in infos if i not in min_distance_points.get('infos')]

    centroid_0, area_0 = min_distance_points.get('infos')[0].values()
    centroid_1, area_1 = min_distance_points.get('infos')[1].values()
    merged_centroid_width = int(
        (centroid_0[0] * area_0 + centroid_1[0] * area_1) / (area_0 + area_1)
    )
    merged_centroid_height = int(
        (centroid_0[1] * area_0 + centroid_1[1] * area_1) / (area_0 + area_1)
    )
    centroids.append((merged_centroid_width, merged_centroid_height))

    return centroids


def draw_centroids_ordered(input_image, ordered_centroids):
    image = input_image.copy()

    for i, p in enumerate(ordered_centroids):
        cv2.putText(
            image,
            str(i),
            p.get('coord'),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,0),
            4
        ) 

    return image


def get_vector_limit(p1, p2, height, width):
    delta_width = p2[0] - p1[0]
    delta_height = p2[1] - p1[1]

    def get_boundary_coord(use_min_width: bool, use_min_height: bool):
        width_boundary = width
        if use_min_width:
            width_boundary = 0
        
        w = (width_boundary - p1[0]) / delta_width

        height_boundary = height
        if use_min_height:
            height_boundary = 0

        h = (height_boundary - p1[1]) / delta_height

        if w > h:
            w_coord = int(p1[0] + delta_width * h)
            return (w_coord, height_boundary)
        else:
            h_coord = int(p1[1] + delta_height * w)
            return (width_boundary, h_coord)

    if delta_height == 0:
        if delta_width < 0:
            return (0, p1[1])
        return (width, p1[1])

    elif delta_width == 0:
        if delta_height < 0:
            return (p1[0], 0)
        return (p1[0], height)

    elif delta_width < 0:
        if delta_height > 0:
            return get_boundary_coord(use_min_height=False, use_min_width=True)
        return get_boundary_coord(use_min_height=True, use_min_width=True)

    else:
        if delta_height > 0:
            return get_boundary_coord(use_min_height=False, use_min_width=False)
        return get_boundary_coord(use_min_height=True, use_min_width=False)


def get_grid_boundaries(height, width, centroids):
    height -= 1
    width -= 1

    return np.array([
                [
                    [
                        (0,0),
                        get_vector_limit(
                            centroids[2].get('coord'),
                            centroids[0].get('coord'), 
                            height,
                            width, 
                        ),
                        centroids[0].get('coord'),
                        get_vector_limit(
                            centroids[1].get('coord'), 
                            centroids[0].get('coord'),
                            height,
                            width,
                        ),
                    ],
        
                    [
                        get_vector_limit(
                            centroids[2].get('coord'),
                            centroids[0].get('coord'),
                            height,
                            width,
                        ),
                        get_vector_limit(
                            centroids[3].get('coord'),
                            centroids[1].get('coord'),
                            height,
                            width,
                        ),
                        centroids[1].get('coord'),
                        centroids[0].get('coord'),
                    ],
                    
                    [
                        get_vector_limit(
                            centroids[3].get('coord'),
                            centroids[1].get('coord'),
                            height,
                            width,
                        ),
                        (width, 0),
                        get_vector_limit(
                            centroids[0].get('coord'),
                            centroids[1].get('coord'),
                            height,
                            width,
                        ),
                        centroids[1].get('coord'),
                    ],
                ],
                [
                    [
                        get_vector_limit(
                            centroids[1].get('coord'),
                            centroids[0].get('coord'),
                            height,
                            width,
                        ),
                        centroids[0].get('coord'),
                        centroids[2].get('coord'),
                        get_vector_limit(
                            centroids[3].get('coord'),
                            centroids[2].get('coord'),
                            height,
                            width,
                        ),
                    ],
        
                    [
                        centroids[0].get('coord'),
                        centroids[1].get('coord'),
                        centroids[3].get('coord'),
                        centroids[2].get('coord'),
                    ],
                    
                    [
                        centroids[1].get('coord'),
                        get_vector_limit(
                            centroids[0].get('coord'),
                            centroids[1].get('coord'),
                            height,
                            width,
                        ),
                        get_vector_limit(
                            centroids[2].get('coord'),
                            centroids[3].get('coord'),
                            height,
                            width,
                        ),
                        centroids[3].get('coord'),
                    ],
                ],
        [
            [
                get_vector_limit(
                    centroids[3].get('coord'),
                    centroids[2].get('coord'),
                    height,
                    width,
                ),
                centroids[2].get('coord'),
                get_vector_limit(
                    centroids[0].get('coord'),
                    centroids[2].get('coord'),
                    height,
                    width,
                ),
                (0, height),
            ],
            [
                centroids[2].get('coord'),
                centroids[3].get('coord'),
                get_vector_limit(
                    centroids[1].get('coord'),
                    centroids[3].get('coord'),
                    height,
                    width,
                ),
                get_vector_limit(
                    centroids[0].get('coord'),
                    centroids[2].get('coord'),
                    height,
                    width,
                ),
            ],
            [
                centroids[3].get('coord'),
                get_vector_limit(
                    centroids[2].get('coord'),
                    centroids[3].get('coord'),
                    height,
                    width,
                ),
                (width, height),
                get_vector_limit(
                    centroids[1].get('coord'),
                    centroids[3].get('coord'),
                    height,
                    width,
                ),
            ],
        ],       
    ], np.int32)


def draw_grid_areas(input_image, clusters):
    image = input_image.copy()
    for line_clusters in clusters:
        cv2.polylines(image, line_clusters, True, (0,0,255), 2)

    return image


def get_max_area_contour_centroid(contours):
    max_area_contour = max(contours, key=lambda c: cv2.contourArea(c))
    moment = cv2.moments(max_area_contour)
    print(moment)
    x = int(moment['m10']/moment['m00'])
    y = int(moment['m01']/moment['m00'])
    return (x, y)


def get_grid_value(grid_boundaries, ball_centroid):
    values = [
        ["bottom-left", "middle-left", "top-left"],
        ["bottom-middle", "middle-middle", "top-middle"],
        ["bottom-right", "middle-right", "top-right"]
    ]
    for i, row in enumerate(values):
        for u, val in enumerate(row):
            contour = grid_boundaries[i, u]
            is_in = cv2.pointPolygonTest(contour, ball_centroid, False)
            if is_in >= 0:
                return val



def map_grid_value(input_image):
    image = input_image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    grid_mask = get_grid_mask(image)
    mask_edges = get_edges(grid_mask)
    all_grid_contours = get_contours(mask_edges)
    mask = get_max_contour_mask(all_grid_contours, image.shape[:2])

    image = apply_mask(image, mask)


    ball_mask = get_ball_mask(image)
    ball_contours = get_contours(ball_mask)
    ball_centroid = get_max_area_contour_centroid(ball_contours)
    #return ball_centroid


    grid_center_points_mask = get_center_points_mask(image)
    grid_center_points_contours = get_contours(grid_center_points_mask)
    #return cv2.cvtColor(draw_contours(image, grid_center_points_contours), cv2.COLOR_HSV2BGR)

    grid_center_points_infos = get_contours_infos(grid_center_points_contours)
    grid_center_points_centroids = merge_split_centroids(grid_center_points_infos)
    grid_center_points_centroids = get_ordered_centroids_infos(grid_center_points_centroids)

    grid_boundaries = get_grid_boundaries(*image.shape[:-1], grid_center_points_centroids)

    value = get_grid_value(grid_boundaries, ball_centroid)
    return value
