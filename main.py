import argparse
import ast
from visualization import DrawAxis, DrawPoint, DrawLine, DrawScene
from geometry_math import Point, Line, foot_of_perp_2d

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


COMMANDS = {
    "createPoint": createPoint,
    "createLine": createLine,
    "footToLine": footToLine,
}


def load_scene(file_path: str):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Split function and arguments
            func_name, arg_str = line.split("(", 1)
            func_name = func_name.strip()
            arg_str = arg_str.rstrip(")")

            if func_name not in COMMANDS:
                raise ValueError(f"Unknown command: {func_name}")

            # Parse args safely
            args = ast.literal_eval(f"({arg_str},)")  # pyright: ignore[reportAny]
            _ = COMMANDS[func_name](*args)  # pyright: ignore[reportAny]


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
