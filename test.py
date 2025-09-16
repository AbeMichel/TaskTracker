import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
import pyqtgraph as pg
from PyQt6.QtCore import QTimer


class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Task Graph")

        layout = QVBoxLayout(self)

        # PyQtGraph plot widget
        self.plotWidget = pg.PlotWidget()
        layout.addWidget(self.plotWidget)

        # Configure the graph
        self.plotWidget.setBackground("w")
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.addLegend()

        # Example line (progress over time)
        self.x_data = []
        self.y_data = []
        self.curve = self.plotWidget.plot(self.x_data, self.y_data, pen=pg.mkPen(color="b", width=2), name="Progress")

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # update every second

    def update_data(self):
        # Simulate new data point
        new_x = len(self.x_data)
        new_y = random.randint(0, 100)  # replace with real data (e.g., % completion)
        self.x_data.append(new_x)
        self.y_data.append(new_y)

        self.curve.setData(self.x_data, self.y_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GraphWidget()
    w.show()
    sys.exit(app.exec())
