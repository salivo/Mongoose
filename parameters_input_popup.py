from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class PointSetParamsPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Point Settings")
        self.setModal(True)  # Blocks input to the main window while open
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        # Set up a layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(QLabel("X"))
        self.x_input = QDoubleSpinBox()
        self.x_input.setRange(float("-inf"), float("inf"))
        self.x_input.setDecimals(2)
        self.x_input.setValue(1.0)
        layout.addWidget(self.x_input)
        layout.addWidget(QLabel("Y"))
        self.y_input = QDoubleSpinBox()
        self.y_input.setRange(float("-inf"), float("inf"))
        self.y_input.setDecimals(2)
        self.y_input.setValue(1.0)
        layout.addWidget(self.y_input)
        layout.addWidget(QLabel("Z"))
        self.z_input = QDoubleSpinBox()
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
