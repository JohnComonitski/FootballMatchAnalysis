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
    
def players_to_list(team):
    x_columns = [c for c in team.keys() if c[-2:].lower()=='_x' and c!='ball_x'] # column header for player x positions
    x_columns.sort()

    home_away = "Home"
    if(str(team.keys()[2][0:4]) == "Away"):
            home_away = "Away"

    players = []
    for x_col in x_columns:
        name = x_col.split("_")[1]
        players.append(Player(None, None, None, None, None, home_away, name))
    return players