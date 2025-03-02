from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, 
                             QHBoxLayout, QGridLayout, QMessageBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import os
from junctionDetails import JunctionDetails, Directions
import sys
sys.path.append('../backend')
from flowrates import FlowRates

# Global variables to store inputs, Note that the direction is the direction traffic comes from
road_inputs = {
    "south_traffic_flow": {},
    "west_traffic_flow": {},
    "east_traffic_flow": {},
    "north_traffic_flow": {}
}

alt_road_inputs = {
    "alt_south_traffic_flow": {},
    "alt_west_traffic_flow": {},
    "alt_east_traffic_flow": {},
    "alt_north_traffic_flow": {}
}

class InputAndParameterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load and apply the stylesheet
        self.apply_stylesheet()

        # Main grid layout (2x2)
        self.main_layout = QGridLayout()

        # Create road groups and assign them to grid
        self.north_group = self.create_road_group("South Traffic Flow", ["North", "East", "West"])
        self.south_group = self.create_road_group("North Traffic Flow", ["South", "East", "West"])
        self.east_group = self.create_road_group("West Traffic Flow", ["East", "North", "South"])
        self.west_group = self.create_road_group("East Traffic Flow", ["West", "North", "South"])

        # Alt road groups
        self.alt_south_group = self.create_road_group("Alt South Traffic Flow", ["North", "East", "West"])
        self.alt_north_group = self.create_road_group("Alt North Traffic Flow", ["South", "East", "West"])
        self.alt_west_group = self.create_road_group("Alt West Traffic Flow", ["East", "North", "South"])
        self.alt_east_group = self.create_road_group("Alt East Traffic Flow", ["West", "North", "South"])

        # Arrange in a 4x2 grid
        self.main_layout.addWidget(self.north_group, 0, 0)
        self.main_layout.addWidget(self.south_group, 0, 1)
        self.main_layout.addWidget(self.east_group, 0, 2)
        self.main_layout.addWidget(self.west_group, 0, 3)

        # Initially hide alt road groups
        self.alt_north_group.setVisible(False)
        self.alt_south_group.setVisible(False)
        self.alt_east_group.setVisible(False)
        self.alt_west_group.setVisible(False)

        # Add alt road groups to the layout but keep them hidden
        self.main_layout.addWidget(self.alt_north_group, 1, 0)
        self.main_layout.addWidget(self.alt_south_group, 1, 1)
        self.main_layout.addWidget(self.alt_east_group, 1, 2)
        self.main_layout.addWidget(self.alt_west_group, 1, 3)

        # Pedestrian crossing buttons
        self.pedestrian_crossing_button = QPushButton("Toggle Pedestrian Crossing (Main Roads)")
        self.pedestrian_crossing_button.clicked.connect(self.toggle_pedestrian_crossing_main)
        self.main_layout.addWidget(self.pedestrian_crossing_button, 2, 0, 1, 2)  # Initially spans two columns

        self.alt_pedestrian_crossing_button = QPushButton("Toggle Pedestrian Crossing (Alt Roads)")
        self.alt_pedestrian_crossing_button.clicked.connect(self.toggle_pedestrian_crossing_alt)
        self.alt_pedestrian_crossing_button.hide()  # Initially hide
        self.main_layout.addWidget(self.alt_pedestrian_crossing_button, 2, 2, 1, 2)

        # Button to show alt road inputs
        self.show_alt_inputs_button = QPushButton("Add Alternate Road Inputs")
        self.show_alt_inputs_button.clicked.connect(self.show_alt_inputs)
        self.main_layout.addWidget(self.show_alt_inputs_button, 3, 0, 1, 4)  # Spans four columns

        # Submit button centered below the grid
        self.submit_button = QPushButton("Start Simulation")
        self.submit_button.setObjectName("submit_button")
        self.submit_button.clicked.connect(self.update_global_inputs)
        self.main_layout.addWidget(self.submit_button, 4, 0, 1, 4)  # Spans four columns

        self.setLayout(self.main_layout)

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

    def toggle_pedestrian_crossing_main(self):
        """ Toggles pedestrian crossing for main road inputs. """
        for road_name in ["south_traffic_flow", "north_traffic_flow", 
                          "west_traffic_flow", "east_traffic_flow"]:
            checkbox = getattr(self, f"{road_name}_pedestrian_crossing_checkbox")
            checkbox.setChecked(not checkbox.isChecked())

    def toggle_pedestrian_crossing_alt(self):
        """ Toggles pedestrian crossing for alt road inputs. """
        for road_name in ["alt_south_traffic_flow", "alt_north_traffic_flow", 
                          "alt_west_traffic_flow", "alt_east_traffic_flow"]:
            checkbox = getattr(self, f"{road_name}_pedestrian_crossing_checkbox")
            checkbox.setChecked(not checkbox.isChecked())

    def show_alt_inputs(self):
        """ Shows the alternate road input configurations. """
        self.alt_north_group.setVisible(True)
        self.alt_south_group.setVisible(True)
        self.alt_east_group.setVisible(True)
        self.alt_west_group.setVisible(True)
        self.alt_pedestrian_crossing_button.setVisible(True)
        
        self.layout().removeWidget(self.show_alt_inputs_button)
        # Button to hide alt road inputs
        self.hide_alt_inputs_button = QPushButton("Hide Alternate Road Inputs")
        self.hide_alt_inputs_button.clicked.connect(self.hide_alt_inputs)
        self.main_layout.addWidget(self.hide_alt_inputs_button, 3, 0, 1, 4)  # Spans four columns

        # Ensuring the layout updates properly
        self.layout().invalidate()

    def hide_alt_inputs(self):
        """ Hides the alternate road input configurations. """
        self.alt_north_group.setVisible(False)
        self.alt_south_group.setVisible(False)
        self.alt_east_group.setVisible(False)
        self.alt_west_group.setVisible(False)
        self.alt_pedestrian_crossing_button.setVisible(False)
        
        self.layout().removeWidget(self.hide_alt_inputs_button)
        # Button to show alt road inputs
        self.show_alt_inputs_button = QPushButton("Add Alternate Road Inputs")
        self.show_alt_inputs_button.clicked.connect(self.show_alt_inputs)
        self.main_layout.addWidget(self.show_alt_inputs_button, 3, 0, 1, 4)  # Spans four columns

        # Ensuring the layout updates properly
        self.layout().invalidate()

    def validate_inputs(self):
        invalid_inputs = []
        for road_name in ["south_traffic_flow", "north_traffic_flow",
                          "west_traffic_flow", "east_traffic_flow",
                          "alt_south_traffic_flow", "alt_north_traffic_flow",
                          "alt_west_traffic_flow", "alt_east_traffic_flow"]:

            base_name = road_name.lower().replace(' ', '_')
            exit_vph_inputs = getattr(self, f"{base_name}_exit_vph_inputs")
            left_turn_lane = getattr(self, f"{base_name}_left_turn_lane_checkbox").isChecked()
            right_turn_lane = getattr(self, f"{base_name}_right_turn_lane_checkbox").isChecked()
            lanes = getattr(self, f"{base_name}_lanes_input").value()
            pedestrian_crossing = getattr(self, f"{base_name}_pedestrian_crossing_checkbox").isChecked()

            for direction, input_field in exit_vph_inputs.items():
                value = int(input_field.text()) if input_field.text().isdigit() else 0

                # Checking where the vehicle is coming from, where it is going and if there is a lane for it
                if base_name.startswith("south") or base_name.startswith("alt_south"):
                    if direction == "West" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Vehicles coming from the South and exiting West require a left turn lane.")
                    if direction == "East" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Vehicles coming from the south and exiting East require a right turn lane.")
                elif base_name.startswith("north") or base_name.startswith("alt_north"):
                    if direction == "West" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Vehicles coming from the North and exiting West require a right turn lane.")
                    if direction == "East" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Vehicles coming from the North and exiting East require a left turn lane.")
                elif base_name.startswith("west") or base_name.startswith("alt_west"):
                    if direction == "North" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Vehicles coming from the West and exiting North require a left turn lane.")
                    if direction == "South" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Vehicles coming from the West and exiting South require a right turn lane.")
                elif base_name.startswith("east") or base_name.startswith("alt_east"):
                    if direction == "North" and value > 0 and not left_turn_lane:
                        invalid_inputs.append("Vehicles coming from the East and exiting North require a right turn lane.")
                    if direction == "South" and value > 0 and not right_turn_lane:
                        invalid_inputs.append("Vehicles coming from the East and exiting South require a right turn lane.")

            # Checking if the number of lanes is enough for the traffic flow
            if (left_turn_lane or right_turn_lane) and lanes < 2:
                invalid_inputs.append(f"{road_name.replace('_', ' ').title()} requires at least 2 lanes if a turn lane is selected.")
            if left_turn_lane and right_turn_lane and lanes < 3:
                invalid_inputs.append(f"{road_name.replace('_', ' ').title()} requires at least 3 lanes if both turn lanes are selected.")

        # Check if pedestrian crossing is consistent for main inputs
        main_pedestrian_crossings = []
        for road_name in ["south_traffic_flow", "north_traffic_flow",
                  "west_traffic_flow", "east_traffic_flow"]:
            
            base_name = road_name.lower().replace(' ', '_')
            pedestrian_crossing = getattr(self, f"{base_name}_pedestrian_crossing_checkbox").isChecked()
            main_pedestrian_crossings.append(pedestrian_crossing)

        if not all(main_pedestrian_crossings) and any(main_pedestrian_crossings):
            invalid_inputs.append("Pedestrian crossing must be enabled for all main directions or none.")

        # Check if pedestrian crossing is consistent for alt inputs
        alt_pedestrian_crossings = []
        for road_name in ["alt_south_traffic_flow", "alt_north_traffic_flow",
                  "alt_west_traffic_flow", "alt_east_traffic_flow"]:
            
            base_name = road_name.lower().replace(' ', '_')
            pedestrian_crossing = getattr(self, f"{base_name}_pedestrian_crossing_checkbox").isChecked()
            alt_pedestrian_crossings.append(pedestrian_crossing)

        if not all(alt_pedestrian_crossings) and any(alt_pedestrian_crossings):
            invalid_inputs.append("Pedestrian crossing must be enabled for all alt directions or none.")

        if invalid_inputs:
            QMessageBox.critical(self, "Invalid Inputs", "\n".join(invalid_inputs))
            return False

        return True

    def update_global_inputs(self):
        """ Stores user inputs into the global dictionary for use in simulations. """

        if not self.validate_inputs():
            return

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
