from PyQt6.QtWidgets import QApplication

import sys
import json, gzip

from Scripts.Util.resource_path import resourcePath
from Scripts.large_task_view import LargeTaskView
from Scripts.mini_task_view import MiniTaskView
from Scripts.Tasks.task_manager import SaveAll, LoadAll

SAVE_PATH = resourcePath("taskSaveData.json")

class TaskTrackerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        try:
            with gzip.open(SAVE_PATH + ".gz", "rt", encoding="utf-8") as f:
                data = json.load(f)
                LoadAll(data)
        except FileNotFoundError:
            pass

        self.mainWindow = LargeTaskView()
        self.miniWindow = MiniTaskView(show=False)

        self.mainWindow.requestMiniView.connect(self.openMiniWindow)
        self.miniWindow.requestLargeView.connect(self.openLargeWindow)

    def run(self):
        self.app.aboutToQuit.connect(self.saveData)
        sys.exit(self.app.exec())

    def saveData(self):
        with gzip.open(SAVE_PATH + ".gz", "wt", encoding="utf-8") as f:
            json.dump(SaveAll(), f, separators=(",", ":"))
        
    def openMiniWindow(self, a0):
        a0.ignore()
        self.mainWindow.hide()
        self.miniWindow.show()

    def openLargeWindow(self):
        self.miniWindow.hide()
        self.mainWindow.show()
        self.mainWindow.showMaximized()
        self.mainWindow.setFocus()

if __name__ == "__main__":
    app = TaskTrackerApp()
    app.run()
