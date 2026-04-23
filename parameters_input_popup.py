from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class NullableSpinBox(QDoubleSpinBox):
    _NULL_STYLE = "QDoubleSpinBox { color: gray; font-style: italic; }"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_null = False

    def is_null(self) -> bool:
        return self._is_null

    def set_null(self, null: bool):
        self._is_null = null
        if null:
            self.setReadOnly(True)
            self.lineEdit().setText("None")
            self.setStyleSheet(self._NULL_STYLE)
        else:
            self.setReadOnly(False)
            self.lineEdit().setText(self.textFromValue(self.value()))
            self.setStyleSheet("")

    def keyPressEvent(self, event):
        if event is not None and event.text() == "?":
            self.set_null(not self._is_null)
            return
        super().keyPressEvent(event)


class PointSetParamsPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Point Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("X"))
        self.x_input = QDoubleSpinBox()
        self.x_input.setRange(float("-inf"), float("inf"))
        self.x_input.setDecimals(2)
        self.x_input.setValue(1.0)
        layout.addWidget(self.x_input)

        layout.addWidget(QLabel("Y"))
        self.y_input = NullableSpinBox()
        self.y_input.setRange(float("-inf"), float("inf"))
        self.y_input.setDecimals(2)
        self.y_input.setValue(1.0)
        layout.addWidget(self.y_input)

        layout.addWidget(QLabel("Z"))
        self.z_input = NullableSpinBox()
        self.z_input.setRange(float("-inf"), float("inf"))
        self.z_input.setDecimals(2)
        self.z_input.setValue(1.0)
        layout.addWidget(self.z_input)

        layout.addWidget(QLabel("Point Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)

        buttons = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)

        self.x_input.setFocus()
        self.x_input.selectAll()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def get_y(self):
        return None if self.y_input.is_null() else self.y_input.value()

    def get_z(self):
        return None if self.z_input.is_null() else self.z_input.value()

    def validate_input(self, text):
        if text.strip():
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)


class LineSetParamsPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Line Settings")
        self.setModal(True)  # Blocks input to the main window while open
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Point Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        buttons = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.name_input.setFocus()
        self.name_input.selectAll()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        if text.strip():
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)


class NameOnlyPopup(QDialog):
    """Generic popup that only asks for a name. Used by footToLine."""

    def __init__(self, title="Settings", label="Name:", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.name_input.setFocus()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        self.ok_button.setEnabled(bool(text.strip()))


class CreateCirclePopup(QDialog):
    """Popup for createCircle: asks for radius and name. Point selected on canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Circle Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Radius:"))
        self.radius_input = QDoubleSpinBox()
        self.radius_input.setRange(0.0001, float("inf"))
        self.radius_input.setDecimals(4)
        self.radius_input.setValue(1.0)
        layout.addWidget(self.radius_input)
        layout.addWidget(QLabel("Circle Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.radius_input.setFocus()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        self.ok_button.setEnabled(bool(text.strip()))


class CreatePlanePopup(QDialog):
    """Popup for createPlane: asks for x coordinate, y1 and y2 (or string labels), and name."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plane Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("X coordinate:"))
        self.x_input = QDoubleSpinBox()
        self.x_input.setRange(float("-inf"), float("inf"))
        self.x_input.setDecimals(2)
        self.x_input.setValue(0.0)
        layout.addWidget(self.x_input)
        layout.addWidget(QLabel("Y1 (value or label):"))
        self.y1_input = QLineEdit()
        self.y1_input.setPlaceholderText("e.g. 5 or 'top'")
        layout.addWidget(self.y1_input)
        layout.addWidget(QLabel("Y2 (value or label):"))
        self.y2_input = QLineEdit()
        self.y2_input.setPlaceholderText("e.g. -5 or 'bottom'")
        layout.addWidget(self.y2_input)
        layout.addWidget(QLabel("Plane Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.x_input.setFocus()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        self.ok_button.setEnabled(bool(text.strip()))

    def get_coords(self):
        """Return (x, y1, y2) with y values as float if possible, else str."""
        x = self.x_input.value()
        y1_text = self.y1_input.text().strip()
        y2_text = self.y2_input.text().strip()
        try:
            y1 = float(y1_text) if y1_text else None
        except ValueError:
            y1 = y1_text if y1_text else None
        try:
            y2 = float(y2_text) if y2_text else None
        except ValueError:
            y2 = y2_text if y2_text else None
        return (x, y1, y2)


class PerpFromPointPopup(QDialog):
    """Popup for createPerpFromPoint: asks for distance and name. Point+Line selected on canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Perpendicular Point Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Distance:"))
        self.distance_input = QDoubleSpinBox()
        self.distance_input.setRange(float("-inf"), float("inf"))
        self.distance_input.setDecimals(4)
        self.distance_input.setValue(1.0)
        layout.addWidget(self.distance_input)
        layout.addWidget(QLabel("Point Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.distance_input.setFocus()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        self.ok_button.setEnabled(bool(text.strip()))


class IntersectPopup(QDialog):
    """Popup for intersect: asks for name and intersection index n. Objects selected on canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Intersect Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Point Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Solution index (n):"))
        self.n_input = QSpinBox()
        self.n_input.setRange(1, 2)
        self.n_input.setValue(1)
        layout.addWidget(self.n_input)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.name_input.setFocus()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        self.ok_button.setEnabled(bool(text.strip()))


class ParallelPopup(QDialog):
    """Popup for parallel: asks for offset (distance or object name) and result name.
    base_point + line selected on canvas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parallel Point Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Offset (distance or line name):"))
        self.offset_input = QLineEdit()
        self.offset_input.setPlaceholderText("e.g. 2.5 or 'lineA'")
        layout.addWidget(self.offset_input)
        layout.addWidget(QLabel("Point Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self.validate_input)
        layout.addWidget(self.name_input)
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.button_box)
        self.offset_input.setFocus()
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

    def validate_input(self, text):
        self.ok_button.setEnabled(bool(text.strip()))

    def get_offset(self):
        """Return offset as float if possible, else as string (object name)."""
        text = self.offset_input.text().strip()
        try:
            return float(text)
        except ValueError:
            return text


class VisibilityPopup(QDialog):
    """Popup for setting type and style of lines/circles."""

    def __init__(self, initial_type=None, initial_style=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visibility Settings")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Style Row
        style_layout = QHBoxLayout()
        style_lbl = QLabel("Style")
        style_lbl.setFixedWidth(40)
        style_layout.addWidget(style_lbl)
        
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        style_layout.addWidget(sep1)

        self.style_group = QButtonGroup(self)
        self.style_btns = {}
        for s in ["normal", "bold"]:
            btn = QPushButton(s.capitalize())
            btn.setCheckable(True)
            self.style_group.addButton(btn)
            style_layout.addWidget(btn)
            self.style_btns[s] = btn
            if initial_style == s:
                btn.setChecked(True)
        layout.addLayout(style_layout)

        # Type Row
        type_layout = QHBoxLayout()
        type_lbl = QLabel("Type")
        type_lbl.setFixedWidth(40)
        type_layout.addWidget(type_lbl)
        
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        type_layout.addWidget(sep2)

        self.type_group = QButtonGroup(self)
        self.type_btns = {}
        for t in ["construct", "hidden", "realsized", "none"]:
            btn = QPushButton(t.capitalize())
            btn.setCheckable(True)
            self.type_group.addButton(btn)
            type_layout.addWidget(btn)
            self.type_btns[t] = btn
            if initial_type == t:
                btn.setChecked(True)
        layout.addLayout(type_layout)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setStyleSheet("""
            QPushButton:checked {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                font-weight: bold;
                border: 2px solid palette(highlight);
                border-radius: 4px;
            }
            QPushButton {
                padding: 5px 10px;
            }
        """)

        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)
        
        # Set focus to the first style button instead of the OK button
        if self.style_btns:
            # Try to grab focus on the currently checked one, otherwise the first
            focused_btn = next((b for b in self.style_btns.values() if b.isChecked()), self.style_btns["normal"])
            focused_btn.setFocus()


    def get_style(self):
        for s, btn in self.style_btns.items():
            if btn.isChecked():
                return s
        return None

    def get_type(self):
        for t, btn in self.type_btns.items():
            if btn.isChecked():
                return t
        return None
