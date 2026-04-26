import math
from typing import override

from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QWheelEvent
from PyQt6.QtWidgets import QWidget

from geometry_math import Circle, Line, Point

style = {"normal": 0.2, "bold": 0.6}
type = {
    "construct": Qt.PenStyle.SolidLine,
    "hidden": Qt.PenStyle.DashLine,
    "realsized": Qt.PenStyle.DashDotLine,
    "none": Qt.PenStyle.NoPen,
}


class DrawingCanvas(QWidget):
    selection_changed = pyqtSignal(list)
    resize_confirmed = pyqtSignal(str, float, float)

    def __init__(self, objects):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.zoom = 0.2
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
        self.last_mouse_widget_pos = None
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setMouseTracking(True)

        # Resize mode state
        self.resize_mode = False
        self.resize_line_key = None
        self.resize_preview = (0.0, 1.0)  # (r1, r2) t-parameters
        self.resize_side = 'end'           # which endpoint is being dragged

    @override
    def wheelEvent(self, a0: QWheelEvent | None):
        if a0 is None:
            return

        mouse_pos = a0.position()
        delta = a0.angleDelta().y()
        if delta == 0:
            return

        # On Linux, touchpads usually emit pixelDelta() whereas normal mice do not.
        # We invert the delta if pixelDelta is present (indicating a touchpad).
        if not a0.pixelDelta().isNull():
            delta = -delta

        # A standard mouse wheel step is 120. For touchpads, the delta is smaller but more frequent.
        # Scale the zoom factor proportionally to the delta for smooth zooming on all devices.
        factor = (self.zoom_in_factor) ** (delta / 120.0)
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
        # In resize mode, left click confirms the new resize
        if self.resize_mode and a0.button() == Qt.MouseButton.LeftButton:
            if self.resize_line_key:
                r1, r2 = self.resize_preview
                self.resize_confirmed.emit(self.resize_line_key, r1, r2)
            self.resize_mode = False
            self.resize_line_key = None
            self.update()
            a0.accept()
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
    def mouseDoubleClickEvent(self, a0):
        if a0 is None:
            return
        print("Double click detected on the canvas!")
        if a0.button() == Qt.MouseButton.LeftButton:
            if self.hovered_obj is not None:
                print(f"Double-clicked on object key: {self.hovered_obj}")
        a0.accept()

    @override
    def mouseMoveEvent(self, a0):
        if a0 is None:
            return
        self.last_mouse_widget_pos = a0.position()
        if a0.buttons() & Qt.MouseButton.MiddleButton:
            current_pos = a0.position()
            delta = current_pos - self.last_mouse_pos
            self.offset += delta * self.sensitivity
            self.last_mouse_pos = current_pos
            self.update()
            a0.accept()
            return

        # Resize mode: compute extension on the active side only
        if self.resize_mode and self.resize_line_key:
            line = self.objects.get(self.resize_line_key)
            if isinstance(line, Line):
                logical = self.map_to_logical(a0.position())
                mx, my = logical.x(), logical.y()
                dx = line.p2.x - line.p1.x
                dy = line.p2.y - line.p1.y
                l2 = dx * dx + dy * dy
                if l2 > 0:
                    t = ((mx - line.p1.x) * dx + (my - line.p1.y) * dy) / l2
                    r1, r2 = self.resize_preview
                    if self.resize_side == 'end':
                        r2 = round(t, 4)
                    else:
                        r1 = round(t, 4)
                    self.resize_preview = (r1, r2)
                self.update()
            return

        logical_pos = self.map_to_logical(a0.position())
        self.check_mouse_hover(logical_pos.x(), logical_pos.y())

    def check_mouse_hover(self, px, py):
        best_match = None
        best_dist = float("inf")
        hit_threshold = self.hit_threshold * self.mm_to_px / (self.scale * self.zoom)
        for key, obj in self.objects.items():
            # Skip invisible objects from hover detection (but never skip axes)
            if (hasattr(obj, 'type') and obj.type == 'none' or getattr(obj, 'hidden', False)) and getattr(obj, 'name', '') not in ('org_x', 'org_y'):
                continue
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

        # Draw all objects
        self.draw_objects(painter)

    def draw_objects(self, painter: QPainter):
        for key, obj in self.objects.items():
            # Skip invisible objects from rendering (but never skip axes)
            if (hasattr(obj, 'type') and obj.type == 'none' or getattr(obj, 'hidden', False)) and getattr(obj, 'name', '') not in ('org_x', 'org_y'):
                continue
            is_hovered = key == self.hovered_obj or key in self.selected_objs
            if isinstance(obj, Line):
                if obj.name in ("org_x", "org_y"):
                    self.draw_axis(painter, obj, is_hovered)
                else:
                    self.draw_line(painter, obj, is_hovered)
            elif isinstance(obj, Circle):
                self.draw_circle(painter, obj, is_hovered)

        for key, obj in self.objects.items():
            # Skip invisible objects from rendering (but never skip axes)
            if (hasattr(obj, 'type') and obj.type == 'none' or getattr(obj, 'hidden', False)) and getattr(obj, 'name', '') not in ('org_x', 'org_y'):
                continue
            is_hovered = key == self.hovered_obj or key in self.selected_objs
            if isinstance(obj, Point):
                self.draw_point(painter, obj, is_hovered)

        # Draw resize mode preview overlay
        if self.resize_mode and self.resize_line_key:
            line = self.objects.get(self.resize_line_key)
            if isinstance(line, Line):
                r1, r2 = self.resize_preview
                dx = line.p2.x - line.p1.x
                dy = line.p2.y - line.p1.y
                sc = self.scale * self.mm_to_px
                sx = int((line.p1.x + r1 * dx) * sc)
                sy = -int((line.p1.y + r1 * dy) * sc)
                ex = int((line.p1.x + r2 * dx) * sc)
                ey = -int((line.p1.y + r2 * dy) * sc)

                # Draw blue preview line
                preview_pen = QPen(QColor(30, 120, 255, 200),
                                   (style.get(line.style, 0.2) + 0.2) * self.mm_to_px)
                preview_pen.setStyle(Qt.PenStyle.DashLine)
                preview_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(preview_pen)
                painter.drawLine(sx, sy, ex, ey)

                # Draw small dots at the ORIGINAL p1 and p2 positions for reference
                orig_pen = QPen(QColor(30, 120, 255, 160), 0.6 * self.mm_to_px)
                orig_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(orig_pen)
                painter.drawPoint(int(line.p1.x * sc), -int(line.p1.y * sc))
                painter.drawPoint(int(line.p2.x * sc), -int(line.p2.y * sc))

    def draw_axis(self, painter: QPainter, line: Line, is_hovered: bool):
        base_color = QColor(200, 50, 50) if line.name == "org_x" else QColor(0, 165, 255)
        color = QColor(255, 165, 0) if is_hovered else base_color
        thickness = 0.5 if is_hovered else 0.3
        pen = QPen(color, thickness * self.mm_to_px)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(
            int(line.p1.x * self.scale * self.mm_to_px),
            -int(line.p1.y * self.scale * self.mm_to_px),
            int(line.p2.x * self.scale * self.mm_to_px),
            -int(line.p2.y * self.scale * self.mm_to_px),
        )

    def draw_point(self, painter: QPainter, point: Point, is_hovered: bool):
        color = QColor(255, 165, 0) if is_hovered else QColor(0, 0, 255)
        thickness = 0.8 if is_hovered else 0.5
        pen = QPen(color, thickness * self.mm_to_px)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        pt = QPointF(
            point.x * self.scale * self.mm_to_px,
            -point.y * self.scale * self.mm_to_px,
        )
        painter.drawPoint(pt)

        # Draw point name
        mapped = painter.transform().map(pt)
        painter.save()
        painter.resetTransform()
        text_pen = QPen(color)
        painter.setPen(text_pen)
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(mapped + QPointF(6, -6), point.name)
        painter.restore()

    def draw_line(self, painter: QPainter, line: Line, is_hovered: bool):
        color = QColor(255, 165, 0) if is_hovered else QColor(0, 0, 0)
        thickness = style[line.style] + 0.2 if is_hovered else style[line.style]
        pen = QPen(color, thickness * self.mm_to_px)
        pen.setStyle(type[line.type])
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        # Apply visual resize (t-parameters along p1→p2)
        r1, r2 = getattr(line, 'resize', (0.0, 1.0))
        dx = line.p2.x - line.p1.x
        dy = line.p2.y - line.p1.y
        sc = self.scale * self.mm_to_px
        painter.drawLine(
            int((line.p1.x + r1 * dx) * sc),
            -int((line.p1.y + r1 * dy) * sc),
            int((line.p1.x + r2 * dx) * sc),
            -int((line.p1.y + r2 * dy) * sc),
        )

        if is_hovered and self.last_mouse_widget_pos and line.name not in ("org_x", "org_y"):
            painter.save()
            painter.resetTransform()
            text_pen = QPen(QColor(255, 165, 0))
            painter.setPen(text_pen)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(self.last_mouse_widget_pos + QPointF(10, -10), line.name)
            painter.restore()

    def draw_circle(self, painter: QPainter, circle: Circle, is_hovered: bool):
        color = QColor(255, 165, 0) if is_hovered else QColor(0, 0, 0)
        thickness = style[circle.style] + 0.2 if is_hovered else style[circle.style]
        pen = QPen(color, thickness * self.mm_to_px)
        pen.setStyle(type[circle.type])
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

        if is_hovered and self.last_mouse_widget_pos:
            painter.save()
            painter.resetTransform()
            text_pen = QPen(QColor(255, 165, 0))
            painter.setPen(text_pen)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(self.last_mouse_widget_pos + QPointF(10, -10), circle.name)
            painter.restore()

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
