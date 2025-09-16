from Scripts.Tasks.task import Task


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QProgressBar

TASK_BAR_HEIGHT = 25

class TaskTimerBar(QProgressBar):
    def __init__(self, task: Task, parent = None):
        super().__init__(parent)
        self.task = task

        self.task.updated.connect(self.updateProgress)
        self.task.focused.connect(self.updateStyle)
        self.task.unfocused.connect(self.updateStyle)

        self.setTextVisible(True)
        self.setFormat(self.task.name)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(TASK_BAR_HEIGHT)
        self.updateStyle()

        self.setValue(100)

    def mousePressEvent(self, event):
        # Call parent callback if assigned
        if self.parent() and hasattr(self.parent(), "setActiveTask"):
            if self.task.active:
                self.parent().setActiveTask(None)
            else:
                self.parent().setActiveTask(self.task)
        super().mousePressEvent(event)

    def formatTime(self):
        msLeft = self.task.durationMs - self.task.elapsedTimeMs
        seconds = msLeft // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        time = f"{seconds:02}"
        if days > 0:
            time = f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
        elif hours > 0:
            time = f"{hours:02}:{minutes:02}:{seconds:02}"
        elif minutes > 0:
            time = f"{minutes:02}:{seconds:02}"

        return time

    def updateProgress(self):
        self.setValue(100 - self.task.progress())
        if self.underMouse():
            self.setFormat(f"{self.task.name} — {self.formatTime()}")

    def updateStyle(self):
        """Update the bar color based on active state"""
        if self.task.active:
            # colored green
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #555;
                    border-radius: 4px;
                    background-color: #333;
                }
                QProgressBar::chunk {
                    background-color: #00aa00;
                    width: 10px;
                }
            """)
        else:
            # grayscale inactive
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #555;
                    border-radius: 4px;
                    background-color: #555;
                }
                QProgressBar::chunk {
                    background-color: #888;
                    width: 10px;
                }
            """)

    def enterEvent(self, event):
        self.setFormat(f"{self.task.name} — {self.formatTime()}")
        return super().enterEvent(event)

    def leaveEvent(self, a0):
        self.setFormat(self.task.name)
        return super().leaveEvent(a0)