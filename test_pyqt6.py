from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QResizeEvent, QWheelEvent
import sys

class ZoomableView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.zoom_scene: QGraphicsScene = scene
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.current_scale: float = 1.0
        self.min_scale: float = 1.0
        self.max_scale: float = 10.0

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        new_scale = self.current_scale * factor

        # Only apply if within limits
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale(factor, factor)
            self.current_scale = new_scale

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        view = self.viewport()
        if view is None:
            return
        self.zoom_scene.setSceneRect(-view.width()/2, -view.height()/2, view.width(), view.height())
        if hasattr(self, 'h_axis'):
            self.h_axis.setLine(-w/2, 0, w/2, 0)

app = QApplication(sys.argv)

scene = QGraphicsScene()

ellipse = QGraphicsEllipseItem(QRectF(0, 0, 10, 10))
ellipse.setBrush(QBrush(QColor("red")))
ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
scene.addItem(ellipse)
ellipse = QGraphicsEllipseItem(QRectF(500, 500, 100, 50))
ellipse.setBrush(QBrush(QColor("green")))
ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
ellipse.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
scene.addItem(ellipse)

view = ZoomableView(scene)
view.showMaximized()

sys.exit(app.exec())
