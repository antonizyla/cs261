from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, QHBoxLayout)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

# Global variables to store inputs
road_inputs = {
    "northbound_traffic_flow": {},
    "eastbound_traffic_flow": {},
    "westbound_traffic_flow": {},
    "southbound_traffic_flow": {}
}

class InputAndParameterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        self.create_road_group(main_layout, "Northbound Traffic Flow", ["North", "East", "West"])
        self.create_road_group(main_layout, "Southbound Traffic Flow", ["South", "East", "West"])
        self.create_road_group(main_layout, "Eastbound Traffic Flow", ["East", "North", "South"])
        self.create_road_group(main_layout, "Westbound Traffic Flow", ["West", "North", "South"])

        self.submit_button = QPushButton("Start Simulation")
        self.submit_button.clicked.connect(self.update_global_inputs)
        main_layout.addWidget(self.submit_button)

        self.setLayout(main_layout)

    def create_road_group(self, layout, road_name, exit_directions):
        group_box = QGroupBox()
        form_layout = QFormLayout()

        # Create a button to toggle visibility of the form layout
        toggle_button = QToolButton()
        toggle_button.setText(road_name + " " + "▼")  # Default is to show the group
        toggle_button.setCheckable(True)
        toggle_button.setChecked(True)
        toggle_button.clicked.connect(lambda: self.toggle_group(toggle_button, group_box, road_name))

        # Add the button to a horizontal layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(toggle_button)
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove any margins around the header layout
        header_layout.addStretch()

        # Total Vehicles per Hour display (not an input)
        total_vph_label = QLabel("Total Vehicles per Hour (VpH): 0")
        form_layout.addRow(total_vph_label)

        # Store reference for total VpH label
        setattr(self, f"{road_name.lower().replace(' ', '_')}_total_vph_label", total_vph_label)

        # Exiting VpH inputs
        exit_vph_inputs = {}
        for direction in exit_directions:
            exit_label = QLabel(f"Exiting {direction}:")
            exit_input = QLineEdit()
            exit_input.setValidator(QIntValidator(0, 999))
            exit_input.setPlaceholderText("0")  # Default placeholder
            exit_input.textChanged.connect(lambda _, r=road_name: self.update_total_vph(r))  # Auto-update total VpH
            form_layout.addRow(exit_label, exit_input)
            exit_vph_inputs[direction] = exit_input

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

        # Set layout for the group box
        group_box.setLayout(form_layout)

        # Set header layout at the top of the group box
        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        # Add header layout above the form layout
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(header_widget)
        group_box_layout.addWidget(group_box)

        # Add the group box to the main layout
        layout.addLayout(group_box_layout)

        # Store references to the inputs
        base_name = road_name.lower().replace(' ', '_')
        setattr(self, f"{base_name}_lanes_input", lanes_input)
        setattr(self, f"{base_name}_bus_lane_checkbox", bus_lane_checkbox)
        setattr(self, f"{base_name}_left_turn_lane_checkbox", left_turn_lane_checkbox)
        setattr(self, f"{base_name}_right_turn_lane_checkbox", right_turn_lane_checkbox)
        setattr(self, f"{base_name}_exit_vph_inputs", exit_vph_inputs)

    def toggle_group(self, toggle_button, group_box, road_name):
        """ Toggles the visibility of the group box content. """
        if toggle_button.isChecked():
            toggle_button.setText(road_name + " " + "▼")  # Show the content
            group_box.setVisible(True)
        else:
            toggle_button.setText(road_name + " " + "►")  # Hide the content
            group_box.setVisible(False)

    def update_total_vph(self, road_name):
        """ Updates the total VpH label based on the sum of exit values. """
        base_name = road_name.lower().replace(' ', '_')
        exit_vph_inputs = getattr(self, f"{base_name}_exit_vph_inputs")
        total_vph_label = getattr(self, f"{base_name}_total_vph_label")

        try:
            total_vph = sum(int(input_field.text()) if input_field.text().isdigit() else 0 
                            for input_field in exit_vph_inputs.values())
        except ValueError:
            total_vph = 0  # In case of invalid input

        total_vph_label.setText(f"Total Vehicles per Hour (VpH): {total_vph}")

    def update_global_inputs(self):
        """ Stores user inputs into the global dictionary for use in simulations. """
        for road_name in ["northbound_traffic_flow", "southbound_traffic_flow", 
                          "eastbound_traffic_flow", "westbound_traffic_flow"]:
            
            total_vph = getattr(self, f"{road_name}_total_vph_label").text().split(": ")[1]
            lanes = getattr(self, f"{road_name}_lanes_input").value()
            bus_lane = getattr(self, f"{road_name}_bus_lane_checkbox").isChecked()
            left_turn_lane = getattr(self, f"{road_name}_left_turn_lane_checkbox").isChecked()
            right_turn_lane = getattr(self, f"{road_name}_right_turn_lane_checkbox").isChecked()

            # Collect exiting VpH values
            exit_vphs = {}
            for direction, input_field in getattr(self, f"{road_name}_exit_vph_inputs").items():
                exit_vphs[direction] = input_field.text()

            # Store inputs in the global dictionary
            road_inputs[road_name] = {
                "total_vph": total_vph,
                "lanes": lanes,
                "bus_lane": bus_lane,
                "left_turn_lane": left_turn_lane,
                "right_turn_lane": right_turn_lane,
                "exit_vphs": exit_vphs
            }

        # Print all inputs to the terminal
        for road_name, inputs in road_inputs.items():
            print(f"{road_name.replace('_', ' ').title()}:")
            print(f"  Total Vehicles per Hour: {inputs['total_vph']}")  
            print(f"  Number of Lanes: {inputs['lanes']}")
            print(f"  Bus Lane: {inputs['bus_lane']}")
            print(f"  Left Turn Lane: {inputs['left_turn_lane']}")
            print(f"  Right Turn Lane: {inputs['right_turn_lane']}")
            for direction, vph in inputs["exit_vphs"].items():
                print(f"  - Exiting {direction}: {vph} VpH")
            print()
