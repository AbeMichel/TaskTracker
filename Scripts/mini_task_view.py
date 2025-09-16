# The window in the bottom right
from Scripts.SupportUI.task_timer import TaskTimerBar
from Scripts.Util.app_constructer import App
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from Scripts.Tasks.task import Task
from Scripts.Tasks.task_manager import GetCategory, GetTasks
from Scripts.SupportUI.task_dialog import TaskCreationWindow
WIDTH = 400
HEIGHT = 200

MENU_BAR_HEIGHT = 20

INACTIVITY_MS = 3000
FADE_DURATION_MS = 800

class MiniTaskView(QWidget):
    requestLargeView = pyqtSignal()
    requestSystemTray = pyqtSignal()
    def __init__(self, show=True):
        super().__init__()
        self.setWindowTitle("Task Viewer")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(WIDTH, 50)

        self._dragActive = False
        self._dragOffset = None

        self.mainLayout = QVBoxLayout(self)

        self.taskLayout = QVBoxLayout()
        # self.taskLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)
        self.mainLayout.addLayout(self.taskLayout)
        self.activeTask = None  # track active task

        self.menu_bar = self.buildMenuBar()
        self.mainLayout.addWidget(self.menu_bar)

        if show:
            self.show()

    def adjustSizeAndPosition(self):
        screenGeom = QApplication.primaryScreen().availableGeometry()
        self.adjustSize()  # recalc size based on layout
        x = screenGeom.right() - self.width() - 10  # 10px margin from right
        y = screenGeom.bottom() - self.height() - MENU_BAR_HEIGHT - 10  # 10px margin from bottom
        self.move(x, y)

    def buildMenuBar(self):
        menu_bar = QWidget(self)
        menu_bar.setFixedHeight(MENU_BAR_HEIGHT)
        layout = QHBoxLayout(menu_bar)
        layout.setContentsMargins(5, 0, 5, 0)

        newTaskBtn = QPushButton("New", menu_bar)
        newTaskBtn.clicked.connect(self.createNewTask)
        layout.addWidget(newTaskBtn)

        maximizeBtn = QPushButton("Maximize", menu_bar)
        maximizeBtn.clicked.connect(lambda: self.requestLargeView.emit())
        layout.addWidget(maximizeBtn)

        close_btn = QPushButton("Close", menu_bar)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        menu_bar.hide()
        return menu_bar
    
    def createNewTask(self):
        dialog = TaskCreationWindow(self)
        if dialog.exec():
            # Task has already been added inside the dialog
            self.addTask(dialog.newTask, False)
            QTimer.singleShot(10, self.adjustSize)


    def addTask(self, task, adjust):
        taskBar = TaskTimerBar(parent=self, task=task)
        self.taskLayout.addWidget(taskBar)
        if adjust:
            QTimer.singleShot(10, self.adjustSizeAndPosition)


    def setActiveTask(self, task: Task):
        # Deactivate previous
        if self.activeTask:
            self.activeTask.setFocused(False)
        # Activate new
        if task is not None:
            task.setFocused(True)
        self.activeTask = task

    def enterEvent(self, event):
        self.menu_bar.show()
        self.adjustSize()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.menu_bar.hide()
        self.adjustSize()
        super().leaveEvent(event)

    def mousePressEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            self._dragActive = True
            self._dragOffset = a0.globalPosition().toPoint() - self.frameGeometry().topLeft()
        return super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0):
        if self._dragActive and self._dragOffset is not None:
            newPos = a0.globalPosition().toPoint() - self._dragOffset
            self.move(int(newPos.x()), int(newPos.y()))
        return super().mouseMoveEvent(a0)
    
    def mouseReleaseEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            self._dragActive = False
        return super().mouseReleaseEvent(a0)

    def openLargeView(self):
        self.requestLargeView.emit()

    def clearTaskLayout(self):
        while self.taskLayout.count():
            item = self.taskLayout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def showEvent(self, a0):
        self.clearTaskLayout()
        for task in GetTasks():
            if task.show:
                self.addTask(task, adjust=False)

        QTimer.singleShot(10, self.adjustSizeAndPosition)
        return super().showEvent(a0)

if __name__ == "__main__":
    app = App()
    wid = MiniTaskView()
    app.exec()