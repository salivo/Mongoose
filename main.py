from typing import Dict
import matplotlib.pyplot as plt

from visualization import *
from geometry_math import *

points: dict[str, Point] = {}
lines: dict[str, Line] = {}

def createPoint(cords, name):
    p = Point(cords, name)
    points[name] = p
    return p

def createLine(p1_name, p2_name, name):
    p1 = points[p1_name]
    p2 = points[p2_name]
    l = Line(p1, p2, name)
    lines[name] = l
    return l

def footToLine(point:str, line:str, new_name:str, y:int):
    point_obj:Point = points[point[0]]
    line_obj:Line = lines[line[0]]
    if y not in (1, 2):
        return
    PointY = point_obj.y1 if y == 1 else point_obj.y2
    LineP1Y = line_obj.p1.y1 if y == 1 else line_obj.p1.y2
    LineP2Y = line_obj.p2.y1 if y == 1 else line_obj.p2.y2
    if (None in (PointY, LineP1Y, LineP2Y)):
        return
    foot_xy = foot_of_perp_2d(
        (line_obj.p1.x, LineP1Y),
        (line_obj.p2.x, LineP2Y),
        (point_obj.x, PointY)
    )
    if y == 1:
        NewPoint = Point((-foot_xy[0], -foot_xy[1], None), new_name)
    else:
        NewPoint = Point((-foot_xy[0], None, foot_xy[1]), new_name)
    points[new_name] = NewPoint
    return NewPoint

def load_scene(file_path: str):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            exec(line, globals())

if __name__ == "__main__":
    # Draw axes
    plt.axhline(0, color='black', linewidth=0.8)
    plt.axvline(0, color='black', linewidth=0.8)

    # Load scene commands from file
    load_scene("scene.mgs")

    # Draw all objects
    for p in points.values():
        DrawPoint(p)

    for l in lines.values():
        DrawLine(l)

    plt.axis("equal")
    plt.show()
