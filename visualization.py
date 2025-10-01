# pyright: basic
# ruff: noqa
from matplotlib.patches import Circle as CirclePatch
import matplotlib.pyplot as plt
from geometry_math import *


def DrawPoint(point: Point, color="blue"):
    plt.scatter(point.x, point.y, color=color)
    if not point.name.startswith("_"):
        plt.text(point.x + 0.02, point.y + 0.1, point.name, color=color)


def DrawLine(line: Line, color="black"):
    if line.name in ("org_x", "org_y"):
        return
    width = 1
    style = "-"
    if line.name.startswith("_"):
        width = 0.5
    if line.name.endswith(")"):
        width = 0.5
        style = "--"
    plt.plot(
        [
            line.p1.x - (line.p2.x - line.p1.x) * (line.resize[0] - 1),
            line.p2.x + (line.p2.x - line.p1.x) * (line.resize[1] - 1),
        ],
        [
            line.p1.y - (line.p2.y - line.p1.y) * (line.resize[0] - 1),
            line.p2.y + (line.p2.y - line.p1.y) * (line.resize[1] - 1),
        ],
        color=color,
        linestyle=style,
        linewidth=width,
    )


def DrawCircle(circle: Circle, color="blue"):
    plt.gca().add_patch(
        CirclePatch((circle.center.x, circle.center.y), circle.radius, fill=False)
    )


def DrawAxis():
    _ = plt.axhline(0, color="black", linewidth=0.8)  # pyright: ignore[reportUnknownMemberType]
    _ = plt.scatter(0, 0, color="black")  # pyright: ignore[reportUnknownMemberType]
    _ = plt.text(0.03, -0.15, "0₁,₂", color="black")  # pyright: ignore[reportUnknownMemberType]


def DrawScene(objects: dict[str, Point | Line | Circle | Plane]):
    for obj in objects:
        obj = objects.get(obj)
        match obj:
            case Point():
                DrawPoint(obj)
            case Line():
                DrawLine(obj)
            case Circle():
                DrawCircle(obj)

    plt.axis("equal")
    plt.show()
