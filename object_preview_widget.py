from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QWidget,
)


class ObjectPreviewWidget(QWidget):
    def __init__(
        self,
        name: str,
        obj_type: str,
        parent_list: QListWidget,
        name_type: str = "",
    ):
        super().__init__()
        self.parent_list = parent_list
        self.name = name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        # Name (Bold)
        if name_type == "hidden":
            self.name_label = QLabel(name)
        else:
            self.name_label = QLabel(f"<b>{name}</b>")

        # Type (Dimmed/Grey)
        self.type_label = QLabel(obj_type)
        font = self.type_label.font()
        font.setPointSize(12)
        self.type_label.setFont(font)

        # Three Dots Button
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedWidth(20)
        self.menu_btn.setFlat(True)
        self.menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Add to layout
        layout.addWidget(self.name_label)
        layout.addStretch()  # Pushes the type and dots to the right
        layout.addWidget(self.type_label)
        layout.addWidget(self.menu_btn)

        self.menu_btn.clicked.connect(self.on_menu_click)

    def on_menu_click(self):
        print(f"Opening settings for {self.name}")
