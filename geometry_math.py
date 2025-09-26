import numpy as np

class Point:
    def __init__(self, cords: tuple[float, float | None, float | None], name: str):
        self.x:float = -cords[0]
        self.y1:float|None = -cords[1] if cords[1] is not None else None
        self.y2:float|None = cords[2]
        self.name:str = name

    def coords(self):
        return np.array([self.x, self.y1, self.y2])

class Line:
    def __init__(self, p1: Point, p2: Point, name: str):
        self.p1:Point = p1
        self.p2:Point = p2
        self.name:str = name

class Plane(Point):
    def __init__(self, cords: tuple[float, float, float], name: str):
        super().__init__(cords, name)

def foot_of_perp_2d(
    LineP1: tuple[float|None, float|None],
    LineP2: tuple[float|None, float|None],
    Point: tuple[float|None, float|None]
)-> tuple[float, float]:
    a_arr = np.asarray(LineP1, dtype=float)
    b_arr = np.asarray(LineP2, dtype=float)
    k_arr = np.asarray(Point, dtype=float)
    v = b_arr - a_arr
    vv = np.dot(v, v)
    if vv == 0:
        return tuple(a_arr)
    t = np.dot(k_arr - a_arr, v) / vv
    foot = a_arr + t * v
    return tuple(foot)
