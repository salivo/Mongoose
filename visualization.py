# pyright: basic
# ruff: noqa
from matplotlib.patches import Circle as CirclePatch
import matplotlib.pyplot as plt
from geometry_math import *


class Visualization:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.fig.canvas.mpl_connect("close_event", self.on_close)
        self.point_colors = "blue"
        self.text_colors = "blue"
        self.line_colors = "black"
        self.running = True

    def drawPoint(self, point: Point):
        self.ax.scatter(point.x, point.y, color=self.point_colors)
        if not point.name.startswith("_"):
            self.ax.text(
                point.x + 0.02, point.y + 0.1, point.name, color=self.text_colors
            )

    def drawLine(self, line: Line):
        if line.name in ("org_x", "org_y"):
            return
        width = 1
        style = "-"
        if line.name.startswith("_"):
            width = 0.5
        if line.name.endswith(")"):
            width = 0.5
            style = "--"
        self.ax.plot(
            [
                line.p1.x - (line.p2.x - line.p1.x) * (line.resize[0] - 1),
                line.p2.x + (line.p2.x - line.p1.x) * (line.resize[1] - 1),
            ],
            [
                line.p1.y - (line.p2.y - line.p1.y) * (line.resize[0] - 1),
                line.p2.y + (line.p2.y - line.p1.y) * (line.resize[1] - 1),
            ],
            color=self.line_colors,
            linestyle=style,
            linewidth=width,
        )

    def drawCircle(self, circle: Circle):
        self.ax.add_patch(
            CirclePatch((circle.center.x, circle.center.y), circle.radius, fill=False)
        )

    def drawAxis(self):
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.tick_params(
            left=False, bottom=False, labelleft=False, labelbottom=False
        )
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        _ = self.ax.axhline(0, color="black", linewidth=0.8)  # pyright: ignore[reportUnknownMemberType]
        _ = self.ax.scatter(0, 0, color="black")  # pyright: ignore[reportUnknownMemberType]
        _ = self.ax.text(0.03, -0.15, "0₁,₂", color="black")  # pyright: ignore[reportUnknownMemberType]

    def drawScene(self, objects):
        self.ax.clear()
        self.ax.set_aspect("equal", adjustable="box")
        self.drawAxis()
        for obj in objects.values():
            match obj:
                case Point():
                    self.drawPoint(obj)
                case Line():
                    self.drawLine(obj)
                case Circle():
                    self.drawCircle(obj)

    def sceneLoop(self):
        while self.running:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def on_close(self, event):
        self.running = False
