import sys
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                            QLabel, QDateEdit, QCheckBox, QPushButton)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class TaskAnalyticsChart(QWidget):
    def __init__(self, task_manager, parent=None, background_color="#2b2b2b", text_color="#ffffff"):
        super().__init__(parent)
        self.task_manager = task_manager  # Reference to your task_manager module
        self.background_color = background_color
        self.text_color = text_color
        
        # Set widget background
        self.setStyleSheet(f"background-color: {background_color}; color: {text_color};")
        
        # Create the main layout
        layout = QVBoxLayout(self)
        
        # Create controls
        self.create_controls(layout)
        
        # Create matplotlib figure and canvas
        self.create_chart(layout)
        
        # Store data for tooltips
        self.tooltip_data = {}
        
        # Initial chart update
        self.update_chart()
    
    def create_controls(self, main_layout):
        """Create the control panel with date range and aggregation options"""
        controls_widget = QWidget()
        controls_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.background_color};
                color: {self.text_color};
            }}
            QComboBox {{
                background-color: {self.lighten_color(self.background_color, 20)};
                color: {self.text_color};
                border: 1px solid {self.lighten_color(self.background_color, 40)};
                padding: 5px;
                border-radius: 3px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.text_color};
                width: 0px;
                height: 0px;
            }}
            QDateEdit {{
                background-color: {self.lighten_color(self.background_color, 20)};
                color: {self.text_color};
                border: 1px solid {self.lighten_color(self.background_color, 40)};
                padding: 5px;
                border-radius: 3px;
            }}
            QCheckBox {{
                color: {self.text_color};
            }}
            QPushButton {{
                background-color: {self.lighten_color(self.background_color, 30)};
                color: {self.text_color};
                border: 1px solid {self.lighten_color(self.background_color, 50)};
                padding: 5px 15px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(self.background_color, 40)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(self.background_color, 10)};
            }}
        """)
        
        layout = QVBoxLayout(controls_widget)
        
        # First row: Time period selection
        time_layout = QHBoxLayout()
        
        # Custom date range checkbox
        self.use_custom_range = QCheckBox("Custom Date Range")
        self.use_custom_range.stateChanged.connect(self.toggle_date_range)
        time_layout.addWidget(self.use_custom_range)
        
        time_layout.addStretch()
        
        # Quick period buttons
        quick_periods = [
            ("Last 7 Days", 7),
            ("Last 30 Days", 30),
            ("Last 90 Days", 90),
            ("This Year", 365)
        ]
        
        for text, days in quick_periods:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, d=days: self.set_quick_period(d))
            time_layout.addWidget(btn)
        
        layout.addLayout(time_layout)
        
        # Second row: Date range controls
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self.update_chart)
        self.start_date.setEnabled(False)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self.update_chart)
        self.end_date.setEnabled(False)
        date_layout.addWidget(self.end_date)
        
        date_layout.addStretch()
        
        # Time aggregation dropdown
        date_layout.addWidget(QLabel("Group by:"))
        self.aggregation_combo = QComboBox()
        self.aggregation_combo.addItems(["Day", "Week", "Month", "Year"])
        self.aggregation_combo.currentTextChanged.connect(self.update_chart)
        date_layout.addWidget(self.aggregation_combo)
        
        layout.addLayout(date_layout)
        main_layout.addWidget(controls_widget)
    
    def create_chart(self, main_layout):
        """Create the matplotlib chart"""
        # Set matplotlib style to match dark theme
        plt.style.use('dark_background' if self.is_dark_theme() else 'default')
        
        self.figure = Figure(figsize=(12, 6), facecolor=self.background_color)
        self.canvas = FigureCanvas(self.figure)
        
        # Connect mouse motion event for tooltips
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        
        # Create tooltip
        self.tooltip = None
        
        main_layout.addWidget(self.canvas)
    
    def is_dark_theme(self):
        """Determine if we're using a dark theme based on background color"""
        # Convert hex to RGB and calculate luminance
        hex_color = self.background_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    
    def lighten_color(self, hex_color, percent):
        """Lighten a hex color by a percentage"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten each component
        r = min(255, int(r + (255 - r) * percent / 100))
        g = min(255, int(g + (255 - g) * percent / 100))
        b = min(255, int(b + (255 - b) * percent / 100))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def toggle_date_range(self):
        """Toggle custom date range controls"""
        enabled = self.use_custom_range.isChecked()
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)
        self.update_chart()
    
    def set_quick_period(self, days):
        """Set a quick time period"""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days)
        
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        self.use_custom_range.setChecked(True)
        self.toggle_date_range()
    
    def get_date_range(self):
        """Get the current date range"""
        if self.use_custom_range.isChecked():
            start_qdate = self.start_date.date()
            end_qdate = self.end_date.date()
            start = datetime(start_qdate.year(), start_qdate.month(), start_qdate.day()).date()
            end = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day()).date()
        else:
            # Default to last 30 days
            end = datetime.now().date()
            start = end - timedelta(days=30)
        
        return start, end
    
    def get_aggregated_data(self, aggregation_type):
        """Aggregate task data by the specified time period and date range"""
        all_tasks = self.task_manager.GetTasks()
        start_date, end_date = self.get_date_range()
        
        # Collect all daily work data within the date range
        aggregated_data = defaultdict(lambda: defaultdict(float))
        
        for task in all_tasks:
            category = self.task_manager.GetCategory(task.categoryId)
            category_name = category["Name"]
            
            for date_str, hours in task.dailyWork.items():
                # Convert milliseconds to hours
                hours_worked = hours / (1000 * 3600)
                
                # Parse the date
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue
                
                # Filter by date range
                if date_obj < start_date or date_obj > end_date:
                    continue
                
                # Determine the aggregation key
                date_obj_dt = datetime.combine(date_obj, datetime.min.time())
                if aggregation_type == "Day":
                    key = date_obj.strftime("%m/%d")
                elif aggregation_type == "Week":
                    # Get Monday of the week
                    monday = date_obj - timedelta(days=date_obj.weekday())
                    key = f"{monday.strftime('%m/%d')}"
                elif aggregation_type == "Month":
                    key = date_obj.strftime("%Y-%m")
                elif aggregation_type == "Year":
                    key = date_obj.strftime("%Y")
                
                aggregated_data[key][category_name] += hours_worked
        
        return dict(aggregated_data)
    
    def get_color_for_category(self, category_name):
        """Get color for a category from the task manager"""
        for category in self.task_manager.CATEGORIES.values():
            if category["Name"] == category_name:
                # Convert the Color object to a hex string if needed
                color = category["Color"]
                if hasattr(color, '__str__'):
                    return str(color)
                return color
        return '#3498db'  # Default blue color
    
    def update_chart(self):
        """Update the chart with current data and settings"""
        aggregation_type = self.aggregation_combo.currentText()
        data = self.get_aggregated_data(aggregation_type)
        
        # Clear the previous plot and reset bar segments
        self.figure.clear()
        self.bar_segments = []
        if self.tooltip:
            self.tooltip = None
        
        ax = self.figure.add_subplot(111, facecolor=self.background_color)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14, color=self.text_color)
            self.figure.patch.set_facecolor(self.background_color)
            self.canvas.draw()
            return
        
        # Get all unique categories and time periods
        all_categories = set()
        for period_data in data.values():
            all_categories.update(period_data.keys())
        all_categories = sorted(list(all_categories))
        
        # Sort time periods
        periods = sorted(data.keys())
        
        # Prepare data for stacked bar chart
        category_data = {}
        for category in all_categories:
            category_data[category] = [data[period].get(category, 0) for period in periods]
        
        # Create the stacked bar chart
        bottom = np.zeros(len(periods))
        self.bar_segments = []  # Store bar segments for tooltip detection
        
        for category_idx, category in enumerate(all_categories):
            color = self.get_color_for_category(category)
            values = category_data[category]
            
            bars = ax.bar(periods, values, bottom=bottom, label=category, 
                         color=color, alpha=0.8, edgecolor=self.lighten_color(self.background_color, 30), 
                         linewidth=0.5)
            
            # Store bar segment info for tooltips
            for bar_idx, (bar, value) in enumerate(zip(bars, values)):
                if value > 0:  # Only store segments with actual data
                    self.bar_segments.append({
                        'bar': bar,
                        'category': category,
                        'period': periods[bar_idx],
                        'hours': value,
                        'bottom': bottom[bar_idx],
                        'top': bottom[bar_idx] + value
                    })
            
            bottom += values
        
        # Customize the chart appearance
        ax.set_facecolor(self.background_color)
        ax.tick_params(colors=self.text_color)
        ax.set_ylabel('Hours Worked', fontsize=12, color=self.text_color)
        ax.set_xlabel(f'Time Period ({aggregation_type})', fontsize=12, color=self.text_color)
        ax.set_title('Task Time Distribution', fontsize=14, fontweight='bold', color=self.text_color)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', color=self.text_color)
        
        # Add legend
        if all_categories:
            legend = ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            legend.get_frame().set_facecolor(self.lighten_color(self.background_color, 20))
            legend.get_frame().set_edgecolor(self.lighten_color(self.background_color, 40))
            for text in legend.get_texts():
                text.set_color(self.text_color)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.2, axis='y', color=self.text_color)
        ax.set_axisbelow(True)
        
        # Set figure background
        self.figure.patch.set_facecolor(self.background_color)
        
        # Adjust layout to prevent label cutoff
        self.figure.tight_layout()
        
        # Refresh the canvas
        self.canvas.draw()
    
    def on_hover(self, event):
        """Handle mouse hover events for tooltips"""
        if event.inaxes is None or not hasattr(self, 'bar_segments'):
            self.hide_tooltip()
            return
        
        # Check if mouse is over any bar segment
        for segment in self.bar_segments:
            bar = segment['bar']
            
            # Get bar boundaries
            bar_x = bar.get_x()
            bar_width = bar.get_width()
            bar_left = bar_x
            bar_right = bar_x + bar_width
            
            # Check if mouse is within this bar's x range
            if bar_left <= event.xdata <= bar_right:
                # Check if mouse is within this segment's y range
                if segment['bottom'] <= event.ydata <= segment['top']:
                    self.show_tooltip(event, segment)
                    return
        
        self.hide_tooltip()
    
    def show_tooltip(self, event, segment):
        """Show tooltip with category and hours information"""
        # Remove existing tooltip
        if self.tooltip:
            self.tooltip.remove()
        
        # Format hours nicely
        hours = segment['hours']
        if hours >= 1:
            hours_text = f"{hours:.1f} hours"
        elif hours >= 0.1:
            hours_text = f"{hours:.2f} hours"
        else:
            minutes = hours * 60
            hours_text = f"{minutes:.0f} minutes"
        
        # Create tooltip text
        tooltip_text = f"{segment['category']}\n{hours_text}\n{segment['period']}"
        
        # Create tooltip annotation
        ax = event.inaxes
        self.tooltip = ax.annotate(
            tooltip_text,
            xy=(event.xdata, event.ydata),
            xytext=(20, 20), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', 
                     facecolor=self.lighten_color(self.background_color, 40),
                     edgecolor=self.lighten_color(self.background_color, 60),
                     alpha=0.9),
            fontsize=10,
            color=self.text_color,
            ha='left'
        )
        
        self.canvas.draw_idle()
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.remove()
            self.tooltip = None
            self.canvas.draw_idle()
    
    def refresh_data(self):
        """Call this method when task data is updated"""
        self.update_chart()
    
    def set_theme(self, background_color, text_color):
        """Update the theme colors"""
        self.background_color = background_color
        self.text_color = text_color
        self.setStyleSheet(f"background-color: {background_color}; color: {text_color};")
        
        # Update matplotlib style
        plt.style.use('dark_background' if self.is_dark_theme() else 'default')
        
        # Recreate the chart with new colors
        self.update_chart()