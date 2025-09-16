from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLabel,
    QScrollArea, QPushButton, QSizePolicy, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QColor, QCursor
from datetime import datetime
from collections import defaultdict

from Scripts.SupportUI.collapsable_category import CollapsibleCategory
from Scripts.SupportUI.category_dialog import CategoryCreationWindow
from Scripts.SupportUI.task_dialog import TaskCreationWindow 
from Scripts.SupportUI.task_calendar import TaskAnalyticsChart
from Scripts.Util.app_constructer import App
from Scripts.Tasks.task_manager import CATEGORIES, AddCategory
import Scripts.Tasks.task_manager as task_manager

MIN_SIDEBAR_WIDTH = 150
MAX_SIDEBAR_WIDTH = 400
DEFAULT_SIDEBAR_WIDTH = 250
WIDTH = 1200
HEIGHT = 700


class CollapsibleSidebar(QWidget):
    """Collapsible and resizable sidebar widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collapsed = False
        self.sidebar_width = DEFAULT_SIDEBAR_WIDTH
        self.min_width = MIN_SIDEBAR_WIDTH
        self.max_width = MAX_SIDEBAR_WIDTH
        
        # Set up the main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Collapse/expand button
        self.collapse_button = QPushButton("◀")
        self.collapse_button.setFixedSize(20, 50)
        self.collapse_button.clicked.connect(self.toggle_collapse)
        self.collapse_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        
        # Resize handle
        self.resize_handle = QFrame()
        self.resize_handle.setFixedWidth(5)
        self.resize_handle.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.resize_handle.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        # Mouse tracking for resize
        self.resize_handle.mousePressEvent = self.start_resize
        self.resize_handle.mouseMoveEvent = self.do_resize
        self.resize_handle.mouseReleaseEvent = self.end_resize
        self.resizing = False
        self.resize_start_x = 0
        self.resize_start_width = 0
        
        self.setup_layout()
        self.setFixedWidth(self.sidebar_width)
    
    def setup_layout(self):
        """Set up the sidebar layout"""
        # Add content and controls
        self.main_layout.addWidget(self.content_widget)
        
        # Right side controls container
        controls_container = QWidget()
        controls_container.setFixedWidth(25)
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(2, 10, 2, 2)
        controls_layout.addWidget(self.collapse_button)
        controls_layout.addStretch()
        
        self.main_layout.addWidget(controls_container)
        self.main_layout.addWidget(self.resize_handle)
    
    def add_widget(self, widget):
        """Add a widget to the sidebar content"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the sidebar content"""
        self.content_layout.addLayout(layout)
    
    def toggle_collapse(self):
        """Toggle sidebar collapse state"""
        self.collapsed = not self.collapsed
        
        if self.collapsed:
            self.content_widget.hide()
            self.setFixedWidth(25)
            self.collapse_button.setText("▶")
            self.resize_handle.hide()
        else:
            self.content_widget.show()
            self.setFixedWidth(self.sidebar_width)
            self.collapse_button.setText("◀")
            self.resize_handle.show()
    
    def start_resize(self, event):
        """Start resizing the sidebar"""
        if not self.collapsed:
            self.resizing = True
            self.resize_start_x = event.globalPosition().x()
            self.resize_start_width = self.sidebar_width
    
    def do_resize(self, event):
        """Handle sidebar resizing"""
        if self.resizing and not self.collapsed:
            delta_x = event.globalPosition().x() - self.resize_start_x
            new_width = int(max(self.min_width, min(self.max_width, self.resize_start_width + delta_x)))
            self.sidebar_width = new_width
            self.setFixedWidth(new_width)
            
            # Notify category widgets of width change
            self.update_category_widths()
    
    def end_resize(self, event):
        """End sidebar resizing"""
        self.resizing = False
    
    def update_category_widths(self):
        """Update width of all category widgets"""
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'update_width'):
                    widget.update_width(self.sidebar_width - 30)  # Account for margins


class LargeTaskView(QWidget):
    requestMiniView = pyqtSignal(QEvent)
    
    def __init__(self, show=True):
        super().__init__()
        self.setWindowTitle("Tasks Overview")
        self.setGeometry(100, 100, WIDTH, HEIGHT)
        
        # Set dark theme colors
        self.bg_color = "#2b2b2b"
        self.text_color = "#ffffff"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.bg_color};
                color: {self.text_color};
            }}
            QPushButton {{
                background-color: {self.lighten_color(self.bg_color, 20)};
                color: {self.text_color};
                border: 1px solid {self.lighten_color(self.bg_color, 40)};
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(self.bg_color, 30)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(self.bg_color, 10)};
            }}
            QScrollArea {{
                border: 1px solid {self.lighten_color(self.bg_color, 40)};
                border-radius: 4px;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {self.bg_color};
            }}
        """)
        
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # Create collapsible sidebar
        self.sidebar = CollapsibleSidebar()
        self.setup_sidebar_content()
        
        # Create main content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        
        # Add analytics chart
        self.analyticsChart = TaskAnalyticsChart(
            task_manager, 
            background_color=self.bg_color, 
            text_color=self.text_color
        )
        self.content_layout.addWidget(self.analyticsChart)
        
        # Add to main layout
        self.mainLayout.addWidget(self.sidebar)
        self.mainLayout.addWidget(self.content_area, 1)  # Content area gets remaining space

        if show:
            self.show()

    def setup_sidebar_content(self):
        """Set up the sidebar with scrollable categories and buttons"""
        # Scrollable area for categories
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollContent = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollLayout.setSpacing(5)
        self.scrollContent.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum
        )

        # Populate categories
        self.categoryWidgets = []
        self.populateCategories()

        self.scrollArea.setWidget(self.scrollContent)
        self.sidebar.add_widget(self.scrollArea)

        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(5)
        
        # Add category button
        self.addCategoryBtn = QPushButton("Add Category")
        self.addCategoryBtn.clicked.connect(self.createCategoryPopup)
        buttons_layout.addWidget(self.addCategoryBtn)
        
        # Add task button
        self.addTaskBtn = QPushButton("Add Task")
        self.addTaskBtn.clicked.connect(self.createTaskPopup)
        buttons_layout.addWidget(self.addTaskBtn)
        
        # Refresh chart button
        self.refreshBtn = QPushButton("Refresh Chart")
        self.refreshBtn.clicked.connect(self.refreshChart)
        buttons_layout.addWidget(self.refreshBtn)

        self.sidebar.add_widget(buttons_container)

    def lighten_color(self, hex_color, percent):
        """Lighten a hex color by a percentage"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten each component
        r = min(255, int(r + (255 - r) * percent / 100))
        g = min(255, int(g + (255 - g) * percent / 100))
        b = min(255, int(b + (255 - b) * percent / 100))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def populateCategories(self):
        """Clear and populate all categories"""
        # Clear existing widgets
        for i in reversed(range(self.scrollLayout.count())):
            widget = self.scrollLayout.takeAt(i).widget()
            if widget:
                widget.deleteLater()
        self.categoryWidgets.clear()
        
        # Add category widgets
        for catId, catData in CATEGORIES.items():
            catWidget = CollapsibleCategory(catId, catData, self.sidebar.sidebar_width - 30)
            catWidget.category_updated.connect(self.on_category_updated)
            catWidget.category_deleted.connect(self.on_category_deleted)
            self.scrollLayout.addWidget(catWidget)
            self.categoryWidgets.append(catWidget)

    def on_category_updated(self):
        """Handle category updates"""
        self.populateCategories()
        self.refreshChart()

    def on_category_deleted(self, category_id):
        """Handle category deletion"""
        if category_id in CATEGORIES:
            del CATEGORIES[category_id]
        self.populateCategories()
        self.refreshChart()

    def createCategoryPopup(self):
        """Create a new category"""
        dialog = CategoryCreationWindow(self)
        if dialog.exec():
            self.populateCategories()
            self.refreshChart()

    def createTaskPopup(self):
        """Create a new task"""
        dialog = TaskCreationWindow(self)
        if dialog.exec():
            self.populateCategories()
            self.refreshChart()

    def refreshChart(self):
        """Refresh the analytics chart with current data"""
        self.analyticsChart.refresh_data()

    def changeEvent(self, a0):
        """Handle window state changes"""
        if a0.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                self.requestMiniView.emit(a0)
        return super().changeEvent(a0)

    def showEvent(self, a0):
        """Handle window show events"""
        self.populateCategories()
        self.refreshChart()
        return super().showEvent(a0)

    def set_theme(self, background_color, text_color):
        """Update the theme of the entire view"""
        self.bg_color = background_color
        self.text_color = text_color
        
        # Update widget stylesheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {self.lighten_color(background_color, 20)};
                color: {text_color};
                border: 1px solid {self.lighten_color(background_color, 40)};
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(background_color, 30)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(background_color, 10)};
            }}
            QScrollArea {{
                border: 1px solid {self.lighten_color(background_color, 40)};
                border-radius: 4px;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {background_color};
            }}
        """)
        
        # Update chart theme
        self.analyticsChart.set_theme(background_color, text_color)


if __name__ == "__main__":
    app = App()
    wid = LargeTaskView()
    app.exec()