from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMainWindow, QLineEdit, QSpinBox, QCheckBox, QGroupBox, QFormLayout
from PyQt5.QtCore import QSize, Qt
import sys

# Global variables to store inputs
road_inputs = {
    "northerly_road": {},
    "easterly_road": {},
    "westerly_road": {},
    "southerly_road": {}
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Road Inputs")

        main_layout = QVBoxLayout()

        self.create_road_group(main_layout, "Northerly Road")
        self.create_road_group(main_layout, "Easterly Road")
        self.create_road_group(main_layout, "Westerly Road")
        self.create_road_group(main_layout, "Southerly Road")

        self.submit_button = QPushButton("Start Simulation")
        self.submit_button.clicked.connect(self.update_global_inputs)
        main_layout.addWidget(self.submit_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_road_group(self, layout, road_name):
        group_box = QGroupBox(road_name)
        form_layout = QFormLayout()

        # Vehicles per hour input
        vph_label = QLabel("Vehicles per Hour (VpH):")
        vph_input = QLineEdit()
        form_layout.addRow(vph_label, vph_input)

        # Number of lanes input
        lanes_label = QLabel("Number of Lanes:")
        lanes_input = QSpinBox()
        lanes_input.setRange(1, 5)
        form_layout.addRow(lanes_label, lanes_input)

        # Checkboxes for lane types
        bus_lane_checkbox = QCheckBox("Bus Lane")
        left_turn_lane_checkbox = QCheckBox("Left Turn Lane")
        right_turn_lane_checkbox = QCheckBox("Right Turn Lane")
        form_layout.addRow(bus_lane_checkbox)
        form_layout.addRow(left_turn_lane_checkbox)
        form_layout.addRow(right_turn_lane_checkbox)

        group_box.setLayout(form_layout)
        layout.addWidget(group_box)

        # Store references to the inputs
        setattr(self, f"{road_name.lower().replace(' ', '_')}_vph_input", vph_input)
        setattr(self, f"{road_name.lower().replace(' ', '_')}_lanes_input", lanes_input)
        setattr(self, f"{road_name.lower().replace(' ', '_')}_bus_lane_checkbox", bus_lane_checkbox)
        setattr(self, f"{road_name.lower().replace(' ', '_')}_left_turn_lane_checkbox", left_turn_lane_checkbox)
        setattr(self, f"{road_name.lower().replace(' ', '_')}_right_turn_lane_checkbox", right_turn_lane_checkbox)

    # Update global variables with inputs
    def update_global_inputs(self):
        for road_name in ["northerly_road", "easterly_road", "westerly_road", "southerly_road"]:
            road_inputs[road_name] = {
                "vph": getattr(self, f"{road_name}_vph_input").text(),
                "lanes": getattr(self, f"{road_name}_lanes_input").value(),
                "bus_lane": getattr(self, f"{road_name}_bus_lane_checkbox").isChecked(),
                "left_turn_lane": getattr(self, f"{road_name}_left_turn_lane_checkbox").isChecked(),
                "right_turn_lane": getattr(self, f"{road_name}_right_turn_lane_checkbox").isChecked()
            }

        # Prints inputs in ternminal when button is clicked
        for road_name, inputs in road_inputs.items():
            print(f"{road_name.replace('_', ' ').title()}:")
            print(f"  Vehicles per Hour: {inputs['vph']}")
            print(f"  Number of Lanes: {inputs['lanes']}")
            print(f"  Bus Lane: {inputs['bus_lane']}")
            print(f"  Left Turn Lane: {inputs['left_turn_lane']}")
            print(f"  Right Turn Lane: {inputs['right_turn_lane']}")
            print()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
