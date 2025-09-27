import numpy as np


class Point:
    def __init__(self, cords: tuple[float, float | None, float | None], name: str):
        self.x: float = -cords[0]
        self.y1: float | None = -cords[1] if cords[1] is not None else None
        self.y2: float | None = cords[2]
        self.name: str = name

    def coords(self):
        return np.array([self.x, self.y1, self.y2])


class Line:
    def __init__(self, p1: Point, p2: Point, name: str, y_active: int = 0):
        self.p1: Point = p1
        self.p2: Point = p2
        self.name: str = name
        self.y_active: int = y_active


class Plane(Point):
    def __init__(self, cords: tuple[float, float, float], name: str):
        super().__init__(cords, name)


def foot_of_perp_2d(
    LineP1: tuple[float | None, float | None],
    LineP2: tuple[float | None, float | None],
    Point: tuple[float | None, float | None],
) -> tuple[float, float]:
    a_arr = np.asarray(LineP1, dtype=float)
    b_arr = np.asarray(LineP2, dtype=float)
    k_arr = np.asarray(Point, dtype=float)
    v = b_arr - a_arr
    vv = np.dot(v, v)  # pyright: ignore[reportAny]
    if vv == 0:
        return tuple(a_arr)
    t = np.dot(k_arr - a_arr, v) / vv  # pyright: ignore[reportAny]
    foot = a_arr + t * v  # pyright: ignore[reportAny]
    return tuple(foot)  # pyright: ignore[reportAny]


def intersect_2d(
    A1: tuple[float, float],
    A2: tuple[float, float],
    B1: tuple[float, float],
    B2: tuple[float, float],
) -> tuple[float, float] | None:
    x1, y1 = A1
    x2, y2 = A2
    x3, y3 = B1
    x4, y4 = B2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:  # Lines are parallel
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return px, py
