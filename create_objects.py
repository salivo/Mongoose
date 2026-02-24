from math import degrees

from geometry_math import (
    Circle,
    Line,
    Plane,
    Point,
    angle_to_horizontal,
    foot_of_perp,
    generatePolygonPoints,
    intersect_circle2circle,
    intersect_circle2line,
    intersect_line2line,
    measure_point2point_distance,
    parallel_point_by_distance,
    parallel_point_by_line,
    perpendicular_point_from_distance,
)


def createPoint(objects, cords: tuple[float, float | None, float | None], name: str):
    if cords[1] is not None:
        p1 = Point((cords[0], -cords[1]), name + "1")
        objects[name + "1"] = p1
    if cords[2] is not None:
        p2 = Point((cords[0], cords[2]), name + "2")
        objects[name + "2"] = p2


def createLine(objects, p1_name: str, p2_name: str, name: str):
    p1 = objects[p1_name]
    p2 = objects[p2_name]
    if type(p1) is Point and type(p2) is Point:
        line = Line(p1, p2, name)
        objects[name] = line


def createCircle(objects, p_name: str, radius: float, name: str):
    p = objects[p_name]
    if type(p) is Point:
        circle = Circle(p, radius, name)
        objects[name] = circle


def createPlane(objects, cords: tuple[float, float | str, float | str], name: str):
    plane = Plane(cords, name)
    objects[name] = plane
    objects[name + "1"] = plane.line1
    objects[name + "2"] = plane.line2


def setType(objects, obj: str, line_type: str):
    object = objects[obj]
    if type(object) is not Circle and type(object) is not Line:
        return
    object.type = line_type


def setStyle(objects, obj: str, line_style: str):
    object = objects[obj]
    if type(object) is not Circle and type(object) is not Line:
        return
    object.style = line_style


def setCircleDrawRange(objects, circle: str, point_from: str, point_to: str):
    circle_obj = objects[circle]
    point_from_obj = objects[point_from]
    point_to_obj = objects[point_to]
    if (
        type(circle_obj) is not Circle
        or type(point_from_obj) is not Point
        or type(point_to_obj) is not Point
    ):
        return
    circle_obj.draw_from = degrees(
        angle_to_horizontal(circle_obj.center, point_from_obj)
    )
    circle_obj.draw_to = degrees(angle_to_horizontal(circle_obj.center, point_to_obj))


def footToLine(objects, point: str, line: str, name: str):
    point_obj = objects[point]
    line_obj = objects[line]
    if type(point_obj) is not Point or type(line_obj) is not Line:
        return
    objects[name] = foot_of_perp(line_obj, point_obj, name)


def createPerpFromPoint(
    objects, point: str, line: str, distance: float, name: str
) -> Point | None:
    point_obj = objects[point]
    line_obj = objects[line]
    if type(point_obj) is not Point or type(line_obj) is not Line:
        print("Invalid Line or Point")
        return
    p = perpendicular_point_from_distance(point_obj, line_obj, distance, name)
    if p is None:
        print("Cannot create perpendicular point")
        return
    objects[name] = p


def intersect(objects, obj1: str, obj2: str, name: str, n: int = 1):
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


def parallel(
    objects, base_point: str, line_parallel_to: str, offset: str | int, name: str
):
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


def findPointWithPlane(objects, point: str, plane: str, new_name: str | None = None):
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
    if new_name:
        newname = new_name
    result = parallel_point_by_line(p3, org_x, Line(pointobj, p1, ""), newname)
    if result is None:
        return
    objects[newname] = result


def measureDistance(objects, obj1: str, obj2: str | None = None):
    object1 = objects[obj1]
    if type(object1) is Line:
        return measure_point2point_distance(object1.p1, object1.p2)
    if type(object1) is Point and obj2 is not None:
        object2 = objects[obj2]
        if type(object2) is not Point:
            return None
        return measure_point2point_distance(object1, object2)


def createPolygon(objects, center: str, startpoint: str, points: list[str]):
    center_obj = objects[center]
    startpoint_obj = objects[startpoint]
    if type(center_obj) is not Point or type(startpoint_obj) is not Point:
        return None
    n = len(points) + 1
    polygon_points = generatePolygonPoints(center_obj, startpoint_obj, n)
    for coord, name in zip(polygon_points[1:], points):
        p = Point(coord, name)
        objects[name] = p
