from Scripts.Tasks.task_manager import CreateTask, ChangeTaskCategory, CATEGORIES
from Scripts.Tasks.task import Task

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QCheckBox, QHBoxLayout, QPushButton, QSizePolicy, 
                            QVBoxLayout, QWidget, QLabel, QMenu, QMessageBox,
                            QInputDialog, QComboBox, QDialog, QLineEdit, QTextEdit)
from PyQt6.QtGui import QAction, QFont
from Scripts.Util.colors import COLORS


class TaskEditDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Edit Task")
        self.setFixedSize(350, 300)
        
        layout = QVBoxLayout(self)
        
        # Task name
        layout.addWidget(QLabel("Task Name:"))
        self.name_input = QLineEdit(task.name)
        layout.addWidget(self.name_input)
        
        # Category selection
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_ids = []
        current_index = 0
        for i, (cat_id, cat_data) in enumerate(CATEGORIES.items()):
            self.category_combo.addItem(cat_data["Name"])
            self.category_ids.append(cat_id)
            if cat_id == task.categoryId:
                current_index = i
        self.category_combo.setCurrentIndex(current_index)
        layout.addWidget(self.category_combo)
        
        # Duration
        layout.addWidget(QLabel("Duration (minutes):"))
        duration_minutes = task.durationMs / (60 * 1000) if task.durationMs > 0 else 0
        self.duration_input = QLineEdit(str(int(duration_minutes)) if duration_minutes > 0 else "")
        self.duration_input.setPlaceholderText("Leave empty for unlimited")
        layout.addWidget(self.duration_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def save_changes(self):
        # Update name
        new_name = self.name_input.text().strip()
        if new_name:
            self.task.name = new_name
        
        # Update category if changed
        new_category_id = self.category_ids[self.category_combo.currentIndex()]
        if new_category_id != self.task.categoryId:
            ChangeTaskCategory(self.task, new_category_id)
        
        # Update duration
        duration_text = self.duration_input.text().strip()
        if duration_text:
            try:
                duration_minutes = float(duration_text)
                self.task.durationMs = int(duration_minutes * 60 * 1000)
            except ValueError:
                pass
        else:
            self.task.durationMs = 0
        
        self.accept()


class CategoryEditDialog(QDialog):
    def __init__(self, category_id, category_data, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.category_data = category_data
        self.setWindowTitle("Edit Category")
        self.setFixedSize(350, 350)
        
        layout = QVBoxLayout(self)
        
        # Category name
        layout.addWidget(QLabel("Category Name:"))
        self.name_input = QLineEdit(category_data["Name"])
        layout.addWidget(self.name_input)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlainText(category_data["Description"])
        self.desc_input.setFixedHeight(80)
        layout.addWidget(self.desc_input)
        
        # Color selection
        layout.addWidget(QLabel("Color:"))
        color_layout = QHBoxLayout()
        self.selected_color = category_data["Color"]
        
        for color_name in dir(COLORS):
            if color_name.startswith("__"):
                continue
            color_value = getattr(COLORS, color_name)
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setStyleSheet(f"background-color: {color_value.hex}; border: 2px solid {'white' if color_value == self.selected_color else 'gray'};")
            btn.clicked.connect(lambda checked, c=color_value: self.select_color(c))
            color_layout.addWidget(btn)
        
        layout.addLayout(color_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def select_color(self, color):
        self.selected_color = color
        # Update button styles to show selection
        # for i in range(self.layout().itemAt(3).layout().count()):
        #     btn = self.layout().itemAt(3).layout().itemAt(i).widget()
        #     if btn:
        #         color_name = list(dir(COLORS))[i + 2]  # Skip __class__ and __module__
        #         color_value = getattr(COLORS, color_name)
        #         border_color = 'white' if color_value == self.selected_color else 'gray'
        #         btn.setStyleSheet(f"background-color: {color_value.hex}; border: 2px solid {border_color};")
    
    def save_changes(self):
        new_name = self.name_input.text().strip()
        if new_name:
            self.category_data["Name"] = new_name
        
        self.category_data["Description"] = self.desc_input.toPlainText()
        self.category_data["Color"] = self.selected_color
        
        self.accept()


class CollapsibleCategory(QWidget):
    category_updated = pyqtSignal()
    category_deleted = pyqtSignal(int)  # Emits category ID
    
    def __init__(self, categoryId, categoryData, sidebar_width=200):
        super().__init__()
        self.categoryId = categoryId
        self.categoryData = categoryData
        self.sidebar_width = sidebar_width
        self.collapsed = False

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)

        # Category header
        self.create_category_header()
        
        # Active tasks container
        self.active_tasks_widget = QWidget()
        self.active_tasks_layout = QVBoxLayout(self.active_tasks_widget)
        self.active_tasks_layout.setContentsMargins(20, 0, 0, 0)
        self.active_tasks_layout.setSpacing(1)
        
        # Completed tasks section
        self.completed_section = self.create_completed_section()
        
        self.refresh_tasks()
        
    def create_category_header(self):
        """Create the category header with checkbox, name, and controls"""
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Category checkbox
        self.category_checkbox = QCheckBox()
        self.category_checkbox.setChecked(True)
        self.category_checkbox.stateChanged.connect(self.toggle_category_show)
        self.header_layout.addWidget(self.category_checkbox)
        
        # Category name label (truncated)
        self.category_label = QLabel(self.categoryData["Name"])
        self.category_label.setStyleSheet(f"color: {self.categoryData['Color']}; font-weight: bold;")
        self.update_label_text()
        self.header_layout.addWidget(self.category_label, 1)  # Stretch factor 1
        
        # Edit button (3 dots)
        self.edit_btn = QPushButton("⋯")
        self.edit_btn.setFixedSize(20, 20)
        self.edit_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background: rgba(255,255,255,0.1); }")
        self.edit_btn.clicked.connect(self.show_category_menu)
        self.header_layout.addWidget(self.edit_btn)
        
        # Collapse/expand button
        self.toggle_btn = QPushButton("−")
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        self.header_layout.addWidget(self.toggle_btn)
        
        # Context menu
        self.header_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.header_widget.customContextMenuRequested.connect(self.show_category_context_menu)
        
        self.layout.addWidget(self.header_widget)
    
    def create_completed_section(self):
        """Create the completed tasks section"""
        completed_widget = QWidget()
        completed_layout = QVBoxLayout(completed_widget)
        completed_layout.setContentsMargins(20, 0, 0, 0)
        completed_layout.setSpacing(1)
        
        # Completed header
        completed_header = QWidget()
        completed_header_layout = QHBoxLayout(completed_header)
        completed_header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.completed_checkbox = QCheckBox("Completed")
        self.completed_checkbox.setFont(QFont("Arial", 9))
        self.completed_checkbox.setStyleSheet("color: #888888;")
        self.completed_checkbox.stateChanged.connect(self.toggle_completed_show)
        
        self.completed_toggle_btn = QPushButton("−")
        self.completed_toggle_btn.setFixedSize(15, 15)
        self.completed_toggle_btn.setFont(QFont("Arial", 8))
        self.completed_toggle_btn.clicked.connect(self.toggle_completed_collapse)
        
        completed_header_layout.addWidget(self.completed_checkbox)
        completed_header_layout.addStretch()
        completed_header_layout.addWidget(self.completed_toggle_btn)
        
        completed_layout.addWidget(completed_header)
        
        # Completed tasks container
        self.completed_tasks_widget = QWidget()
        self.completed_tasks_layout = QVBoxLayout(self.completed_tasks_widget)
        self.completed_tasks_layout.setContentsMargins(15, 0, 0, 0)
        self.completed_tasks_layout.setSpacing(1)
        
        completed_layout.addWidget(self.completed_tasks_widget)
        
        self.completed_collapsed = False
        return completed_widget
    
    def update_width(self, width):
        """Update the sidebar width and truncate text accordingly"""
        self.sidebar_width = width
        self.update_label_text()
        
        # Update all task labels
        for i in range(self.active_tasks_layout.count()):
            widget = self.active_tasks_layout.itemAt(i).widget()
            if hasattr(widget, 'update_width'):
                widget.update_width(width - 40)  # Account for indentation
                
        for i in range(self.completed_tasks_layout.count()):
            widget = self.completed_tasks_layout.itemAt(i).widget()
            if hasattr(widget, 'update_width'):
                widget.update_width(width - 55)  # Account for deeper indentation
    
    def update_label_text(self):
        """Update category label with proper truncation"""
        available_width = self.sidebar_width - 60  # Account for checkbox, buttons
        font_metrics = self.category_label.fontMetrics()
        truncated_text = font_metrics.elidedText(
            self.categoryData["Name"], 
            Qt.TextElideMode.ElideRight, 
            available_width
        )
        self.category_label.setText(truncated_text)
        self.category_label.setToolTip(self.categoryData["Name"])  # Show full name on hover
    
    def show_category_menu(self):
        """Show category edit menu"""
        menu = QMenu(self)
        
        edit_action = QAction("Edit Category", self)
        edit_action.triggered.connect(self.edit_category)
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Category", self)
        delete_action.triggered.connect(self.delete_category)
        menu.addAction(delete_action)
        
        menu.exec(self.edit_btn.mapToGlobal(self.edit_btn.rect().bottomLeft()))
    
    def show_category_context_menu(self, position):
        """Show context menu for category"""
        self.show_category_menu()
    
    def edit_category(self):
        """Open category edit dialog"""
        dialog = CategoryEditDialog(self.categoryId, self.categoryData, self)
        if dialog.exec():
            self.category_label.setStyleSheet(f"color: {self.categoryData['Color']}; font-weight: bold;")
            self.update_label_text()
            self.category_updated.emit()
    
    def delete_category(self):
        """Delete category with confirmation"""
        if self.categoryData["Tasks"]:
            QMessageBox.warning(self, "Cannot Delete", 
                              "Cannot delete category with tasks. Move or delete tasks first.")
            return
        
        reply = QMessageBox.question(self, "Delete Category", 
                                   f"Are you sure you want to delete '{self.categoryData['Name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.category_deleted.emit(self.categoryId)
    
    def refresh_tasks(self):
        """Clear and re-add task widgets"""
        # Clear active tasks
        for i in reversed(range(self.active_tasks_layout.count())):
            widget = self.active_tasks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Clear completed tasks
        for i in reversed(range(self.completed_tasks_layout.count())):
            widget = self.completed_tasks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add tasks to appropriate sections
        for task in self.categoryData["Tasks"]:
            task_widget = TaskWidget(task, self.sidebar_width - 40)
            task_widget.task_updated.connect(self.category_updated.emit)
            task_widget.task_deleted.connect(self.handle_task_deleted)
            
            if task.isFinished():
                self.completed_tasks_layout.addWidget(task_widget)
            else:
                self.active_tasks_layout.addWidget(task_widget)
        
        # Add widgets to layout if not already added
        if self.active_tasks_widget.parent() is None:
            self.layout.addWidget(self.active_tasks_widget)
        if self.completed_section.parent() is None:
            self.layout.addWidget(self.completed_section)
        
        # Update completed section visibility
        has_completed = self.completed_tasks_layout.count() > 0
        self.completed_section.setVisible(has_completed and not self.collapsed)
    
    def handle_task_deleted(self, task):
        """Handle task deletion"""
        self.categoryData["Tasks"].remove(task)
        self.refresh_tasks()
        self.category_updated.emit()
    
    def toggle_collapse(self):
        """Toggle category collapse state"""
        self.collapsed = not self.collapsed
        self.active_tasks_widget.setVisible(not self.collapsed)
        self.completed_section.setVisible(not self.collapsed and self.completed_tasks_layout.count() > 0)
        self.toggle_btn.setText("+" if self.collapsed else "−")
    
    def toggle_completed_collapse(self):
        """Toggle completed tasks collapse state"""
        self.completed_collapsed = not self.completed_collapsed
        self.completed_tasks_widget.setVisible(not self.completed_collapsed)
        self.completed_toggle_btn.setText("+" if self.completed_collapsed else "−")
    
    def toggle_category_show(self, state):
        """Toggle visibility of all tasks in category"""
        show = state == 2
        for task in self.categoryData["Tasks"]:
            task.show = show
        self.refresh_tasks()
    
    def toggle_completed_show(self, state):
        """Toggle visibility of completed tasks"""
        show = state == 2
        for i in range(self.completed_tasks_layout.count()):
            widget = self.completed_tasks_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'task'):
                widget.task.show = show
                widget.update_checkbox()


class TaskWidget(QWidget):
    task_updated = pyqtSignal()
    task_deleted = pyqtSignal(Task)
    
    def __init__(self, task, width):
        super().__init__()
        self.task = task
        self.width = width
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Task checkbox
        self.task_checkbox = QCheckBox()
        self.task_checkbox.setChecked(task.show)
        self.task_checkbox.stateChanged.connect(self.toggle_task_show)
        layout.addWidget(self.task_checkbox)
        
        # Task name label
        self.task_label = QLabel()
        self.update_label_text()
        layout.addWidget(self.task_label, 1)
        
        # Edit button
        self.edit_btn = QPushButton("⋯")
        self.edit_btn.setFixedSize(15, 15)
        self.edit_btn.setFont(QFont("Arial", 8))
        self.edit_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background: rgba(255,255,255,0.1); }")
        self.edit_btn.clicked.connect(self.show_task_menu)
        layout.addWidget(self.edit_btn)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_task_context_menu)
        
        # Style completed tasks differently
        if self.task.isFinished():
            self.setStyleSheet("color: #888888;")
            self.task_label.setStyleSheet("text-decoration: line-through;")
    
    def update_width(self, width):
        """Update width and truncate text"""
        self.width = width
        self.update_label_text()
    
    def update_label_text(self):
        """Update task label with proper truncation"""
        available_width = self.width - 40  # Account for checkbox and button
        font_metrics = self.task_label.fontMetrics()
        truncated_text = font_metrics.elidedText(
            self.task.name, 
            Qt.TextElideMode.ElideRight, 
            available_width
        )
        self.task_label.setText(truncated_text)
        self.task_label.setToolTip(self.task.name)
    
    def update_checkbox(self):
        """Update checkbox state"""
        self.task_checkbox.setChecked(self.task.show)
    
    def show_task_menu(self):
        """Show task edit menu"""
        menu = QMenu(self)
        
        edit_action = QAction("Edit Task", self)
        edit_action.triggered.connect(self.edit_task)
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Task", self)
        delete_action.triggered.connect(self.delete_task)
        menu.addAction(delete_action)
        
        if not self.task.isFinished():
            complete_action = QAction("Mark Complete", self)
            complete_action.triggered.connect(self.mark_complete)
            menu.addAction(complete_action)
        
        menu.exec(self.edit_btn.mapToGlobal(self.edit_btn.rect().bottomLeft()))
    
    def show_task_context_menu(self, position):
        """Show context menu for task"""
        self.show_task_menu()
    
    def edit_task(self):
        """Open task edit dialog"""
        dialog = TaskEditDialog(self.task, self)
        if dialog.exec():
            self.update_label_text()
            self.task_updated.emit()
    
    def delete_task(self):
        """Delete task with confirmation"""
        reply = QMessageBox.question(self, "Delete Task", 
                                   f"Are you sure you want to delete '{self.task.name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.task_deleted.emit(self.task)
    
    def mark_complete(self):
        """Mark task as complete"""
        self.task.elapsedTimeMs = self.task.durationMs
        self.task_updated.emit()
    
    def toggle_task_show(self, state):
        """Toggle task visibility"""
        self.task.show = state == 2