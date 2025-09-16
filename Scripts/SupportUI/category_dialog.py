from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QLabel, QHBoxLayout, QButtonGroup, QRadioButton
)
from Scripts.Util.colors import COLORS, ColorHex
from Scripts.Tasks.task_manager import AddCategory

class CategoryCreationWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Category")
        self.setFixedSize(300, 300)
        self.categoryId = None
        self.selectedColor = COLORS.Blue  # default color

        mainLayout = QVBoxLayout(self)

        # Name input
        mainLayout.addWidget(QLabel("Category Name:"))
        self.nameInput = QLineEdit()
        mainLayout.addWidget(self.nameInput)

        # Description input
        mainLayout.addWidget(QLabel("Description:"))
        self.descInput = QTextEdit()
        self.descInput.setFixedHeight(80)
        mainLayout.addWidget(self.descInput)

        # Predefined color selection
        mainLayout.addWidget(QLabel("Select Color:"))
        colorLayout = QHBoxLayout()
        self.colorGroup = QButtonGroup(self)
        for color_name in dir(COLORS):
            if color_name.startswith("__"):
                continue
            color_value = getattr(COLORS, color_name)
            btn = QRadioButton()
            btn.setStyleSheet(f"background-color: {color_value.hex}; min-width: 20px; min-height: 20px;")
            btn.setToolTip(color_name)
            self.colorGroup.addButton(btn)
            colorLayout.addWidget(btn)
            if color_value == self.selectedColor:
                btn.setChecked(True)
            btn.toggled.connect(lambda checked, c=color_value: self.setSelectedColor(c) if checked else None)

        mainLayout.addLayout(colorLayout)

        # Buttons
        btnLayout = QHBoxLayout()
        self.okBtn = QPushButton("Create")
        self.okBtn.clicked.connect(self.createCategory)
        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.reject)
        btnLayout.addWidget(self.okBtn)
        btnLayout.addWidget(self.cancelBtn)
        mainLayout.addLayout(btnLayout)

        self.show()

    def setSelectedColor(self, color: ColorHex):
        self.selectedColor = color

    def createCategory(self):
        name = self.nameInput.text().strip()
        description = self.descInput.toPlainText().strip()
        if name:
            self.categoryId = AddCategory(name=name, color=self.selectedColor, description=description)
            self.accept()
