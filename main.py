import argparse
import atexit
import traceback
from typing import cast, override
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver
from visualization import Visualization
from geometry_math import (
    Plane,
    Point,
    Line,
    Circle,
    foot_of_perp,
    intersect_circle2circle,
    intersect_circle2line,
    intersect_line2line,
    parallel_point_by_distance,
    parallel_point_by_line,
    perpendicular_point_from_distance,
)

objects: dict[str, Point | Line | Circle | Plane] = {}

org_x: Line = Line(Point((-10, 0), "ORG_X_1"), Point((10, 0), "ORG_X_1"), "org_x")
org_y: Line = Line(Point((0, -10), "ORG_Y_1"), Point((0, 10), "ORG_Y_1"), "org_y")


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


def createPlane(cords: tuple[float, float, float], name: str):
    plane = Plane(cords, name)
    objects[name] = plane
    objects[name + "1"] = plane.line1
    objects[name + "2"] = plane.line2


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


def parallel(base_point: str, line_parallel_to: str, offset: str | int, name: str):
    p = objects[base_point]
    line = objects[line_parallel_to]
    if not isinstance(p, Point) or not isinstance(line, Line):
        return
    if isinstance(offset, str):
        lineto = objects[offset]
        if isinstance(lineto, Line):
            result = parallel_point_by_line(p, line, lineto, name)
            if result is None:
                return
            objects[name] = result
    else:
        objects[name] = parallel_point_by_distance(p, line, offset, name)


def findPointWithPlane(point: str, plane: str):
    if point not in objects or plane not in objects:
        return
    pointobj = objects[point]
    planeobj = objects[plane]
    if not isinstance(pointobj, Point) or not isinstance(planeobj, Plane):
        return
    newname = pointobj.name

    p1 = parallel_point_by_line(pointobj, org_y, org_x, "")
    if p1 is None:
        return

    if pointobj.name.endswith("1"):
        newname = pointobj.name[:-1] + "2"
        p2 = parallel_point_by_line(pointobj, planeobj.line1, org_x, "")
        if p2 is None:
            return
        p3 = parallel_point_by_line(p2, org_y, planeobj.line2, "")

    elif pointobj.name.endswith("2"):
        newname = pointobj.name[:-1] + "1"
        p2 = parallel_point_by_line(pointobj, planeobj.line2, org_x, "")
        if p2 is None:
            return
        p3 = parallel_point_by_line(p2, org_y, planeobj.line1, "")
    else:
        raise ValueError(f"Name {pointobj.name} has no 1/2 suffix")
    if not p3:
        return
    result = parallel_point_by_line(p3, org_x, Line(pointobj, p1, ""), newname)
    if result is None:
        return
    objects[newname] = result


safe_commands = {
    "createPoint": createPoint,
    "createLine": createLine,
    "createCircle": createCircle,
    "createPlane": createPlane,
    "footToLine": footToLine,
    "intersect": intersect,
    "parallel": parallel,
    "createPerpFromPoint": createPerpFromPoint,
    "findPointWithPlane": findPointWithPlane,
    "objects": objects,
}


def load_scene(file_path: str):
    objects.clear()
    objects["org_x"] = org_x
    objects["org_y"] = org_y
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


class ObserverHandler(FileSystemEventHandler):
    def __init__(self, path: str):
        self.path: str = path

    @override
    def on_modified(self, event: FileSystemEvent):
        if self.path == event.src_path:
            print(f"File modified: {event.src_path}")
            load_scene(file_path)
            visual.drawScene(objects)


def close(observer: BaseObserver) -> None:
    observer.stop()
    observer.join()


if __name__ == "__main__":
    visual = Visualization()
    parser = argparse.ArgumentParser(description="Process a file path.")
    _ = parser.add_argument("file", help="Path to the input file")
    args = parser.parse_args()
    file_path = cast(str, args.file)
    observer = Observer()
    handler = ObserverHandler(file_path)
    _ = observer.schedule(handler, file_path, recursive=True)
    observer.start()
    _ = atexit.register(close, observer)
    load_scene(file_path)
    visual.drawScene(objects)
    visual.sceneLoop()
