import argparse
import traceback
from visualization import DrawAxis, DrawScene
from geometry_math import (
    Point,
    Line,
    Circle,
    foot_of_perp,
    intersect_circle2circle,
    intersect_circle2line,
    intersect_line2line,
    perpendicular_point_from_distance,
)

objects: dict[str, Point | Line | Circle] = {}


def createPoint(cords: tuple[float, float | None, float | None], name: str):
    if cords[1] is not None:
        p1 = Point((cords[0], -cords[1]), name + "1")
        objects[name + "1"] = p1
    if cords[2] is not None:
        p2 = Point((cords[0], cords[2]), name + "2")
        objects[name + "2"] = p2


def createLine(p1_name: str, p2_name: str, name: str):
    p1 = objects[p1_name]
    p2 = objects[p2_name]
    if type(p1) is Point and type(p2) is Point:
        line = Line(p1, p2, name)
        objects[name] = line


def createCircle(p_name: str, radius: float, name: str):
    p = objects[p_name]
    if type(p) is Point:
        circle = Circle(p, radius, name)
        objects[name] = circle


def footToLine(point: str, line: str, name: str):
    point_obj = objects[point]
    line_obj = objects[line]
    if type(point_obj) is not Point or type(line_obj) is not Line:
        return
    objects[name] = foot_of_perp(line_obj, point_obj, name)


def createPerpFromPoint(
    point: str, line: str, distance: float, name: str
) -> Point | None:
    point_obj = objects[point]
    line_obj = objects[line]
    if type(point_obj) is not Point or type(line_obj) is not Line:
        return
    p = perpendicular_point_from_distance(point_obj, line_obj, distance, name)
    if p is None:
        return
    objects[name] = p


def intersect(obj1: str, obj2: str, name: str, n: int = 1):
    a = objects[obj1]
    b = objects[obj2]
    if isinstance(a, Line) and isinstance(b, Line):
        p = intersect_line2line(a, b, name)
    elif isinstance(a, Circle) and isinstance(b, Circle):
        p = intersect_circle2circle(a, b, name, n)
    elif isinstance(a, Circle) and isinstance(b, Line):
        p = intersect_circle2line(a, b, name, n)
    elif isinstance(a, Line) and isinstance(b, Circle):
        p = intersect_circle2line(b, a, name, n)
    else:
        print("Unsupported types for intersection")
        return
    if p is None:
        return
    objects[name] = p


safe_commands = {
    "createPoint": createPoint,
    "createLine": createLine,
    "createCircle": createCircle,
    "footToLine": footToLine,
    "intersect": intersect,
    "createPerpFromPoint": createPerpFromPoint,
    "objects": objects,
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
    DrawScene(objects)
