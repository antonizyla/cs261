from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, 
                             QHBoxLayout, QGridLayout, QMessageBox, QVBoxLayout, QScrollArea, QSizePolicy, QButtonGroup  )
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import os
from directions import CardinalDirection, Turn
from typing import Optional, Callable
import sys
from pathlib import Path
sys.path.append((Path(__file__).parent.parent / 'backend').resolve().__str__())
from flowrates import FlowRates
from params import Parameters
from visualisation import JunctionData, JunctionView
from resultsPage import ResultsWidget

# Global variables to store inputs, Note that the direction is the direction traffic comes from
class CopyPaste():
    car_flow_rates: list[list[int]]  = [[0] * 3] * 4

    lane_count: list[int] = [0] * 4

    dedicated_left: list[bool] = [False] * 4
    dedicated_bus: list[bool] = [False] * 4
    dedicated_right: list[bool] = [False] * 4

    priority: list[int] = [0] * 4

    pedestrian_crossing: bool = False
    crossing_rph: int = 0
    crossing_time: int = 0

    valid_paste: bool = False

class InputAndParameterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.check_alternate = 0
        
        # Button to show alt road inputs
        self.add_junction_button = QPushButton("Add Alternative Configuration")
        self.add_junction_button.clicked.connect(self.add_junction)
        
        self.junctions_list = JunctionList()
        self.junctions_list.setWidgetResizable(True)
        
        # Button to show alt road inputs
        self.remove_junction_button = QPushButton("Remove Alternative Configuration")
        self.remove_junction_button.clicked.connect(self.remove_junction)

        # Submit button centered below the grid
        self.submit_button = QPushButton("Start Simulation")
        self.submit_button.setObjectName("submit_button")
        self.submit_button.clicked.connect(self.update_global_inputs_backend)
        
        self.update_layout()
        
        # Load and apply the stylesheet
        self.apply_stylesheet()

    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")
        
    def update_layout(self):
        layout = QGridLayout()
        layout.addWidget(self.junctions_list, 0, 0, 1, -1)
        layout.addWidget(self.add_junction_button, 1, 0, 1, 1)
        layout.addWidget(self.remove_junction_button, 1, 1, 1, 1)
        layout.addWidget(self.submit_button, 2, 0, 1, -1)
        self.setLayout(layout)
    
    def add_junction(self):
        self.check_alternate += 1
        self.junctions_list.add_junction()
    
    def remove_junction(self):
        if self.check_alternate:
            self.junctions_list.remove_junction()
            self.check_alternate -= 1
        else:
            QMessageBox.critical(self, "No Alternate Configurations Set", "Please click the Add Alternate Configuration button to add an alternate configuration")
            return False

        
    def update_global_inputs_backend(self):
        # Generates data objects for backend
        if not self.junctions_list.validate_inputs():
            return
        
        junction_outputs = []

        for junction in self.junctions_list.junctions:
            flow_rates = junction.get_flow_rates()
            
            parameters = junction.get_parameters()
            
            junction_outputs.append((parameters, flow_rates))
        return junction_outputs


class JunctionList(QScrollArea):
    def __init__(self, parent = None):
        super().__init__(parent)
        

        junction = JunctionInputAndParameterWidget(1)        
        self.junctions = [junction]
        
        layout = QGridLayout()
        layout.addWidget(junction, 0, 0, 1, -1, Qt.AlignTop)
        
        self.inner_widget = QWidget(self)
        self.inner_widget.setLayout(layout)
        self.setWidget(self.inner_widget)

        self.setStyleSheet("background-color: #D3D3D3; border-radius: 10px;")

        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")
    
    
    def add_junction(self):
        new_junction = JunctionInputAndParameterWidget(len(self.junctions) + 1)
        self.inner_widget.layout().addWidget(new_junction, len(self.junctions), 0, 1, -1, Qt.AlignTop)
        self.junctions.append(new_junction)
        self.inner_widget.layout().invalidate()
    
    def remove_junction(self):
        if len(self.junctions) == 1:
            return
        layout = self.inner_widget.layout()
        layout.removeWidget(self.junctions.pop(-1))
        layout.invalidate()
    
    def count_junctions(self):
        return len(self.junctions)
    
    def validate_inputs(self):
        error_messages = []
        
        for junction in self.junctions:
            error_messages += junction.validate_inputs()
        
        if len(error_messages) > 0:
            QMessageBox.critical(self, "Invalid Inputs", "\n".join(error_messages))
            return False

        return True
    
    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")


class JunctionInputAndParameterWidget(QGroupBox):
    def __init__(self, count, parent=None):
        name = "Junction " + str(count)
        super().__init__(name, parent)
        
        layout = QGridLayout()
        self.setObjectName("junctiongroup")
        
        self.road_groups = []
        for direction in CardinalDirection:
            self.road_groups.append(RoadGroupWidget(direction, self.update_visualisation, self))
        for i in range(4):
            layout.addWidget(self.road_groups[i], 0, i, 1, 1) # direction could have been used as an int here, but i think this is clearer
            
        self.pedestrian_crossing_checkbox = QCheckBox("Toggle Pedestrian Crossing")
        self.pedestrian_crossing_checkbox.setObjectName("pedestrian_crossing_checkbox")
        layout.addWidget(self.pedestrian_crossing_checkbox, 1, 0, 1, -1)

        crossing_time_layout = QHBoxLayout()
        self.crossing_time_label = QLabel("Crossing Time (s):")
        self.crossing_time_label.setObjectName("crossing_stuff")
        self.crossing_time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.crossing_time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.crossing_time_input = QLineEdit()
        self.crossing_time_input.setValidator(QIntValidator(0, 999))
        self.crossing_time_input.setPlaceholderText("0")
        self.crossing_time_input.setFixedWidth(50)

        self.crossing_time_label.setVisible(False)
        self.crossing_time_input.setVisible(False)

        crossing_time_layout.addWidget(self.crossing_time_label)
        crossing_time_layout.addWidget(self.crossing_time_input)
        crossing_time_layout.addStretch(1)  # Push input closer to label

        # Add the horizontal layout as a single widget in the grid
        layout.addLayout(crossing_time_layout, 2, 0, 1, 2)  # Spanning two columns

        # Create a horizontal layout for Crossing Requests per Hour
        crossing_rph_layout = QHBoxLayout()
        self.crossing_rph_label = QLabel("Crossing Requests per Hour:")
        self.crossing_rph_label.setObjectName("crossing_stuff")
        self.crossing_rph_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.crossing_rph_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.crossing_rph_input = QLineEdit()
        self.crossing_rph_input.setValidator(QIntValidator(0, 999))
        self.crossing_rph_input.setPlaceholderText("0")
        self.crossing_rph_input.setFixedWidth(50)

        self.crossing_rph_label.setVisible(False)
        self.crossing_rph_input.setVisible(False)

        crossing_rph_layout.addWidget(self.crossing_rph_label)
        crossing_rph_layout.addWidget(self.crossing_rph_input)
        crossing_rph_layout.addStretch(1)  # Push input closer to label

        # Add the horizontal layout as a single widget in the grid
        layout.addLayout(crossing_rph_layout, 3, 0, 1, 2)  # Spanning two columns

        self.pedestrian_crossing_checkbox.stateChanged.connect(self.toggle_crossing_inputs)

        

        self.visualisation_checkbox = QCheckBox("Show Visualisation")
        self.visualisation_checkbox.setObjectName("vis_checkbox")
        self.visualisation_checkbox.stateChanged.connect(self.toggle_visualisation)
        layout.addWidget(self.visualisation_checkbox, 4, 0, 1, -1)

        self.copy_button = QPushButton("copy")
        self.copy_button.clicked.connect(self.copy_data)
        layout.addWidget(self.copy_button, 5, 0)

        self.paste_button = QPushButton("Paste")
        self.paste_button.clicked.connect(self.paste_data)
        layout.addWidget(self.paste_button, 5, 1)


        self.visualisation = JunctionView()
    
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.visualisation_hidden = True
    
    def toggle_crossing_inputs(self, state):
            is_checked = state == Qt.Checked
            self.crossing_time_label.setVisible(is_checked)
            self.crossing_time_input.setVisible(is_checked)
            self.crossing_rph_label.setVisible(is_checked)
            self.crossing_rph_input.setVisible(is_checked)
    
    def validate_inputs(self):
        error_messages = []
        
        for direction in CardinalDirection:
            error_messages += self.road_groups[direction.index].validate_inputs()
        
        return [self.title() + ": " + error_message for error_message in error_messages]
    
    def update_global_inputs_frontend(self):
        # Generates data object for visualisation
        junction_data = [[], [], None]
        
        for direction in CardinalDirection:
            junction_data[0].append(self.road_groups[direction.index].lanes_input.value())
            junction_data[1].append(
                [
                    self.road_groups[direction.index].left_turn_lane_checkbox.isChecked(),
                    self.road_groups[direction.index].bus_lane_checkbox.isChecked(),
                    self.road_groups[direction.index].right_turn_lane_checkbox.isChecked()
                ]
            )
        junction_data[2] = self.pedestrian_crossing_checkbox.isChecked()
        return JunctionData(lane_counts = junction_data[0], dedicated_lanes = junction_data[1], has_crosswalk = junction_data[2])
    
    def update_visualisation(self):
        if self.visualisation_hidden:
            return
        self.visualisation.set_junction(self.update_global_inputs_frontend())
        
    def toggle_visualisation(self):
        self.visualisation_hidden = not self.visualisation_hidden

        if self.visualisation_hidden:
            # Move road groups to row 0, spreading across columns
            for i in range(4):
                self.layout().removeWidget(self.road_groups[i])
                self.layout().addWidget(self.road_groups[i], 0, i, 1, 1)

            self.layout().removeWidget(self.pedestrian_crossing_checkbox)
            self.layout().addWidget(self.pedestrian_crossing_checkbox, 1, 0, 1, -1)

            # Remove old label/input widgets
            self.layout().removeWidget(self.crossing_time_label)
            self.layout().removeWidget(self.crossing_time_input)
            self.layout().removeWidget(self.crossing_rph_label)
            self.layout().removeWidget(self.crossing_rph_input)

            # Re-create compact layouts
            crossing_time_layout = QHBoxLayout()
            crossing_time_layout.addWidget(self.crossing_time_label)
            crossing_time_layout.addWidget(self.crossing_time_input)
            crossing_time_layout.addStretch(1)  # Push input closer to the label

            crossing_rph_layout = QHBoxLayout()
            crossing_rph_layout.addWidget(self.crossing_rph_label)
            crossing_rph_layout.addWidget(self.crossing_rph_input)
            crossing_rph_layout.addStretch(1)  # Push input closer to the label

            # Add the layouts back, keeping labels and inputs close together
            self.layout().addLayout(crossing_time_layout, 2, 0, 1, 2)
            self.layout().addLayout(crossing_rph_layout, 3, 0, 1, 2)

            self.layout().removeWidget(self.visualisation_checkbox)
            self.layout().addWidget(self.visualisation_checkbox, 4, 0, 1, -1)

            self.layout().removeWidget(self.copy_button)
            self.layout().addWidget(self.copy_button, 5, 0)

            self.layout().removeWidget(self.paste_button)
            self.layout().addWidget(self.paste_button, 5, 1)

            self.layout().removeWidget(self.visualisation)
            self.visualisation.hide()
            return
        
        for i in range(4):
            self.layout().removeWidget(self.road_groups[i])
            self.layout().addWidget(self.road_groups[i], int(i/2), i%2, 1, 1)
            
        self.layout().removeWidget(self.pedestrian_crossing_checkbox)
        self.layout().addWidget(self.pedestrian_crossing_checkbox, 2, 0, 1, 2)

        # Remove widgets from layout
        self.layout().removeWidget(self.crossing_time_label)
        self.layout().removeWidget(self.crossing_time_input)
        self.layout().removeWidget(self.crossing_rph_label)
        self.layout().removeWidget(self.crossing_rph_input)

        # Create a compact layout for Crossing Time
        crossing_time_layout = QHBoxLayout()
        crossing_time_layout.addWidget(self.crossing_time_label)
        crossing_time_layout.addWidget(self.crossing_time_input)
        crossing_time_layout.addStretch(1)  # Push input closer to the label

        # Create a compact layout for Crossing Requests per Hour
        crossing_rph_layout = QHBoxLayout()
        crossing_rph_layout.addWidget(self.crossing_rph_label)
        crossing_rph_layout.addWidget(self.crossing_rph_input)
        crossing_rph_layout.addStretch(1)  # Push input closer to the label

        # Add the layouts back in the new positions
        self.layout().addLayout(crossing_time_layout, 3, 0, 1, 2)  # Span across two columns
        self.layout().addLayout(crossing_rph_layout, 4, 0, 1, 2)  # Span across two columns

        self.layout().removeWidget(self.visualisation_checkbox)
        self.layout().addWidget(self.visualisation_checkbox, 5, 0, 1, 2)

        self.layout().removeWidget(self.copy_button)
        self.layout().addWidget(self.copy_button, 6, 0)

        self.layout().removeWidget(self.paste_button)
        self.layout().addWidget(self.paste_button, 6, 1)

        self.visualisation.set_junction(self.update_global_inputs_frontend())
        self.layout().addWidget(self.visualisation, 0, 2, 2, 2)
        self.visualisation.show()
    
    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")
    
    def copy_data(self):
        # CopyPaste.data = (self.get_flow_rates(), self.get_parameters()) - was going to do this, but wont work for invalid data
        
        CopyPaste.pedestrian_crossing = self.pedestrian_crossing_checkbox.isChecked()
        CopyPaste.crossing_rph = self.crossing_time_input.text()
        CopyPaste.crossing_time = self.crossing_rph_input.text()

        for i in range(4):
            self.road_groups[i].copy_data()
        
        CopyPaste.valid_paste = True

    def paste_data(self):
        if not CopyPaste.valid_paste:
            return

        self.pedestrian_crossing_checkbox.setChecked(CopyPaste.pedestrian_crossing)
        self.crossing_time_input.setText(CopyPaste.crossing_rph)
        self.crossing_rph_input.setText(CopyPaste.crossing_time)

        for i in range(4):
            self.road_groups[i].paste_data()
        
    def get_flow_rates(self):
        flow_rates_list = []
            
        for direction in CardinalDirection:
            road_group = self.road_groups[direction.index]
            
            flow_rates_list.append(
                FlowRates(
                    dir_from = direction.to_Dir(), 
                    left = int(road_group.exit_vph_inputs[0].text()),
                    ahead = int(road_group.exit_vph_inputs[1].text()),  
                    right = int(road_group.exit_vph_inputs[2].text()), 
                    dedicated_left = road_group.left_turn_lane_checkbox.isChecked(), 
                    dedicated_bus = road_group.bus_lane_checkbox.isChecked(), 
                    dedicated_right = road_group.right_turn_lane_checkbox.isChecked()
                )
            )
        return flow_rates_list
    
    def get_parameters(self):
        parameters = Parameters(
            no_lanes = [self.road_groups[direction.index].lanes_input.value() for direction in CardinalDirection], 

            # Note: backend used to (or still does?) assume that crossings are independent, frontend assumes they are all identical
            pedestrian_crossing = [self.pedestrian_crossing_checkbox.isChecked()] * 4,
            crossing_time = [int(self.crossing_time_input.text()) if self.pedestrian_crossing_checkbox.isChecked() else 0] * 4,
            crossing_rph = [int(self.crossing_rph_input.text()) if self.pedestrian_crossing_checkbox.isChecked() else 0] * 4,

            sequencing_priority = [self.road_groups[direction.index].priority_input.value() for direction in CardinalDirection]
        )
        return parameters
    

class RoadGroupWidget(QGroupBox):
    def __init__(self, road_source: CardinalDirection, update_visualisation: Callable[None, None], parent: Optional[QWidget] = None) -> None:
        road_name = road_source.simple_string().capitalize() + " Traffic Flow"
        
        super().__init__(road_name, parent)
        
        self.road_direction = road_source
        self.setObjectName("road_group")
        
        """Creates a group box for each road section with input fields."""
        form_layout = QFormLayout()

        # Total Vehicles per Hour display
        self.total_vph_label = QLabel("Total Vehicles per Hour (VpH): 0")
        form_layout.addRow(self.total_vph_label)

        # Exiting VpH inputs
        self.exit_vph_inputs = []
        for direction in CardinalDirection.all_except_clockwise(road_source):
            exit_label = QLabel(f"Exiting {direction.simple_string()}:")

            exit_input = QLineEdit()
            exit_input.setValidator(QIntValidator(0, 999))
            exit_input.setPlaceholderText("0")  
            exit_input.textChanged.connect(self.update_total_vph)
            self.exit_vph_inputs.append(exit_input)
            
            form_layout.addRow(exit_label, exit_input)
            
        # Number of lanes input
        self.lanes_label = QLabel("Number of Lanes:")
        self.lanes_input = QSpinBox()
        self.lanes_input.setRange(1, 5)
        self.lanes_input.valueChanged.connect(update_visualisation)
        form_layout.addRow(self.lanes_label, self.lanes_input)

        # Checkboxes for lane types
        self.bus_lane_checkbox = QCheckBox("Bus Lane")
        self.bus_lane_checkbox.stateChanged.connect(update_visualisation)
        self.bus_lane_checkbox.stateChanged.connect(self.select_bus)
        form_layout.addRow(self.bus_lane_checkbox)
        
        self.left_turn_lane_checkbox = QCheckBox("Left Turn Lane")
        self.left_turn_lane_checkbox.stateChanged.connect(update_visualisation)
        self.left_turn_lane_checkbox.stateChanged.connect(self.select_left)
        form_layout.addRow(self.left_turn_lane_checkbox)
        
        self.right_turn_lane_checkbox = QCheckBox("Right Turn Lane")
        self.right_turn_lane_checkbox.stateChanged.connect(update_visualisation)
        form_layout.addRow(self.right_turn_lane_checkbox)
        self.setLayout(form_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  
        
        self.priority_label = QLabel("Priority:")
        self.priority_input = QSpinBox()
        self.priority_input.setRange(0, 4)
        form_layout.addRow(self.priority_label, self.priority_input)  
    
    def select_bus(self):
        if self.bus_lane_checkbox.isChecked():
            self.left_turn_lane_checkbox.setChecked(False)

    def select_left(self):
        if self.left_turn_lane_checkbox.isChecked():
            self.bus_lane_checkbox.setChecked(False)

    def update_total_vph(self):
        """ Updates the total VpH label based on the sum of exit values. """
        try:
            total_vph = sum(int(input_field.text()) if input_field.text().isdigit() else 0 
                           for input_field in self.exit_vph_inputs)
        except ValueError:
            total_vph = 0  

        self.total_vph_label.setText(f"Total Vehicles per Hour (VpH): {total_vph}")    

    def validate_inputs(self) -> Optional[list[str]]:      
        if not all([self.exit_vph_inputs[i].text().isdigit() for i in range(3)]):
            return [f"{self.title()} requires valid traffic flows for each direction."]
        
        has_left_lane = self.left_turn_lane_checkbox.isChecked()
        has_right_lane = self.right_turn_lane_checkbox.isChecked()
        undedicated_lanes = self.lanes_input.value() - (has_left_lane + has_right_lane)        

        has_left_vehicles = (int(self.exit_vph_inputs[0].text()) > 0)
        has_ahead_vehicles = (int(self.exit_vph_inputs[1].text()) > 0)
        has_right_vehicles = (int(self.exit_vph_inputs[2].text()) > 0)
        
        error_messages = []
        
        if undedicated_lanes < 0:
            error_messages.append(f"{self.title()} does not have enough lanes to supply the selected dedicates lanes.")
        elif undedicated_lanes == 0 and has_ahead_vehicles:
            error_messages.append(f"{self.title()} does not have enough undedicated lanes.")
        
        invalid_left = has_left_vehicles and not has_left_lane and (undedicated_lanes <= 0)
        invalid_right = has_right_vehicles and not has_right_lane and (undedicated_lanes <= 0)
        
        if invalid_left:
            if invalid_right:
                error_messages.append(f"{self.title()} requires a dedicated left and right lane, or at least one undedicated lane.")
            error_messages.append(f"{self.title()} requires a dedicated left lane, or at least one undedicated lane.")
        elif invalid_right:
            error_messages.append(f"{self.title()} requires a dedicated right lane, or at least one undedicated lane.")

        if self.parent().pedestrian_crossing_checkbox.isChecked():
            if not self.parent().crossing_time_input.text().isdigit() or not self.parent().crossing_rph_input.text().isdigit():
                if "Crossing time and Requests per Hour cannot be empty" not in error_messages:
                    error_messages.append("Crossing time and Requests per Hour cannot be empty")

        return error_messages
    
    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")


    def copy_data(self):
        i = self.road_direction.index

        CopyPaste.car_flow_rates[i] = [self.exit_vph_inputs[j].text() for j in range(3)]

        CopyPaste.lane_count[i] = self.lanes_input.value()

        CopyPaste.dedicated_left[i] = self.left_turn_lane_checkbox.isChecked()
        CopyPaste.dedicated_bus[i] = self.bus_lane_checkbox.isChecked()
        CopyPaste.dedicated_right[i] = self.right_turn_lane_checkbox.isChecked()

        CopyPaste.priority[i] = self.priority_input.value()

    def paste_data(self):
        i = self.road_direction.index
        for j in range(3):
            self.exit_vph_inputs[j].setText(CopyPaste.car_flow_rates[i][j])

        self.lanes_input.setValue(CopyPaste.lane_count[i])

        self.left_turn_lane_checkbox.setChecked(CopyPaste.dedicated_left[i])
        self.bus_lane_checkbox.setChecked(CopyPaste.dedicated_bus[i])
        self.right_turn_lane_checkbox.setChecked(CopyPaste.dedicated_right[i])

        self.priority_input.setValue(CopyPaste.priority[i])


