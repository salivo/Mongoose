from math import sqrt
import numpy as np


class Point:
    def __init__(self, cords: tuple[float, float], name: str):
        self.x: float = -cords[0]
        self.y: float = cords[1]
        self.name: str = name


class Line:
    def __init__(self, p1: Point, p2: Point, name: str):
        self.p1: Point = p1
        self.p2: Point = p2
        self.name: str = name


class Circle:
    def __init__(self, center: Point, radius: float, name: str):
        self.center: Point = center
        self.name: str = name
        self.radius: float = radius


class Plane:
    def __init__(self, cords: tuple[float, float, float], name: str):
        self.p0: Point = Point((cords[0], 0), "_P" + name + "0")
        self.p1: Point = Point((0, -cords[1]), "_P" + name + "1")
        self.p2: Point = Point((0, cords[2]), "_P" + name + "2")
        self.line1: Line = Line(self.p0, self.p1, name + "1")
        self.line2: Line = Line(self.p0, self.p2, name + "2")
        self.name: str = name


def foot_of_perp(line: Line, point: Point, name: str) -> Point:
    # Extract the coordinates
    A = (line.p1.x, line.p1.y)
    B = (line.p2.x, line.p2.y)
    K = (point.x, point.y)

    A_arr = np.asarray(A, dtype=float)
    B_arr = np.asarray(B, dtype=float)
    K_arr = np.asarray(K, dtype=float)

    v = B_arr - A_arr
    vv = np.dot(v, v)  # pyright: ignore[reportAny]
    if vv == 0:  # Line is a single point
        foot_xy = A_arr.copy()
    else:
        t = np.dot(K_arr - A_arr, v) / vv  # pyright: ignore[reportAny]
        foot_xy = A_arr + t * v  # pyright: ignore[reportAny]

    # Return as a new Point
    return Point((-foot_xy[0], foot_xy[1]), name)


def perpendicular_point_from_distance(
    base_point: Point,  # Point from which the perpendicular is drawn
    line: Line,  # Line to which the perpendicular is relative
    distance: float,  # Distance from base_point along perpendicular
    name: str,
) -> Point | None:
    x1, y1 = line.p1.x, line.p1.y
    x2, y2 = line.p2.x, line.p2.y
    vx = x2 - x1
    vy = y2 - y1
    perp_x = -vy
    perp_y = vx
    norm = sqrt(perp_x**2 + perp_y**2)
    if norm == 0:
        return None  # Line is a single point
    perp_unit_x = perp_x / norm
    perp_unit_y = perp_y / norm
    px = base_point.x + distance * perp_unit_x
    py = base_point.y + distance * perp_unit_y
    return Point((-px, py), name)


def intersect_line2line(line1: Line, line2: Line, name: str) -> Point | None:
    x1, y1 = line1.p1.x, line1.p1.y
    x2, y2 = line1.p2.x, line1.p2.y
    x3, y3 = line2.p1.x, line2.p1.y
    x4, y4 = line2.p2.x, line2.p2.y

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Lines are parallel

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    return Point((-px, py), name)


def intersect_circle2line(
    circle: Circle, line: Line, name: str, n: int
) -> Point | None:
    # Circle center and radius
    cx, cy = circle.center.x, circle.center.y
    r = circle.radius

    # Line points
    x1, y1 = line.p1.x, line.p1.y
    x2, y2 = line.p2.x, line.p2.y

    # Parametric form of line: P(t) = (x1, y1) + t * (dx, dy)
    dx = x2 - x1
    dy = y2 - y1

    # Quadratic equation coefficients for |P(t) - C|^2 = r^2
    a = dx**2 + dy**2
    b = 2 * (dx * (x1 - cx) + dy * (y1 - cy))
    c = (x1 - cx) ** 2 + (y1 - cy) ** 2 - r**2

    disc = b**2 - 4 * a * c
    if disc < 0:
        return None  # No intersection

    sqrt_disc = sqrt(disc)

    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    intersections = [
        (x1 + t1 * dx, y1 + t1 * dy),
        (x1 + t2 * dx, y1 + t2 * dy),
    ]

    # Remove duplicates if tangent (disc == 0)
    _ = [tuple(map(float, set_)) for set_ in set(intersections)]

    if 1 <= n <= len(intersections):
        px, py = intersections[n - 1]
        return Point((-px, py), name)

    return None


def intersect_circle2circle(
    circle1: Circle, circle2: Circle, name: str, n: int
) -> Point | None:
    x1, y1, r1 = circle1.center.x, circle1.center.y, circle1.radius
    x2, y2, r2 = circle2.center.x, circle2.center.y, circle2.radius

    # Distance between centers
    dx = x2 - x1
    dy = y2 - y1
    d = sqrt(dx**2 + dy**2)

    # No solutions: circles too far apart or contained
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return None

    # Distance from circle1 center to line between intersections
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = sqrt(max(r1**2 - a**2, 0))

    # Base point along the line connecting the centers
    xm = x1 + a * dx / d
    ym = y1 + a * dy / d

    # Offsets for the two intersection points
    rx = -dy * (h / d)
    ry = dx * (h / d)

    intersections = [
        (xm + rx, ym + ry),
        (xm - rx, ym - ry),
    ]

    if 1 <= n <= len(intersections):
        px, py = intersections[n - 1]
        return Point((-px, py), name)

    return None


def parallel_point_by_distance(
    base_point: Point, line_parallel_to: Line, distance: float, name: str
) -> Point:
    vx = line_parallel_to.p2.x - line_parallel_to.p1.x
    vy = line_parallel_to.p2.y - line_parallel_to.p1.y
    norm = sqrt(vx * vx + vy * vy)
    if norm == 0:
        raise ValueError("Reference line has zero length")
    ux, uy = vx / norm, vy / norm  # unit vector along the line
    return Point((-base_point.x - distance * ux, base_point.y + distance * uy), name)


def parallel_point_by_line(
    base_point: Point, line_parallel_to: Line, line_to: Line, name: str
) -> Point | None:
    dx = line_parallel_to.p2.x - line_parallel_to.p1.x
    dy = line_parallel_to.p2.y - line_parallel_to.p1.y
    if dx == 0 and dy == 0:
        raise ValueError("line_parallel_to cannot be degenerate")

    parallel_line = Line(
        base_point,
        Point((-base_point.x - dx, base_point.y + dy), name + "_dir"),
        "temp_parallel",
    )

    return intersect_line2line(parallel_line, line_to, name)
