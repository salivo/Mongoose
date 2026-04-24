from enum import Enum
from tkinter import Variable

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QGuiApplication, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QWidget,
)
from typing_extensions import Any


class ObjectTypes(Enum):
    POINT = "Point"
    LINE = "Line"
    PLANE = "Plane"
    CIRCLE = "Circle"
    VARIABLE = "Variable"
    UNKNOWN = "Unknown"


icons = {
    ObjectTypes.POINT: "point.svg",
    ObjectTypes.LINE: "line.svg",
    ObjectTypes.PLANE: "plane.svg",
    ObjectTypes.CIRCLE: "circle.svg",
    ObjectTypes.VARIABLE: "variable.svg",
}


class ObjectPreviewType:
    def __init__(
        self, name: str, obj_type: ObjectTypes, viewstyle: str, params: Any, id: str
    ):
        self.name = name
        self.obj_type = obj_type
        self.viewstyle = viewstyle
        self.params = params
        self.id = id


class ObjectPreviewWidget(QWidget):
    def __init__(
        self,
        content: ObjectPreviewType,
        parent_list: QListWidget,
    ):
        super().__init__()
        self.parent_list = parent_list
        self.content = content
        if content.obj_type == ObjectTypes.VARIABLE:
            self.show_variable_command()
        else:
            self.show_normal_command()

    def show_normal_command(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        if self.content.obj_type == ObjectTypes.UNKNOWN:
            self.type_label = QLabel("X")
        else:
            self.type_label = QLabel()
            pixmap = get_icon(self.content.obj_type)
            self.type_label.setPixmap(pixmap)

        self.name_label = QLabel(f"<b>{self.content.name}</b>")
        # Type (Dimmed/Grey)
        self.params_label = QLabel(str(self.content.params))
        font = self.params_label.font()
        font.setPointSize(12)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.6)  # 60% visibility
        self.params_label.setGraphicsEffect(opacity_effect)
        self.params_label.setFont(font)
        # Three Dots Button
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedWidth(20)
        self.menu_btn.setFlat(True)
        self.menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Add to layout
        layout.addWidget(self.type_label)
        layout.addWidget(self.name_label)
        layout.addStretch()  # Pushes the type and dots to the right
        layout.addWidget(self.params_label)
        layout.addWidget(self.menu_btn)

        self.menu_btn.clicked.connect(self.on_menu_click)

    def show_variable_command(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        self.type_label = QLabel()
        pixmap = get_icon(self.content.obj_type)
        self.type_label.setPixmap(pixmap)
        self.value_input = QLineEdit(str(self.content.name))
        self.value_input.setStyleSheet("""
                QLineEdit {
                    border: none;
                    background: transparent;
                    /* Use the theme's text color for the underline */
                    border-bottom: 1px solid palette(placeholder-text);
                    padding-bottom: 2px;
                }
                QLineEdit:focus {
                    /* Use the theme's highlight/accent color when active */
                    border-bottom: 2px solid palette(highlight);
                }
            """)
        self.value_input.setReadOnly(True)
        layout.addWidget(self.type_label)
        layout.addWidget(self.value_input)

    def on_menu_click(self):
        print(f"Opening settings for {self.content.id}")


def get_icon(icon_name, size=24):
    try:
        svg_path = icons[icon_name]
        with open("static/icons/" + svg_path, "r") as f:
            svg_data = f.read()
        dpr = QGuiApplication.primaryScreen().devicePixelRatio()
        pixmap = QPixmap(int(size * dpr), int(size * dpr))
        pixmap.fill(Qt.GlobalColor.transparent)
        pixmap.setDevicePixelRatio(dpr)
        renderer = QSvgRenderer(svg_data.encode("utf-8"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        target_rect = QRectF(0, 0, size, size)
        renderer.render(painter, target_rect)

        painter.end()
        return pixmap
    except Exception as e:
        print(f"Warning: Could not load icon {icon_name}: {e}")
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap
