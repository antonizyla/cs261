from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, 
                             QHBoxLayout, QGridLayout, QMessageBox, QVBoxLayout, QScrollArea, QSizePolicy  )
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import os
from directions import CardinalDirection, Turn
from typing import Optional
import sys
from pathlib import Path
sys.path.append((Path(__file__).parent.parent / 'backend').resolve().__str__())
from flowrates import FlowRates
from params import Parameters
from visualisation import JunctionData

# Global variables to store inputs, Note that the direction is the direction traffic comes from

class InputAndParameterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
        print(self.width())

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
        self.junctions_list.add_junction()
    
    def remove_junction(self):
        self.junctions_list.remove_junction()
        
    def update_global_inputs_backend(self):
        # Generates data objects for backend
        if not self.junctions_list.validate_inputs():
            return
        
        junction_outputs = []

        for junction in self.junctions_list.junctions:
            flow_rates = []
            
            for direction in CardinalDirection:
                road_group = junction.road_groups[direction.index]
                
                flow_rates.append(
                    FlowRates(
                        dir_from = direction.to_Dir(), 
                        left = int(road_group.exit_vph_inputs[0].text()),
                        ahead = int(road_group.exit_vph_inputs[1].text()),  
                        right = int(road_group.exit_vph_inputs[2].text()), 
                        dedicated_left = road_group.left_turn_lane_checkbox.isChecked(), 
                        dedicated_bus = road_group.bus_lane_checkbox.isChecked(), 
                        dedicated_right = road_group.right_turn_lane_checkbox.isChecked(), 
                        seq_priority = int(road_group.priority_input.value())
                    )
                )
            parameters = Parameters(
                no_lanes = [junction.road_groups[direction.index].lanes_input.value() for direction in CardinalDirection], 
                dedicated_lane = None, # Not sure whats wanted here 
                dedicated_lane_flow = None, # Not implemented
                pedestrian_crossing = [junction.pedestrian_crossing_checkbox.isChecked()], # Why is an array wanted? 
                crossing_time = None, # Not implemented
                crossing_rph = None, # Not implemented
                sequencing_priority = [junction.road_groups[direction.index].priority_input.value() for direction in CardinalDirection]
            )
            
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


class JunctionInputAndParameterWidget(QGroupBox):
    def __init__(self, count, parent=None):
        name = "Junction " + str(count)
        super().__init__(name, parent)
        
        layout = QGridLayout()
        
        self.road_groups = []
        for direction in CardinalDirection:
            self.road_groups.append(RoadGroupWidget(direction, self))
        for i in range(4):
            layout.addWidget(self.road_groups[i], 0, i, 1, 1) # direction could have been used as an int here, but i think this is clearer
            
        self.pedestrian_crossing_checkbox = QCheckBox("Toggle Pedestrian Crossing")
        layout.addWidget(self.pedestrian_crossing_checkbox, 1, 0, 1, 1)
    
        self.setLayout(layout)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
    
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
                    road_group.left_turn_lane_checkbox.isChecked(),
                    road_group.bus_lane_checkbox.isChecked(),
                    road_group.right_turn_lane_checkbox.isChecked()
                ]
            )
        junction_data[2] = junction.pedestrian_crossing_checkbox.isChecked()
        return JunctionData(junction_data)
    
    
class RoadGroupWidget(QGroupBox):
    def __init__(self, road_source: CardinalDirection, parent: Optional[QWidget] = None) -> None:
        road_name = road_source.simple_string().capitalize() + " Traffic Flow"
        
        super().__init__(road_name, parent)
        
        self.road_direction = road_source
        
        """Creates a group box for each road section with input fields."""
        form_layout = QFormLayout()

        # Total Vehicles per Hour display
        self.total_vph_label = QLabel("Total Vehicles per Hour (VpH): 0")
        form_layout.addRow(self.total_vph_label)

        # Exiting VpH inputs
        self.exit_vph_inputs = []
        for direction in CardinalDirection.all_except_clockwise(road_source - Turn.BACK):
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
        form_layout.addRow(self.lanes_label, self.lanes_input)

        # Checkboxes for lane types
        self.bus_lane_checkbox = QCheckBox("Bus Lane")
        form_layout.addRow(self.bus_lane_checkbox)
        
        self.left_turn_lane_checkbox = QCheckBox("Left Turn Lane")
        form_layout.addRow(self.left_turn_lane_checkbox)
        
        self.right_turn_lane_checkbox = QCheckBox("Right Turn Lane")
        form_layout.addRow(self.right_turn_lane_checkbox)
        self.setLayout(form_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  
        
        self.priority_label = QLabel("Priority:")
        self.priority_input = QSpinBox()
        self.priority_input.setRange(0, 4)
        form_layout.addRow(self.priority_label, self.priority_input)  
    
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
            
        return error_messages