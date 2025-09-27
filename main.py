import argparse
import ast
import math
import traceback
from types import NoneType
from visualization import DrawAxis, DrawPoint, DrawLine, DrawScene
from geometry_math import (
    Point,
    Line,
    foot_of_perp_2d,
    intersect_2d,
    perpendicular_point_from_distance,
)

points: dict[str, Point] = {}
lines: dict[str, Line] = {}


def createPoint(cords: tuple[float, float, float], name: str):
    p = Point(cords, name)
    points[name] = p
    return p


def createLine(p1_name: str, p2_name: str, name: str, y: int = 0):
    if y not in (0, 1, 2):
        return
    p1 = points[p1_name]
    p2 = points[p2_name]
    line = Line(p1, p2, name, y)
    lines[name] = line
    return line


def footToLine(point: str, line: str, new_name: str, y: int):
    point_obj: Point = points[point[0]]
    line_obj: Line = lines[line[0]]
    if y not in (1, 2):
        return
    PointY = point_obj.y1 if y == 1 else point_obj.y2
    LineP1Y = line_obj.p1.y1 if y == 1 else line_obj.p1.y2
    LineP2Y = line_obj.p2.y1 if y == 1 else line_obj.p2.y2
    if None in (PointY, LineP1Y, LineP2Y):
        return
    foot_xy = foot_of_perp_2d(
        (line_obj.p1.x, LineP1Y), (line_obj.p2.x, LineP2Y), (point_obj.x, PointY)
    )
    if y == 1:
        NewPoint = Point((-foot_xy[0], -foot_xy[1], None), new_name)
    else:
        NewPoint = Point((-foot_xy[0], None, foot_xy[1]), new_name)
    points[new_name] = NewPoint
    return NewPoint


def intersect(line1_name: str, line2_name: str, new_name: str, y: int = 1):
    if y not in (1, 2):
        raise ValueError("y must be 1 or 2")

    L1 = lines[line1_name]
    L2 = lines[line2_name]

    # Choose the branch
    yattr = "y1" if y == 1 else "y2"
    A1 = (L1.p1.x, getattr(L1.p1, yattr))
    A2 = (L1.p2.x, getattr(L1.p2, yattr))
    B1 = (L2.p1.x, getattr(L2.p1, yattr))
    B2 = (L2.p2.x, getattr(L2.p2, yattr))

    # Check for None coordinates
    if None in (A1[1], A2[1], B1[1], B2[1]):
        # Intersection skipped: missing y coordinates
        return None

    xy = intersect_2d(A1, A2, B1, B2)
    if xy is None:
        # Lines are parallel — no intersection.
        return None

    x, y_val = xy
    if y == 1:
        pt = Point((-x, -y_val, None), new_name)
    else:
        pt = Point((-x, None, y_val), new_name)

    points[new_name] = pt
    return pt


def createPerpFromPoint(
    point_name: str, line_name: str, distance: float, new_point_name: str, y: int = 1
) -> Point | None:
    if y not in (1, 2):
        raise ValueError("y must be 1 or 2")

    base_pt = points[point_name]
    ref_line = lines[line_name]

    yattr = "y1" if y == 1 else "y2"
    A = (ref_line.p1.x, getattr(ref_line.p1, yattr))
    B = (ref_line.p2.x, getattr(ref_line.p2, yattr))
    P = (base_pt.x, getattr(base_pt, yattr))

    if None in (A[1], B[1], P[1]):
        # Cannot create perpendicular from point — missing y values
        return None

    xy = perpendicular_point_from_distance(P, A, B, distance)
    if xy is None:
        # Line is degenerate; perpendicular not created
        return None
    x, y_val = xy
    if y == 1:
        new_pt = Point((-x, -y_val, None), new_point_name)
    else:
        new_pt = Point((-x, None, y_val), new_point_name)
    points[new_point_name] = new_pt
    return new_pt


def getPoint(name: str) -> Point | None:
    return points.get(name)


safe_commands = {
    "createPoint": createPoint,
    "createLine": createLine,
    "footToLine": footToLine,
    "intersect": intersect,
    "createPerpFromPoint": createPerpFromPoint,
    "getPoint": getPoint,
    "points": points,
    "lines": lines,
}


def load_scene(file_path: str):
    with open(file_path) as f:
        code = f.read()
    try:
        exec(code, {"__builtins__": None}, safe_commands)
    except Exception as e:
        tb_list = traceback.extract_tb(e.__traceback__)
        # find the last frame that belongs to the user's file
        user_frame = None
        for tb in tb_list:
            if tb.filename == "<string>":
                user_frame = tb
        if user_frame:
            print(f"Not allowed command on line {user_frame.lineno} in {file_path}")
        else:
            print(f"Error loading scene: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file path.")
    _ = parser.add_argument("file", help="Path to the input file")
    args = parser.parse_args()
    load_scene(args.file)  # pyright: ignore[reportAny]
    DrawAxis()
    for point in points.values():
        DrawPoint(point)

    for line in lines.values():
        DrawLine(line)
    DrawScene()
