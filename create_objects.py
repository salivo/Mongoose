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

org_x: Line = Line(
    0, Point(0, (-10, 0), "ORG_X_1"), Point(0, (10, 0), "ORG_X_1"), "org_x"
)
org_x.type = "none"
org_y: Line = Line(
    1, Point(1, (0, -10), "ORG_Y_1"), Point(1, (0, 10), "ORG_Y_1"), "org_y"
)
org_y.type = "none"


def createPoint(
    id, objects, cords: tuple[float, float | None, float | None], name: str
):
    if cords[1] is not None:
        p1 = Point(id, (cords[0], -cords[1]), name + "1")
        objects[name + "1"] = p1
    if cords[2] is not None:
        p2 = Point(id, (cords[0], cords[2]), name + "2")
        objects[name + "2"] = p2


def createLine(id, objects, p1_name: str, p2_name: str, name: str):
    p1 = objects[p1_name]
    p2 = objects[p2_name]
    if type(p1) is Point and type(p2) is Point:
        line = Line(id, p1, p2, name)
        objects[name] = line


def createCircle(id, objects, p_name: str, radius: float, name: str):
    p = objects[p_name]
    if type(p) is Point:
        circle = Circle(id, p, radius, name)
        objects[name] = circle


def createPlane(id, objects, cords: tuple[float, float | str, float | str], name: str):
    plane = Plane(id, cords, name)
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


def setCircleDrawRange(id: int, objects, circle: str, point_from: str, point_to: str):
    circle_obj = objects[circle]
    point_from_obj = objects[point_from]
    point_to_obj = objects[point_to]
    if (
        not isinstance(circle_obj, Circle)
        or not isinstance(point_from_obj, Point)
        or not isinstance(point_to_obj, Point)
    ):
        return
    start_angle = degrees(angle_to_horizontal(circle_obj.center, point_from_obj))
    end_angle = degrees(angle_to_horizontal(circle_obj.center, point_to_obj))
    draw_span = end_angle - start_angle
    if draw_span < 0:
        draw_span += 360

    circle_obj.draw_from = start_angle
    circle_obj.draw_span = draw_span


def footToLine(id, objects, point: str, line: str, name: str):
    point_obj = objects[point]
    line_obj = objects[line]
    if type(point_obj) is not Point or type(line_obj) is not Line:
        return
    objects[name] = foot_of_perp(id, line_obj, point_obj, name)


def createPerpFromPoint(
    id, objects, point: str, line: str, distance: float, name: str
) -> Point | None:
    point_obj = objects[point]
    line_obj = objects[line]
    if type(point_obj) is not Point or type(line_obj) is not Line:
        print("Invalid Line or Point")
        return
    p = perpendicular_point_from_distance(id, point_obj, line_obj, distance, name)
    if p is None:
        print("Cannot create perpendicular point")
        return
    objects[name] = p


def intersect(id, objects, obj1: str, obj2: str, name: str, n: int = 1):
    a = objects[obj1]
    b = objects[obj2]
    if isinstance(a, Line) and isinstance(b, Line):
        p = intersect_line2line(id, a, b, name)
    elif isinstance(a, Circle) and isinstance(b, Circle):
        p = intersect_circle2circle(id, a, b, name, n)
    elif isinstance(a, Circle) and isinstance(b, Line):
        p = intersect_circle2line(id, a, b, name, n)
    elif isinstance(a, Line) and isinstance(b, Circle):
        p = intersect_circle2line(id, b, a, name, n)
    else:
        print("Unsupported types for intersection")
        return
    if p is None:
        return
    objects[name] = p


def parallel(
    id, objects, base_point: str, line_parallel_to: str, offset: str | int, name: str
):
    p = objects[base_point]
    line = objects[line_parallel_to]
    if not isinstance(p, Point) or not isinstance(line, Line):
        return
    if isinstance(offset, str):
        lineto = objects[offset]
        if isinstance(lineto, Line):
            result = parallel_point_by_line(id, p, line, lineto, name)
            if result is None:
                return
            objects[name] = result
    else:
        objects[name] = parallel_point_by_distance(id, p, line, offset, name)


def findPointWithPlane(
    id, objects, point: str, plane: str, new_name: str | None = None
):
    if point not in objects or plane not in objects:
        return
    pointobj = objects[point]
    planeobj = objects[plane]
    if not isinstance(pointobj, Point) or not isinstance(planeobj, Plane):
        return
    newname = pointobj.name

    p1 = parallel_point_by_line(id, pointobj, org_y, org_x, "")
    if p1 is None:
        return

    if pointobj.name.endswith("1"):
        newname = pointobj.name[:-1] + "2"
        p2 = parallel_point_by_line(id, pointobj, planeobj.line1, org_x, "")
        if p2 is None:
            return
        p3 = parallel_point_by_line(id, p2, org_y, planeobj.line2, "")

    elif pointobj.name.endswith("2"):
        newname = pointobj.name[:-1] + "1"
        p2 = parallel_point_by_line(id, pointobj, planeobj.line2, org_x, "")
        if p2 is None:
            return
        p3 = parallel_point_by_line(id, p2, org_y, planeobj.line1, "")
    else:
        raise ValueError(f"Name {pointobj.name} has no 1/2 suffix")
    if not p3:
        return
    if new_name:
        newname = new_name
    result = parallel_point_by_line(id, p3, org_x, Line(id, pointobj, p1, ""), newname)
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


def createPolygon(id, objects, center: str, startpoint: str, points: list[str]):
    center_obj = objects[center]
    startpoint_obj = objects[startpoint]
    if type(center_obj) is not Point or type(startpoint_obj) is not Point:
        return None
    n = len(points) + 1
    polygon_points = generatePolygonPoints(id, center_obj, startpoint_obj, n)
    for coord, name in zip(polygon_points[1:], points):
        p = Point(id, coord, name)
        objects[name] = p


def getObject(objects, name: str):
    return objects[name]
