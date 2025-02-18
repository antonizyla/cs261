from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QLabel, QGroupBox, 
                             QFormLayout, QToolButton, QHBoxLayout, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt
import os

# Global variables to store results
road_results = {
    "northbound_traffic_flow": {},
    "eastbound_traffic_flow": {},
    "westbound_traffic_flow": {},
    "southbound_traffic_flow": {}
}

class ResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load and apply the stylesheet
        self.apply_stylesheet()

        # Use a grid layout instead of a vertical layout
        main_layout = QGridLayout()
        main_layout.setSpacing(5)  # Reduce spacing for a more compact layout

        # Button to generate results
        self.generate_results_button = QPushButton("Generate Results")
        self.generate_results_button.clicked.connect(self.get_results)
        main_layout.addWidget(self.generate_results_button, 0, 0, 1, 2)  # Span two columns

        # Create road result groups in a 2x2 grid
        self.create_road_group(main_layout, "Northbound Traffic Flow", 1, 0)  # Top-left
        self.create_road_group(main_layout, "Southbound Traffic Flow", 1, 1)  # Top-right
        self.create_road_group(main_layout, "Eastbound Traffic Flow", 2, 0)   # Bottom-left
        self.create_road_group(main_layout, "Westbound Traffic Flow", 2, 1)   # Bottom-right

        # Button to get report
        self.generate_report_button = QPushButton("Generate Report")
        self.generate_report_button.clicked.connect(self.get_report)
        main_layout.addWidget(self.generate_report_button, 3, 0, 1, 2)  # Span two columns

        self.setLayout(main_layout)

    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            with open(os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss'), 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")

    def create_road_group(self, layout, road_name, row, col):
        """Creates a collapsible group box for each road's results and places it in the grid."""
        group_box = QGroupBox()
        group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Makes all groups uniform in height
        form_layout = QFormLayout()
        form_layout.setContentsMargins(5, 5, 5, 5)  # Minimize padding inside groups

        # Create a button to toggle visibility of the form layout
        toggle_button = QToolButton()
        toggle_button.setText(road_name + " ▼")  # Default is to show the group
        toggle_button.setCheckable(True)
        toggle_button.setChecked(True)
        toggle_button.clicked.connect(lambda: self.toggle_group(toggle_button, group_box, road_name))

        # Add the button to a horizontal layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(toggle_button)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch()

        # Labels for results (default placeholders)
        avg_wait_label = QLabel("Average Wait Time: -")
        max_wait_label = QLabel("Max Wait Time: -")
        max_queue_label = QLabel("Max Queue Length: -")

        form_layout.addRow(avg_wait_label)
        form_layout.addRow(max_wait_label)
        form_layout.addRow(max_queue_label)

        # Store reference for updating results later
        base_name = road_name.lower().replace(' ', '_')
        setattr(self, f"{base_name}_avg_wait_label", avg_wait_label)
        setattr(self, f"{base_name}_max_wait_label", max_wait_label)
        setattr(self, f"{base_name}_max_queue_label", max_queue_label)

        # Set layout for the group box
        group_box.setLayout(form_layout)

        # Set header layout at the top of the group box
        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        # Add header layout above the form layout
        group_box_layout = QVBoxLayout()
        group_box_layout.setContentsMargins(0, 0, 0, 0)  # Reduce outer margins
        group_box_layout.addWidget(header_widget)
        group_box_layout.addWidget(group_box)

        # Add the group box to the grid layout at the specified position
        layout.addLayout(group_box_layout, row, col)

    def toggle_group(self, toggle_button, group_box, road_name):
        """ Toggles the visibility of the group box content. """
        if toggle_button.isChecked():
            toggle_button.setText(road_name + " ▼")  # Show the content
            group_box.setVisible(True)
        else:
            toggle_button.setText(road_name + " ►")  # Hide the content
            group_box.setVisible(False)

    def get_results(self):
        # Placeholder result values
        self.average_wait = [20, 30, 25, 15]
        self.max_wait_time = [40, 50, 35, 20]
        self.max_queue_length = [10, 15, 12, 8]

        counter = 0
        for road_name in ["northbound_traffic_flow", "southbound_traffic_flow", 
                          "eastbound_traffic_flow", "westbound_traffic_flow"]:

            road_results[road_name] = {
                "average_wait": self.average_wait[counter],
                "max_wait_times": self.max_wait_time[counter],
                "max_queue_length": self.max_queue_length[counter],
            }

            # Update UI labels
            base_name = road_name.lower().replace(' ', '_')
            getattr(self, f"{base_name}_avg_wait_label").setText(f"Average Wait Time: {self.average_wait[counter]} sec")
            getattr(self, f"{base_name}_max_wait_label").setText(f"Max Wait Time: {self.max_wait_time[counter]} sec")
            getattr(self, f"{base_name}_max_queue_label").setText(f"Max Queue Length: {self.max_queue_length[counter]} cars")

            counter += 1
    
    def get_report(self):
        #Get the report from the backend
        return 0
