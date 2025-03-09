import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, 
                             QHBoxLayout, QMessageBox, QGridLayout, QSizePolicy, QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
import mplcursors
import numpy as np
import mplcursors



# Global variables to store results
road_results = {
    "south_traffic_flow": {},
    "west_traffic_flow": {},
    "east_traffic_flow": {},
    "north_traffic_flow": {}
}

alt_road_results = {
    "alt_south_traffic_flow": {},
    "alt_west_traffic_flow": {},
    "alt_east_traffic_flow": {},
    "alt_north_traffic_flow": {}
}

alt1_road_results = {
    "alt1_south_traffic_flow": {},
    "alt1_west_traffic_flow": {},
    "alt1_east_traffic_flow": {},
    "alt1_north_traffic_flow": {}
}

alt2_road_results = {
    "alt2_south_traffic_flow": {},
    "alt2_west_traffic_flow": {},
    "alt2_east_traffic_flow": {},
    "alt2_north_traffic_flow": {}
}
alt3_road_results = {
    "alt3_south_traffic_flow": {},
    "alt3_west_traffic_flow": {},
    "alt3_east_traffic_flow": {},
    "alt3_north_traffic_flow": {}
}

class ResultsWidget(QWidget):
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.number = number

        # Checks if the results have been generated
        self.results_generated = False
        
        self.apply_stylesheet()

        # Use a grid layout for the road groups
        main_layout = QGridLayout()
        main_layout.setSpacing(5)  # Reduce spacing for a more compact layout

        # Create road result groups in a 2x2 grid
        self.create_road_group(main_layout, "South Traffic Flow", 0, 0)  # Top-left
        self.create_road_group(main_layout, "North Traffic Flow", 0, 1)  # Top-right
        self.create_road_group(main_layout, "West Traffic Flow", 1, 0)   # Bottom-left
        self.create_road_group(main_layout, "East Traffic Flow", 1, 1)   # Bottom-right

        # Button to generate results

        # Button to get report
        self.generate_report_button = QPushButton("Download Report as PDF") 
        self.generate_report_button.clicked.connect(self.get_report)
        main_layout.addWidget(self.generate_report_button, 2, 0, 1, 2)  # Bottom-right

        
        self.go_inputs_button = QPushButton("Run Simulation Again")
        main_layout.addWidget(self.go_inputs_button, 3, 0, 1, 2)  # Bottom

        self.exit_button = QPushButton("Exit")
        self.exit_button.setObjectName("exitButton")
        main_layout.addWidget(self.exit_button, 4, 0, 1, 2)  # Bottom


        # Set the layout of the main widget
        layout = QVBoxLayout()
        layout.addLayout(main_layout)
        self.setLayout(layout)

    def update_junctions(self, number_junctions):
        self.number = number_junctions
        print(f"Number of junctions updated to: {number_junctions}")


    def apply_stylesheet(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'stylesheet.qss'), 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")


    def create_road_group(self, layout, road_name, row, col):
        # Create the group container with an empty form layout (no result labels)
        group_box = QGroupBox()
        group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout = QFormLayout()
        form_layout.setContentsMargins(5, 5, 5, 5)

        # Create a toggle button for collapsing/expanding
        toggle_button = QToolButton()
        toggle_button.setText(road_name + " ▼")
        toggle_button.setCheckable(True)
        toggle_button.setChecked(True)
        toggle_button.clicked.connect(lambda: self.toggle_group(toggle_button, group_box, road_name))

        header_layout = QHBoxLayout()
        header_layout.addWidget(toggle_button)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch()

        # Instead of adding result labels, only add an empty row
        form_layout.addRow(QWidget())

        # Store the layout and prepare for chart insertion later
        base_name = road_name.lower().replace(' ', '_')
        setattr(self, f"{base_name}_chart", None)
        setattr(self, f"{base_name}_form_layout", form_layout)

        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        # Assemble the group box and add it to the provided layout grid
        group_box.setLayout(form_layout)
        group_box_layout = QVBoxLayout()
        group_box_layout.setContentsMargins(0, 0, 0, 0)
        group_box_layout.addWidget(header_widget)
        group_box_layout.addWidget(group_box)
        layout.addLayout(group_box_layout, row, col)

        placeholder = QLabel("Click the 'Generate Results' button to get results. "
        "\nResults will be displayed here as charts. The three categories will be:")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px")
        form_layout.addRow(placeholder)

        # Labels for results (default placeholders)
        avg_wait_label = QLabel("Average Wait Time")
        max_wait_label = QLabel("Max Wait Time")
        max_queue_label = QLabel("Max Queue Length")


        instruction = QLabel("When the results are generated, hover over the bars to see the exact values."
        "\nRight-click on the annotation to remove it (Secondary Click on MacOS).")
        
        # Add the labels to the grid layout
        form_layout.addWidget(avg_wait_label)
        form_layout.addWidget(max_wait_label)
        form_layout.addWidget(max_queue_label)

        form_layout.addWidget(instruction)
  
        setattr(self, f"{base_name}_avg_wait_label", avg_wait_label)
        setattr(self, f"{base_name}_max_wait_label", max_wait_label)
        setattr(self, f"{base_name}_max_queue_label", max_queue_label)


    def toggle_group(self, toggle_button, group_box, road_name):
        """ Toggles the visibility of the group box content. """
        if toggle_button.isChecked():
            toggle_button.setText(road_name + " ▼")  # Show the content
            group_box.setVisible(True)
        else:
            toggle_button.setText(road_name + " ►")  # Hide the content
            group_box.setVisible(False)

    def get_results(self, results):
        # Process the 3D results list.
        # Assume each junction’s data is structured as:
        # junction = [ [avg, max, queue] for each road direction in order:
        #              south, north, west, east, 
        #              overall_score ] where the overall score is the last element.
        # First, create a list to hold overall scores per junction.
        self.overall_scores = []
        # Initialize metrics for up to 5 configurations if needed.
        # Each configuration will have one list per road direction (order: south, north, west, east).
        # For configuration 1:
        self.average_wait = [0, 0, 0, 0]
        self.max_wait_time = [0, 0, 0, 0]
        self.max_queue_length = [0, 0, 0, 0]
        # For configuration 2:
        self.alt_avg_wait = [0, 0, 0, 0]
        self.alt_max_wait_time = [0, 0, 0, 0]
        self.alt_max_queue_length = [0, 0, 0, 0]
        # For configuration 3:
        self.alt1_avg_wait = [0, 0, 0, 0]
        self.alt1_max_wait_time = [0, 0, 0, 0]
        self.alt1_max_queue_length = [0, 0, 0, 0]
        # For configuration 4:
        self.alt2_avg_wait = [0, 0, 0, 0]
        self.alt2_max_wait_time = [0, 0, 0, 0]
        self.alt2_max_queue_length = [0, 0, 0, 0]
        # For configuration 5:
        self.alt3_avg_wait = [0, 0, 0, 0]
        self.alt3_max_wait_time = [0, 0, 0, 0]
        self.alt3_max_queue_length = [0, 0, 0, 0]

        # Loop through each junction's results.
        for j, junction_data in enumerate(results):
            # The last element of each junction list is the overall score.
            overall = int(junction_data[-1])
            self.overall_scores.append(overall)
            # For the four road directions, assign metrics.
            for i in range(4):
                metrics = junction_data[i]  # Expected to be [avg_wait, max_wait, max_queue]
                if j == 0:
                    self.average_wait[i] = metrics[0]
                    print(f"Average wait time for junction {i+1} is {self.average_wait[i]}")

                    self.max_wait_time[i] = metrics[1]
                    print(f"Max wait time for junction {i+1} is {self.max_wait_time[i]}")

                    self.max_queue_length[i] = metrics[2]
                    print(f"Max queue length for junction {i+1} is {self.max_queue_length[i]}")
                elif j == 1:
                    self.alt_avg_wait[i] = metrics[0]
                    print(f"Average wait time for junction {i+1} is {self.alt_avg_wait[i]}")
                    self.alt_max_wait_time[i] = metrics[1]
                    print(f"Max wait time for junction {i+1} is {self.alt_max_wait_time[i]}")
                    self.alt_max_queue_length[i] = metrics[2]
                    print(f"Max queue length for junction {i+1} is {self.alt_max_queue_length[i]}")
                elif j == 2:
                    self.alt1_avg_wait[i] = metrics[0]
                    print(f"Average wait time for junction {i+1} is {self.alt1_avg_wait[i]}")
                    self.alt1_max_wait_time[i] = metrics[1]
                    print(f"Max wait time for junction {i+1} is {self.alt1_max_wait_time[i]}")
                    self.alt1_max_queue_length[i] = metrics[2]
                    print(f"Max queue length for junction {i+1} is {self.alt1_max_queue_length[i]}")
                elif j == 3:
                    self.alt2_avg_wait[i] = metrics[0]
                    self.alt2_max_wait_time[i] = metrics[1]
                    self.alt2_max_queue_length[i] = metrics[2]
                elif j == 4:
                    self.alt3_avg_wait[i] = metrics[0]
                    self.alt3_max_wait_time[i] = metrics[1]
                    self.alt3_max_queue_length[i] = metrics[2]
        self.results_generated = True
        

        for road_name in ["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]:
            base_name = road_name.lower().replace(' ', '_')
            form_layout = getattr(self, f"{base_name}_form_layout")
            # Remove any QLabel widget (e.g., the placeholder) from the form layout
            for i in reversed(range(form_layout.count())):
                widget = form_layout.itemAt(i).widget()
                if widget and widget.__class__.__name__ == "QLabel":
                    form_layout.removeWidget(widget)
                    widget.deleteLater()

        print(f"Number of junctions is : {self.number}")
        # Create overall score labels based on the number of junctions
        # Remove old overall scores layout if it exists
        if hasattr(self, 'overall_layout'):
            self.layout().removeItem(self.overall_layout)
            while self.overall_layout.count():
                item = self.overall_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Create new overall scores layout with a maximum of two labels per row
        self.overall_layout = QGridLayout()
        for i in range(self.number):
            overall_label = QLabel(f"Overall Score (Junction {i+1}): {self.overall_scores[i]}")
            overall_label.setAlignment(Qt.AlignCenter)
            overall_label.setObjectName("overallScoreLabel")
            row = i // 2
            col = i % 2
            # If it's the only label in the row, span across both columns
            if (self.number % 2 != 0) and (i == self.number - 1):
                self.overall_layout.addWidget(overall_label, row, 0, 1, 2)
            else:
                self.overall_layout.addWidget(overall_label, row, col)
        self.layout().insertLayout(0, self.overall_layout)


        # Update the main configuration charts
        for idx, road_name in enumerate(["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]):
            base_name = road_name.lower().replace(' ', '_')
            existing_chart = getattr(self, f"{base_name}_chart", None)
            if existing_chart:
                form_layout = getattr(self, f"{base_name}_form_layout")
                form_layout.removeWidget(existing_chart)
                existing_chart.deleteLater()
                setattr(self, f"{base_name}_chart", None)
            road_results[road_name] = {
                "average_wait": self.average_wait[idx],
                "max_wait_times": self.max_wait_time[idx],
                "max_queue_length": self.max_queue_length[idx],
            }
            self.update_chart(road_name, idx)

        # Update the alternative configuration charts
        for idx, alt_road_name in enumerate(["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]):
            base_name = alt_road_name.lower().replace(' ', '_')
            existing_chart = getattr(self, f"{base_name}_chart", None)
            if existing_chart:
                form_layout = getattr(self, f"{base_name}_form_layout")
                form_layout.removeWidget(existing_chart)
                existing_chart.deleteLater()
                setattr(self, f"{base_name}_chart", None)
            alt_road_results[alt_road_name] = {
                "average_wait": self.alt_avg_wait[idx],
                "max_wait_times": self.alt_max_wait_time[idx],
                "max_queue_length": self.alt_max_queue_length[idx],
            }
            self.update_chart(alt_road_name, idx)

    def get_report(self):
        """Generates a PDF report with the results and bar charts using ReportLab."""

        if self.results_generated:
            # Ask the user where to save the PDF
            options = QFileDialog.Options()
            #options |= QFileDialog.DontUseNativeDialog  UNCOMMENT THIS LINE IF SAVE DOESNT WORK ON WINDOWS/LINUX
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "PDF Files (*.pdf);;All Files (*)", options=options)

            if not file_path:
                return  # User canceled the save dialog
            
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"

            # Create a PDF canvas
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, height - 36, "Simulation Results Report")
            c.setFont("Helvetica", 12)
            c.drawString(40, height - 55, "Below are the results of the simulation.")
            y_position = height - 75

            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y_position, "Overall Scores:")
            y_position -= 20
            for i in range(self.number):
                c.setFont("Helvetica", 11)
                c.drawString(40, y_position, f"Junction {i+1} Overall Score: {self.overall_scores[i]}")
                y_position -= 15
            y_position -= 10

            directions = ["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]
            for idx, road_name in enumerate(directions):
                base_name = road_name  # The direction index corresponds to idx in the result arrays.
                section_title = road_name.replace('_', ' ').title() + " Results"

                # Section Title
                c.setFont("Helvetica-Bold", 14)
                c.drawString(40, y_position, section_title)
                y_position -= 10  # Increased spacing

                # Header for Main and Alternative configurations
                c.setFont("Helvetica-Bold", 12)
                y_position -= 20

                # Print result sets for each junction configuration (using j+1)
                for j in range(self.number):
                    config_num = j + 1
                    c.setFont("Helvetica", 11)
                    if config_num == 1:
                        result = (
                            f"Avg Wait: {self.average_wait[idx]} sec, "
                            f"Max Wait: {self.max_wait_time[idx]} sec, "
                            f"Max Queue: {self.max_queue_length[idx]} cars"
                        )
                    elif config_num == 2:
                        result = (
                            f"Avg Wait: {self.alt_avg_wait[idx]} sec, "
                            f"Max Wait: {self.alt_max_wait_time[idx]} sec, "
                            f"Max Queue: {self.alt_max_queue_length[idx]} cars"
                        )
                    elif config_num == 3:
                        result = (
                            f"Avg Wait: {self.alt1_avg_wait[idx]} sec, "
                            f"Max Wait: {self.alt1_max_wait_time[idx]} sec, "
                            f"Max Queue: {self.alt1_max_queue_length[idx]} cars"
                        )
                    elif config_num == 4:
                        result = (
                            f"Avg Wait: {self.alt2_avg_wait[idx]} sec, "
                            f"Max Wait: {self.alt2_max_wait_time[idx]} sec, "
                            f"Max Queue: {self.alt2_max_queue_length[idx]} cars"
                        )
                    elif config_num == 5:
                        result = (
                            f"Avg Wait: {self.alt3_avg_wait[idx]} sec, "
                            f"Max Wait: {self.alt3_max_wait_time[idx]} sec, "
                            f"Max Queue: {self.alt3_max_queue_length[idx]} cars"
                        )
                    else:
                        result = "No data available"
                    c.drawString(40, y_position, f"Junction {config_num}: {result}")
                    y_position -= 20  # Decrement y_position after each result

                y_position -= 10  # Adjust spacing after each junction's output

                # Add the chart directly to the PDF without saving it
                chart = getattr(self, f"{base_name}_chart", None)
                if chart:
                    img_buffer = BytesIO()
                    chart.figure.savefig(img_buffer, format='png', dpi=300)
                    img_buffer.seek(0)
                    
                    # Ensure enough space before adding an image
                    if y_position < 250:
                        c.showPage()
                        y_position = height - 60

                    # Maintain original size of the chart but scale it down
                    img_width, img_height = chart.figure.get_size_inches() * chart.figure.dpi
                    scale_factor = 0.35  # Scale down to 35% of the original size
                    scaled_width = img_width * scale_factor
                    scaled_height = img_height * scale_factor
                    c.drawImage(ImageReader(img_buffer), 15, y_position - scaled_height, width=scaled_width, height=scaled_height)
                    y_position -= scaled_height + 20  #Increased spacing below the image

                y_position -= 15  # Extra space between sections

                # Start new page if space is running out
                if y_position < 100:
                    c.showPage()
                    y_position = height - 100

            # Save the PDF
            c.save()
        else:
            QMessageBox.critical(self, "Results Yet to be Generated", "Please generate the results by pressing the Generate Results button")
            return False

    def update_chart(self, road_name, index):
        base_name = road_name.lower().replace(' ', '_')
        if getattr(self, f"{base_name}_chart", None):
            getattr(self, f"{base_name}_chart").deleteLater()

        # Configurations: Main, Alt, Alt1, Alt2, and Alt3
        configurations = ["Junction 1", "Junction 2", "Junction 3", "Junction 4", "Junction 5"]
        num_configs = len(configurations)

        # Categories to display
        categories = ['Avg Wait', 'Max Wait', 'Max Queue']
        x = np.arange(len(categories))  # Base positions for the three categories
        width = 0.8 / self.number  # Bar width adjusted for the number of configurations

        fig, ax = plt.subplots(figsize=(4, 6))
        configurations = configurations[:self.number]
        bars = []  # Store the BarContainer objects for later use

        for i, config in enumerate(configurations):
            # Retrieve values for the given road (using index)
            if config == "Junction 1":
                avg_wait_val = self.average_wait[index]
                max_wait_val = self.max_wait_time[index]
                max_queue_val = self.max_queue_length[index]
            elif config == "Junction 2":
                avg_wait_val = self.alt_avg_wait[index]
                max_wait_val = self.alt_max_wait_time[index]
                max_queue_val = self.alt_max_queue_length[index]
            elif config == "Junction 3":
                avg_wait_val = self.alt1_avg_wait[index]
                max_wait_val = self.alt1_max_wait_time[index]
                max_queue_val = self.alt1_max_queue_length[index]
            elif config == "Junction 4":
                avg_wait_val = self.alt2_avg_wait[index]
                max_wait_val = self.alt2_max_wait_time[index]
                max_queue_val = self.alt2_max_queue_length[index]
            elif config == "Junction 5":
                avg_wait_val = self.alt3_avg_wait[index]
                max_wait_val = self.alt3_max_wait_time[index]
                max_queue_val = self.alt3_max_queue_length[index]

            values = [avg_wait_val, max_wait_val, max_queue_val]
            offset = -0.4 + width / 2 + i * width
            bar_container = ax.bar(x + offset, values, width=width, label=config)
            bars.append(bar_container)

        cursor = mplcursors.cursor(bars, hover=True)

        @cursor.connect("add")
        def on_hover(sel):
            sel.annotation.set_text(f'{sel.artist.get_label()}\n{sel.target[1]:.2f}')
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.7)

        ax.set_ylabel('Values')
        ax.set_title(f'{road_name.replace("_", " ").title()} Comparison')
        ax.legend()

        # Compute group centers from the drawn bars so that category labels sit in the middle of the group
        group_centers = []
        for j in range(len(categories)):
            x_positions = []
            for bar_container in bars:
                # Each container holds a Rectangle for the j-th category
                bar = bar_container[j]
                x_positions.append(bar.get_x() + bar.get_width() / 2)
            group_center = np.mean(x_positions)
            group_centers.append(group_center)
        ax.set_xticks(group_centers)
        ax.set_xticklabels(categories)

        canvas_obj = FigureCanvas(fig)
        setattr(self, f"{base_name}_chart", canvas_obj)
        getattr(self, f"{base_name}_form_layout").addRow(canvas_obj)

