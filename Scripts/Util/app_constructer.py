import sys
from PyQt6.QtWidgets import QApplication

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
    
    def exec(self):
        sys.exit(self.app.exec())