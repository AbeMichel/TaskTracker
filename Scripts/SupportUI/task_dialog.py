from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from Scripts.Tasks.task_manager import CATEGORIES, CreateTask
from Scripts.SupportUI.category_dialog import CategoryCreationWindow

class TaskCreationWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Task")

        self.layout = QVBoxLayout(self)

        # Task name input
        self.layout.addWidget(QLabel("Task Name:"))
        self.taskNameInput = QLineEdit()
        self.layout.addWidget(self.taskNameInput)

        # Category selection
        self.layout.addWidget(QLabel("Category:"))
        self.categorySelector = QComboBox()
        self.categoryIds = []
        for catId, catData in CATEGORIES.items():
            self.categorySelector.addItem(catData["Name"])
            self.categoryIds.append(catId)
        self.categorySelector.addItem("New Category")
        self.categorySelector.activated.connect(self.categorySelected)
        self.layout.addWidget(self.categorySelector)

        # Duration input (optional)
        self.layout.addWidget(QLabel("Duration (minutes, optional):"))
        self.durationInput = QLineEdit()
        self.durationInput.setPlaceholderText("Leave empty for unlimited")
        self.layout.addWidget(self.durationInput)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.createBtn = QPushButton("Create")
        self.createBtn.clicked.connect(self.createTask)
        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.reject)
        buttonLayout.addWidget(self.createBtn)
        buttonLayout.addWidget(self.cancelBtn)
        self.layout.addLayout(buttonLayout)
        self.adjustSize()

    def addCategory(self):
        dialog = CategoryCreationWindow(self)
        if dialog.exec():
            count = self.categorySelector.count() - 1
            index = max(count, 0)
            self.categorySelector.insertItem(index, CATEGORIES[dialog.categoryId]["Name"])
            self.categoryIds.append(dialog.categoryId)
            self.categorySelector.setCurrentIndex(max(count, 0))
        else:
            self.categorySelector.setCurrentIndex(0)

    def categorySelected(self, text):
        if self.categorySelector.currentIndex() == self.categorySelector.count() - 1:
            self.addCategory()

    def createTask(self):
        name = self.taskNameInput.text().strip()
        if not name:
            return  # you could also show a warning

        # Get selected category
        index = self.categorySelector.currentIndex()
        categoryId = self.categoryIds[index]

        # Parse duration
        duration_text = self.durationInput.text().strip()
        duration_ms = 0
        if duration_text:
            try:
                duration_min = float(duration_text)
                duration_ms = int(duration_min * 60 * 1000)  # convert to milliseconds
            except ValueError:
                duration_ms = 0

        # Create the task
        self.newTask = CreateTask(name, categoryId, duration_ms)

        # Close dialog with success
        self.accept()
