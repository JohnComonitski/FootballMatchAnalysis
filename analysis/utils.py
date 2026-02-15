import math
import cv2
import os
from natsort import natsorted

def circumference_points(center, r, step):
    cx, cy = center
    points = []
    
    theta = 0.0
    while theta < 2 * math.pi:
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
        theta += step

    return points

def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x2 - x1, y2 - y1)

def pass_points(p1, p2, step=1):
    x1, y1 = p1
    x2, y2 = p2
    
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return [p1]
    
    n_steps = int(dist / step)
    
    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist
    
    points = []
    for i in range(n_steps + 1):
        x = x1 + dx * step * i
        y = y1 + dy * step * i
        points.append((x, y))
    
    if points[-1] != (x2, y2):
        points.append((x2, y2))
    
    return points

def power_function(x):
    #f(x) = 1 / (1 + e^(-10*(x - 0.5)))
    return round(float(1 / ( 1 + math.exp( 30 * (x - 0.5)))), 2)

def gen_video(image_folder="", output_video="", fps = 24):
    if image_folder == "":
        return

    images = [img for img in os.listdir(image_folder) if img.lower().endswith(".png")]
    images = natsorted(images)

    if not images:
        raise 

    first_frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = first_frame.shape

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    for img_name in images:
        frame = cv2.imread(os.path.join(image_folder, img_name))
        video.write(frame)

    video.release()

def get_center(box):
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    cx = round((min_x + max_x) / 2, 1)
    cy = round((min_y + max_y) / 2, 1)

    return (cx, cy)

def get_quadrant(coords, zone, mapping):
    x, y = coords
    box = mapping[str(zone)]

    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    
    min_x, max_x = min(xs), max(xs)
    max_y, min_y = max(ys), min(ys)

    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    if x <= cx and y >= cy:
        return 1
    elif x > cx and y >= cy:
        return 2
    elif x <= cx and y < cy:
        return 3
    else:
        return 4

def is_pass_possible(moment, end):
    if(str(end[0]) != "nan" and str(end[0]) != "nan"):
        res = circumference_points(end, 5, .25)
        for ps in res:
            if (ps[0] > -53 and ps[0] < 53) and (ps[1] > -34 and ps[1] < 34):
                p = moment.pass_probability(ps)
                if p > .01:
                    return 1
    return 0

def in_front_of_player(start, end, point):
    x1, y1 = start
    x2, y2 = end
    x3, y3 = point

    if x1 >= x2:
        if x3 > x2:
            return True
    else:
        if x3 <= x2:
            return True

    dx = x2 - x1
    dy = y2 - y1

    nx = dx
    ny = dy

    side_start = nx * (x1 - x2) + ny * (y1 - y2)
    side_point = nx * (x3 - x2) + ny * (y3 - y2)

    return side_start * side_point > 0