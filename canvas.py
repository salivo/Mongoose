from typing import override

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from geometry_math import Circle, Line, Plane, Point


class DrawingCanvas(QWidget):
    def __init__(self, objects):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.zoom = 1.0
        self.offset = QPointF(0.0, 0.0)

        self.a4_w_mm = 210
        self.a4_h_mm = 297
        # Conversion factor (e.g., 3.78 pixels per mm for ~96 DPI)
        self.mm_to_px = 3.78
        self.paper_w = self.a4_w_mm * self.mm_to_px
        self.paper_h = self.a4_h_mm * self.mm_to_px

        self.scale = 10

        self.padding = 10 * self.mm_to_px

        self.objects = objects

    @override
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fill the "Workspace" background
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        # Move to center and apply zoom
        painter.translate(
            self.width() / 2 + self.offset.x(), self.height() / 2 + self.offset.y()
        )
        painter.scale(self.zoom, self.zoom)

        # Draw the A4 "Paper" surface
        paper_rect = QPointF(-self.paper_w / 2, -self.paper_h / 2)
        painter.fillRect(
            int(paper_rect.x()),
            int(paper_rect.y()),
            int(self.paper_w),
            int(self.paper_h),
            QColor(255, 255, 255),
        )

        # Draw a shadow or border for the paper
        pen = QPen(QColor(0, 0, 0), 1 / self.zoom)
        painter.setPen(pen)
        painter.drawRect(
            int(paper_rect.x()),
            int(paper_rect.y()),
            int(self.paper_w),
            int(self.paper_h),
        )

        # Draw axis
        pen = QPen(QColor(255, 0, 0), 0.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.drawLine(
            int(-self.paper_w / 2 + self.padding),
            0,
            int(self.paper_w / 2 - self.padding),
            0,
        )
        # Draw all objects
        self.draw_objects(painter)

    def draw_objects(self, painter: QPainter):
        for obj in self.objects.values():
            if isinstance(obj, Point):
                self.draw_point(painter, obj)
            elif isinstance(obj, Line):
                self.draw_line(painter, obj)
            # elif isinstance(obj, Circle):
            #     self.draw_circle(obj)
            # elif isinstance(obj, Plane):
            #     self.draw_plane(obj)

    def draw_point(self, painter: QPainter, point: Point):
        pen = QPen(QColor(0, 0, 255), 5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPoint(QPointF(point.x * self.scale, point.y * self.scale))

    def draw_line(self, painter: QPainter, line: Line):
        pen = QPen(QColor(0, 0, 0), 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(
            int(line.p1.x * self.scale),
            int(line.p1.y * self.scale),
            int(line.p2.x * self.scale),
            int(line.p2.y * self.scale),
        )
