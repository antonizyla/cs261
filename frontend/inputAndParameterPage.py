from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, 
                             QHBoxLayout, QGridLayout, QMessageBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import os

# Global variables to store inputs, Note that the direction is the direction traffic comes from
road_inputs = {
    "south_traffic_flow": {},
    "west_traffic_flow": {},
    "east_traffic_flow": {},
    "north_traffic_flow": {}
}

class InputAndParameterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load and apply the stylesheet
        self.apply_stylesheet()

        # Main grid layout (2x2)
        main_layout = QGridLayout()

        # Create road groups and assign them to grid
        self.north_group = self.create_road_group("South Traffic Flow", ["North", "East", "West"])
        self.south_group = self.create_road_group("North Traffic Flow", ["South", "East", "West"])
        self.east_group = self.create_road_group("West Traffic Flow", ["East", "North", "South"])
        self.west_group = self.create_road_group("East Traffic Flow", ["West", "North", "South"])

        # Arrange in a 2x2 grid
        main_layout.addWidget(self.north_group, 0, 0)
        main_layout.addWidget(self.south_group, 0, 1)
        main_layout.addWidget(self.east_group, 1, 0)
        main_layout.addWidget(self.west_group, 1, 1)

        # Submit button centered below the grid
        self.submit_button = QPushButton("Start Simulation")
        self.submit_button.clicked.connect(self.update_global_inputs)
        main_layout.addWidget(self.submit_button, 2, 0, 1, 2)  # Spans two columns

        self.setLayout(main_layout)

    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")


    def create_road_group(self, road_name, exit_directions):
        """Creates a group box for each road section with input fields."""
        group_box = QGroupBox(road_name)
        form_layout = QFormLayout()

        # Total Vehicles per Hour display
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
            exit_input.setPlaceholderText("0")  
            exit_input.textChanged.connect(lambda _, r=road_name: self.update_total_vph(r))
            form_layout.addRow(exit_label, exit_input)
            exit_vph_inputs[direction] = exit_input

        # Number of lanes input
        lanes_label = QLabel("Number of Lanes:")
        lanes_input = QSpinBox()
        lanes_input.setRange(1, 5)
        form_layout.addRow(lanes_label, lanes_input)

        # Checkboxes for lane types
        bus_lane_checkbox = QCheckBox("Bus Lane")
        pedestrian_crossing_checkbox = QCheckBox("Pedestrian Crossing")
        left_turn_lane_checkbox = QCheckBox("Left Turn Lane")
        right_turn_lane_checkbox = QCheckBox("Right Turn Lane")
        form_layout.addRow(bus_lane_checkbox)
        form_layout.addRow(pedestrian_crossing_checkbox)
        form_layout.addRow(left_turn_lane_checkbox)
        form_layout.addRow(right_turn_lane_checkbox)

        # Set layout for the group box
        group_box.setLayout(form_layout)

        # Store references to the inputs
        base_name = road_name.lower().replace(' ', '_')
        print(f"{base_name = }")
        setattr(self, f"{base_name}_lanes_input", lanes_input)
        setattr(self, f"{base_name}_bus_lane_checkbox", bus_lane_checkbox)
        setattr(self, f"{base_name}_pedestrian_crossing_checkbox", pedestrian_crossing_checkbox)
        setattr(self, f"{base_name}_left_turn_lane_checkbox", left_turn_lane_checkbox)
        setattr(self, f"{base_name}_right_turn_lane_checkbox", right_turn_lane_checkbox)
        setattr(self, f"{base_name}_exit_vph_inputs", exit_vph_inputs)

        return group_box  # Return the group box to add to the grid layout

    def update_total_vph(self, road_name):
        """ Updates the total VpH label based on the sum of exit values. """
        base_name = road_name.lower().replace(' ', '_')
        exit_vph_inputs = getattr(self, f"{base_name}_exit_vph_inputs")
        total_vph_label = getattr(self, f"{base_name}_total_vph_label")

        try:
            total_vph = sum(int(input_field.text()) if input_field.text().isdigit() else 0 
                           for input_field in exit_vph_inputs.values())
        
        except ValueError:
            total_vph = 0  

        total_vph_label.setText(f"Total Vehicles per Hour (VpH): {total_vph}")


    # Validating Inputs based on exits and lane types
    def validate_inputs(self):
        invalid_inputs = []
        for road_name in ["south_traffic_flow", "north_traffic_flow",
                          "west_traffic_flow", "east_traffic_flow"]:

            base_name = road_name.lower().replace(' ', '_')
            exit_vph_inputs = getattr(self, f"{base_name}_exit_vph_inputs")
            left_turn_lane = getattr(self, f"{base_name}_left_turn_lane_checkbox").isChecked()
            right_turn_lane = getattr(self, f"{base_name}_right_turn_lane_checkbox").isChecked()
            lanes = getattr(self, f"{base_name}_lanes_input").value()
            pedestrian_crossing = getattr(self, f"{base_name}_pedestrian_crossing_checkbox").isChecked()

            for direction, input_field in exit_vph_inputs.items():
                value = int(input_field.text()) if input_field.text().isdigit() else 0

                # Checking where the vehicle is coming from, where it is going and if there is a lane for it
                if base_name.startswith("south"):
                    if direction == "West" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Northbound vehicles exiting West require a left turn lane.")
                    if direction == "East" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Northbound vehicles exiting East require a right turn lane.")
                elif base_name.startswith("north"):
                    if direction == "West" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Southbound vehicles exiting West require a right turn lane.")
                    if direction == "East" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Southbound vehicles exiting East require a left turn lane.")
                elif base_name.startswith("west"):
                    if direction == "North" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Eastbound vehicles exiting North require a left turn lane.")
                    if direction == "South" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Eastbound vehicles exiting South require a right turn lane.")
                elif base_name.startswith("east"):
                    if direction == "North" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Westbound vehicles exiting North require a right turn lane.")
                    if direction == "South" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Westbound vehicles exiting South require a right turn lane.")

            # Checking if the number of lanes is enough for the traffic flow
            if (left_turn_lane or right_turn_lane) and lanes < 2:
                invalid_inputs.append(f"{road_name.replace('_', ' ').title()} requires at least 2 lanes if a turn lane is selected.")
            if left_turn_lane and right_turn_lane and lanes < 3:
                invalid_inputs.append(f"{road_name.replace('_', ' ').title()} requires at least 3 lanes if both turn lanes are selected.")

        # Check if pedestrian crossing is consistent
        pedestrian_crossings = []
        for road_name in ["south_traffic_flow", "north_traffic_flow",
                          "west_traffic_flow", "east_traffic_flow"]:
            base_name = road_name.lower().replace(' ', '_')
            pedestrian_crossing = getattr(self, f"{base_name}_pedestrian_crossing_checkbox").isChecked()
            pedestrian_crossings.append(pedestrian_crossing)

        if not all(pedestrian_crossings) and any(pedestrian_crossings):
            invalid_inputs.append("Pedestrian crossing must be enabled for all directions or none.")

        if invalid_inputs:
            QMessageBox.critical(self, "Invalid Inputs", "\n".join(invalid_inputs))
            return False

        return True


    # def update_global_inputs(self):
    #     """ Stores user inputs into the global dictionary for use in simulations. """

    #     if not self.validate_inputs():
    #         return

    #     for road_name in ["south_traffic_flow", "north_traffic_flow", 
    #                       "west_traffic_flow", "east_traffic_flow"]:
            
    #         total_vph = getattr(self, f"{road_name}_total_vph_label").text().split(": ")[1]
    #         lanes = getattr(self, f"{road_name}_lanes_input").value()
    #         bus_lane = getattr(self, f"{road_name}_bus_lane_checkbox").isChecked()
    #         pedestrian_crossing = getattr(self, f"{road_name}_pedestrian_crossing_checkbox").isChecked()
    #         left_turn_lane = getattr(self, f"{road_name}_left_turn_lane_checkbox").isChecked()
    #         right_turn_lane = getattr(self, f"{road_name}_right_turn_lane_checkbox").isChecked()

    #         # Collect exiting VpH values
    #         exit_vphs = {}
    #         for direction, input_field in getattr(self, f"{road_name}_exit_vph_inputs").items():
    #             exit_vphs[direction] = input_field.text()

    #         # Store inputs in the global dictionary
    #         road_inputs[road_name] = {
    #             "total_vph": total_vph,
    #             "lanes": lanes,
    #             "bus_lane": bus_lane,
    #             "pedestrian_crossing": pedestrian_crossing,
    #             "left_turn_lane": left_turn_lane,
    #             "right_turn_lane": right_turn_lane,
    #             "exit_vphs": exit_vphs
    #         }

    #     # Print all inputs to the terminal
    #     for road_name, inputs in road_inputs.items():
    #         print(f"{road_name.replace('_', ' ').title()}:")
    #         print(f"  Total Vehicles per Hour: {inputs['total_vph']}")  
    #         print(f"  Number of Lanes: {inputs['lanes']}")
    #         print(f"  Bus Lane: {inputs['bus_lane']}")
    #         print(f"  Pedestrian Crossing: {inputs['pedestrian_crossing']}")
    #         print(f"  Left Turn Lane: {inputs['left_turn_lane']}")
    #         print(f"  Right Turn Lane: {inputs['right_turn_lane']}")
    #         print("  Exit VpH:", inputs['exit_vphs'])
    #         print()

    def update_global_inputs(self):
        """ Stores user inputs into the global dictionary for use in simulations. """

        if not self.validate_inputs():
            return
        
        # road_names = ["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]

        for road_name in ["south_traffic_flow", "north_traffic_flow", 
                          "west_traffic_flow", "east_traffic_flow"]:
            
            total_vph = getattr(self, f"{road_name}_total_vph_label").text().split(": ")[1]
            lanes = getattr(self, f"{road_name}_lanes_input").value()
            bus_lane = getattr(self, f"{road_name}_bus_lane_checkbox").isChecked()
            pedestrian_crossing = getattr(self, f"{road_name}_pedestrian_crossing_checkbox").isChecked()
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
                "pedestrian_crossing": pedestrian_crossing,
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
            print(f"  Pedestrian Crossing: {inputs['pedestrian_crossing']}")
            print(f"  Left Turn Lane: {inputs['left_turn_lane']}")
            print(f"  Right Turn Lane: {inputs['right_turn_lane']}")
            print("  Exit VpH:", inputs['exit_vphs'])
            print()
