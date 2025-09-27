# pyright: basic
# ruff: noqa
import matplotlib.pyplot as plt
from geometry_math import *


def DrawPoint(point: Point, color="blue"):
    show_name = not point.name.startswith("_")

    if point.y1 == point.y2 and point.y1 is not None:
        plt.scatter(point.x, point.y1, color=color)
        if show_name:
            plt.text(point.x + 0.02, point.y1 + 0.1, point.name + "₁,₂", color=color)
        return

    if point.y1 is not None:
        plt.scatter(point.x, point.y1, color=color)
        if show_name:
            plt.text(point.x + 0.02, point.y1 + 0.1, point.name + "₁", color=color)

    if point.y2 is not None:
        plt.scatter(point.x, point.y2, color=color)
        if show_name:
            plt.text(point.x + 0.02, point.y2 + 0.1, point.name + "₂", color=color)


def DrawLine(line: Line, color="black"):
    width = 1
    style = "-"
    if line.name.startswith("_"):
        width = 0.5
    if line.name.endswith(")"):
        width = 0.5
        style = "--"
    if line.p1.y1 is not None and line.p2.y1 is not None:
        if line.y_active in (0, 1):
            plt.plot(
                [line.p1.x, line.p2.x],
                [line.p1.y1, line.p2.y1],
                color=color,
                linestyle=style,
                linewidth=width,
            )
    if line.p1.y2 is not None and line.p2.y2 is not None:
        if (line.p1.y1 != line.p1.y2) or (line.p2.y1 != line.p2.y2):
            if line.y_active in (0, 2):
                plt.plot(
                    [line.p1.x, line.p2.x],
                    [line.p1.y2, line.p2.y2],
                    color=color,
                    linestyle=style,
                    linewidth=width,
                )


# def DrawPlane(point: Plane, color="green"):
#     plt.scatter(point.x, 0, color=color)
#     plt.text(point.x + 0.02, 0.1, point.name + "₀", color=color)

#     plt.scatter(0, point.y1, color=color)
#     plt.text(0 + 0.02, point.y1 + 0.1, point.name + "₁", color=color)

#     plt.scatter(0, point.y2, color=color)
#     plt.text(0.02, point.y2 + 0.1, point.name + "₂", color=color)


def DrawAxis():
    _ = plt.axhline(0, color="black", linewidth=0.8)  # pyright: ignore[reportUnknownMemberType]
    _ = plt.scatter(0, 0, color="black")  # pyright: ignore[reportUnknownMemberType]
    _ = plt.text(0.03, -0.15, "0₁,₂", color="black")  # pyright: ignore[reportUnknownMemberType]


def DrawScene():
    plt.axis("equal")
    plt.show()
