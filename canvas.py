import math
from typing import override

from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QWheelEvent
from PyQt6.QtWidgets import QWidget

from geometry_math import Circle, Line, Point

style = {"normal": 1, "bold": 3}


class DrawingCanvas(QWidget):
    selection_changed = pyqtSignal(list)

    def __init__(self, objects):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.zoom = 1.0
        self.offset = QPointF(0.0, 0.0)

        self.a4_w_mm = 210
        self.a4_h_mm = 297
        # Conversion factor for 300 DPI (300 / 25.4)
        self.mm_to_px = 11.8110236
        self.paper_w = self.a4_w_mm * self.mm_to_px
        self.paper_h = self.a4_h_mm * self.mm_to_px
        self.padding = 10 * self.mm_to_px

        self.scale = 10
        self.hit_threshold = 0.05
        self.sensitivity = 1
        self.zoom_in_factor = 1.1

        self.objects = objects
        self.hovered_obj = None
        self.selected_objs = []
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setMouseTracking(True)

    @override
    def wheelEvent(self, a0: QWheelEvent | None):
        if a0 is None:
            return

        mouse_pos = a0.position()
        factor = (
            self.zoom_in_factor if a0.angleDelta().y() > 0 else 1 / self.zoom_in_factor
        )
        center = QPointF(self.width() / 2, self.height() / 2)
        relative_pos = mouse_pos - (center + self.offset)
        self.offset -= relative_pos * (factor - 1)
        self.zoom *= factor
        self.update()
        a0.accept()

    @override
    def mousePressEvent(self, a0):
        if a0 is None:
            return
        if a0.button() == Qt.MouseButton.MiddleButton:
            self.last_mouse_pos = a0.position()
        if a0.button() == Qt.MouseButton.LeftButton:
            if self.hovered_obj is not None:
                if a0.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.selected_objs.append(self.hovered_obj)
                else:
                    self.selected_objs.clear()
                    self.selected_objs.append(self.hovered_obj)
            else:
                self.selected_objs.clear()
        self.selection_changed.emit(self.selected_objs)
        self.update()
        a0.accept()

    @override
    def mouseMoveEvent(self, a0):
        if a0 is None:
            return
        if a0.buttons() & Qt.MouseButton.MiddleButton:
            current_pos = a0.position()
            delta = current_pos - self.last_mouse_pos
            self.offset += delta * self.sensitivity
            self.last_mouse_pos = current_pos
            self.update()
            a0.accept()
            return
        logical_pos = self.map_to_logical(a0.position())
        self.check_mouse_hover(logical_pos.x(), logical_pos.y())

    def check_mouse_hover(self, px, py):
        best_match = None
        best_dist = float("inf")
        hit_threshold = self.hit_threshold * self.mm_to_px / (self.scale * self.zoom)
        for key, obj in self.objects.items():
            dist = float("inf")
            if isinstance(obj, Point):
                dist = (
                    math.hypot(px - obj.x, py - obj.y) - self.hit_threshold
                )  # Adjusted becose point harder to hit
            elif isinstance(obj, Line):
                dist = self.dist_point_to_line(
                    px, py, obj.p1.x, obj.p1.y, obj.p2.x, obj.p2.y
                )
            elif isinstance(obj, Circle):
                dist_to_center = math.hypot(px - obj.center.x, py - obj.center.y)
                dist_to_edge = abs(dist_to_center - obj.radius)
                if dist_to_edge <= hit_threshold:
                    mouse_angle = math.degrees(
                        math.atan2(py - obj.center.y, px - obj.center.x)
                    )
                    if obj.draw_from and obj.draw_span:
                        mouse_angle %= 360
                        start = obj.draw_from % 360
                        diff = (mouse_angle - start) % 360

                        if diff <= obj.draw_span:
                            dist = dist_to_edge
                        else:
                            dist = float("inf")
                    else:
                        dist = dist_to_edge

            if dist <= hit_threshold and dist < best_dist:
                best_match = key
                best_dist = dist
        if self.hovered_obj != best_match:
            self.hovered_obj = best_match
            self.update()

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
        for key, obj in self.objects.items():
            is_hovered = key == self.hovered_obj or key in self.selected_objs
            if isinstance(obj, Line):
                if obj.name == "org_x" or obj.name == "org_y":
                    continue
                self.draw_line(painter, obj, is_hovered)
            elif isinstance(obj, Circle):
                self.draw_circle(painter, obj, is_hovered)
            # elif isinstance(obj, Plane):
            #     self.draw_plane(obj)

        for key, obj in self.objects.items():
            is_hovered = key == self.hovered_obj or key in self.selected_objs
            if isinstance(obj, Point):
                self.draw_point(painter, obj, is_hovered)

    def draw_point(self, painter: QPainter, point: Point, is_hovered: bool):
        color = QColor(255, 165, 0) if is_hovered else QColor(0, 0, 255)
        thickness = 0.8 * self.mm_to_px if is_hovered else 0.5 * self.mm_to_px
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPoint(
            QPointF(
                point.x * self.scale * self.mm_to_px,
                -point.y * self.scale * self.mm_to_px,
            )
        )

    def draw_line(self, painter: QPainter, line: Line, is_hovered: bool):
        color = QColor(255, 165, 0) if is_hovered else QColor(0, 0, 0)
        thickness = style[line.style] + 0.5 if is_hovered else style[line.style]
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(
            int(line.p1.x * self.scale * self.mm_to_px),
            -int(line.p1.y * self.scale * self.mm_to_px),
            int(line.p2.x * self.scale * self.mm_to_px),
            -int(line.p2.y * self.scale * self.mm_to_px),
        )

    def draw_circle(self, painter: QPainter, circle: Circle, is_hovered: bool):
        color = QColor(255, 165, 0) if is_hovered else QColor(0, 0, 0)
        thickness = 1.5 if is_hovered else 1
        pen = QPen(color, thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        draw_from = 0
        span = 360 * 16
        if circle.draw_from:
            draw_from = (circle.draw_from) * 16
        if circle.draw_span:
            span = circle.draw_span * 16
        painter.drawArc(
            int((circle.center.x - circle.radius) * self.scale * self.mm_to_px),
            -int((circle.center.y + circle.radius) * self.scale * self.mm_to_px),
            int(2 * circle.radius * self.scale * self.mm_to_px),
            int(2 * circle.radius * self.scale * self.mm_to_px),
            int(draw_from),
            int(span),
        )

    def map_to_logical(self, pos: QPointF) -> QPointF:
        center_x = self.width() / 2 + self.offset.x()
        center_y = self.height() / 2 + self.offset.y()
        # Reverse translation and zoom
        logical_x = (pos.x() - center_x) / self.zoom
        logical_y = -(pos.y() - center_y) / self.zoom
        # Reverse scale
        return QPointF(
            logical_x / (self.scale * self.mm_to_px),
            logical_y / (self.scale * self.mm_to_px),
        )

    def dist_point_to_line(self, px, py, x1, y1, x2, y2):
        l2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if l2 == 0:
            return math.hypot(px - x1, py - y1)

        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return math.hypot(px - proj_x, py - proj_y)
