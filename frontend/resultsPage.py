import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, 
                             QHBoxLayout, QGridLayout, QSizePolicy, QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
import sqlite3


# Sample results
overall = 50
max_wait = 100
avg_wait = 75
max_length = 25

alt_overall = 75
alt_max_wait = 150
alt_avg_wait = 125
alt_max_length = 50

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

overallScore = 66
alt_overallScore = 80

class ResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load and apply the stylesheet
        self.apply_stylesheet()

        # Overall scores
        overall_scores_layout = QHBoxLayout()
        overall_label = QLabel(f"Main Configuration Overall Score: {overallScore}")
        overall_label.setObjectName("overallScoreLabel")
        overall_label.setAlignment(Qt.AlignCenter)
        overall_scores_layout.addWidget(overall_label)

        alt_overall_label = QLabel(f"Alternate Configuration Overall Score: {alt_overallScore}")
        alt_overall_label.setObjectName("overallScoreLabel")
        alt_overall_label.setAlignment(Qt.AlignCenter)
        overall_scores_layout.addWidget(alt_overall_label)

        # Use a grid layout for the road groups
        main_layout = QGridLayout()
        main_layout.setSpacing(5)  # Reduce spacing for a more compact layout

        # Create road result groups in a 2x2 grid
        self.create_road_group(main_layout, "South Traffic Flow", 0, 0)  # Top-left
        self.create_road_group(main_layout, "North Traffic Flow", 0, 1)  # Top-right
        self.create_road_group(main_layout, "West Traffic Flow", 1, 0)   # Bottom-left
        self.create_road_group(main_layout, "East Traffic Flow", 1, 1)   # Bottom-right

        # Button to generate results
        self.generate_results_button = QPushButton("Generate Results")
        self.generate_results_button.clicked.connect(self.get_results)
        main_layout.addWidget(self.generate_results_button, 2, 0)  # Bottom-left

        # Button to get report
        self.generate_report_button = QPushButton("Download Report as PDF") 
        self.generate_report_button.clicked.connect(self.get_report)
        main_layout.addWidget(self.generate_report_button, 2, 1)  # Bottom-right

        # Button to save results to database
        self.save_to_db_button = QPushButton("Save Results to Database")
        self.save_to_db_button.clicked.connect(self.save_results_to_db)
        main_layout.addWidget(self.save_to_db_button, 3, 0)  # Bottom-right

        # Add the button to view the database
        self.view_db_button = QPushButton("View Database")
        self.view_db_button.clicked.connect(self.view_database)
        main_layout.addWidget(self.view_db_button, 3, 1)  # Bottom-right

        self.go_inputs_button = QPushButton("Run Simulation Again")
        main_layout.addWidget(self.go_inputs_button, 4, 0, 1, 2)  # Bottom

        self.exit_button = QPushButton("Exit")
        self.exit_button.setObjectName("exitButton")
        main_layout.addWidget(self.exit_button, 5, 0, 1, 2)  # Bottom


        # Set the layout of the main widget
        layout = QVBoxLayout()
        layout.addLayout(overall_scores_layout)
        layout.addLayout(main_layout)
        self.setLayout(layout)

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

        alt_avg_wait_label = QLabel("Alternate Average Wait Time: -")
        alt_max_wait_label = QLabel("Alternate Max Wait Time: -")
        alt_max_queue_label = QLabel("AlternateMax Queue Length: -")

        # Create a grid layout for the labels
        labels_layout = QGridLayout()

        # Add the labels to the grid layout
        labels_layout.addWidget(avg_wait_label, 0, 0)
        labels_layout.addWidget(max_wait_label, 1, 0)
        labels_layout.addWidget(max_queue_label, 2, 0)

        labels_layout.addWidget(alt_avg_wait_label, 0, 1)
        labels_layout.addWidget(alt_max_wait_label, 1, 1)
        labels_layout.addWidget(alt_max_queue_label, 2, 1)

        # Add the grid layout to the form layout
        form_layout.addRow(labels_layout)

        # Store reference for updating results later
        base_name = road_name.lower().replace(' ', '_')
        setattr(self, f"{base_name}_chart", None)
        setattr(self, f"{base_name}_avg_wait_label", avg_wait_label)
        setattr(self, f"{base_name}_max_wait_label", max_wait_label)
        setattr(self, f"{base_name}_max_queue_label", max_queue_label)
        setattr(self, f"{base_name}_form_layout", form_layout)

        setattr(self, f"{base_name}_alt_avg_wait_label", alt_avg_wait_label)
        setattr(self, f"{base_name}_alt_max_wait_label", alt_max_wait_label)
        setattr(self, f"{base_name}_alt_max_queue_label", alt_max_queue_label)
        setattr(self, f"{base_name}_form_layout", form_layout)

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

        self.alt_avg_wait = [30, 40, 35, 25]
        self.alt_max_wait_time = [60, 70, 55, 40]
        self.alt_max_queue_length = [20, 25, 22, 18]

        counter = 0
        for road_name in ["south_traffic_flow", "north_traffic_flow", 
                          "west_traffic_flow", "east_traffic_flow"]:

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

            self.update_chart(road_name, counter)
            counter += 1

        counter2 = 0
        for alt_road_name in ["south_traffic_flow", "north_traffic_flow", 
                              "west_traffic_flow", "east_traffic_flow"]:
            
            alt_road_results[alt_road_name] = {
                "average_wait": self.alt_avg_wait[counter2],
                "max_wait_times": self.alt_max_wait_time[counter2],
                "max_queue_length": self.alt_max_queue_length[counter2],
            }

            base_name = alt_road_name.lower().replace(' ', '_')
            getattr(self, f"{base_name}_alt_avg_wait_label").setText(f"Alternate Average Wait Time: {self.alt_avg_wait[counter2]} sec")
            getattr(self, f"{base_name}_alt_max_wait_label").setText(f"Alternate Max Wait Time: {self.alt_max_wait_time[counter2]} sec")
            getattr(self, f"{base_name}_alt_max_queue_label").setText(f"Alternate Max Queue Length: {self.alt_max_queue_length[counter2]} cars")
            
            self.update_chart(alt_road_name, counter2)
            counter2 += 1

    def get_report(self):
        """Generates a PDF report with the results and bar charts using ReportLab."""

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
        c.drawString(40, height - 80, "Below are the results of the simulation.")
        y_position = height - 120

        for road_name in ["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]:
        
            base_name = road_name.lower().replace('_', '_')
            section_title = road_name.replace('_', ' ').title() + " Results"

            # Section Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y_position, section_title)
            y_position -= 30  # Increased spacing

            # Main and Alternative Configuration in two columns
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y_position, "Main Configuration:")
            c.drawString(300, y_position, "Alternative Configuration:")
            y_position -= 20

            c.setFont("Helvetica", 11)
            c.drawString(60, y_position, f"- Average Wait Time: {road_results[road_name]['average_wait']} sec")
            c.drawString(320, y_position, f"- Average Wait Time: {alt_road_results[road_name]['average_wait']} sec")
            y_position -= 20

            c.drawString(60, y_position, f"- Max Wait Time: {road_results[road_name]['max_wait_times']} sec")
            c.drawString(320, y_position, f"- Max Wait Time: {alt_road_results[road_name]['max_wait_times']} sec")
            y_position -= 20

            c.drawString(60, y_position, f"- Max Queue Length: {road_results[road_name]['max_queue_length']} cars")
            c.drawString(320, y_position, f"- Max Queue Length: {alt_road_results[road_name]['max_queue_length']} cars")
            y_position -= 30  # Extra spacing before chart

            # Add the chart directly to the PDF without saving it
            chart = getattr(self, f"{base_name}_chart", None)
            if chart:
                img_buffer = BytesIO()
                chart.figure.savefig(img_buffer, format='png', dpi=300)
                img_buffer.seek(0)
                
                # Ensure enough space before adding an image
                if y_position < 250:
                    c.showPage()
                    y_position = height - 100

                # Maintain original size of the chart but scale it down
                img_width, img_height = chart.figure.get_size_inches() * chart.figure.dpi
                scale_factor = 0.35  # Scale down to 35% of the original size
                scaled_width = img_width * scale_factor
                scaled_height = img_height * scale_factor
                c.drawImage(ImageReader(img_buffer), 15, y_position - scaled_height, width=scaled_width, height=scaled_height)
                y_position -= scaled_height + 35  #Increased spacing below the image

            y_position -= 15  # Extra space between sections

            # Start new page if space is running out
            if y_position < 100:
                c.showPage()
                y_position = height - 100

        # Save the PDF
        c.save()

    def save_results_to_db(self):
        """Saves the results to a SQLite database."""
        # Connect to the database (or create it if it doesn't exist)
        conn = sqlite3.connect('simulation_results.db')
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                road_name TEXT,
                average_wait INTEGER,
                max_wait_times INTEGER,
                max_queue_length INTEGER,
                alt_average_wait INTEGER,
                alt_max_wait_times INTEGER,
                alt_max_queue_length INTEGER
            )
        ''')

        # Insert results into the database
        for road_name in ["south_traffic_flow", "north_traffic_flow", "west_traffic_flow", "east_traffic_flow"]:
            cursor.execute('''
                INSERT INTO results (road_name, average_wait, max_wait_times, max_queue_length, alt_average_wait, alt_max_wait_times, alt_max_queue_length)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                road_name,
                road_results[road_name]['average_wait'],
                road_results[road_name]['max_wait_times'],
                road_results[road_name]['max_queue_length'],
                alt_road_results[road_name]['average_wait'],
                alt_road_results[road_name]['max_wait_times'],
                alt_road_results[road_name]['max_queue_length']
            ))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        print("Results saved to database successfully.")
       
    def update_chart(self, road_name, index):
        base_name = road_name.lower().replace(' ', '_')
        if getattr(self, f"{base_name}_chart"):
            getattr(self, f"{base_name}_chart").deleteLater()

        categories = ['Average Wait Time', 'Max Wait Time', 'Max Queue Length']
        input_values = [self.average_wait[index], self.max_wait_time[index], self.max_queue_length[index]]
        alt_values = [self.alt_avg_wait[index], self.alt_max_wait_time[index], self.alt_max_queue_length[index]]

        x = range(len(categories))
        x2 = [val + 0.4 for val in x]

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(x, input_values, width=0.4, label='Main Configuration')
        ax.bar(x2, alt_values, width=0.4, label='Alternative Configuration')

        ax.set_ylabel('Values')
        ax.set_title(f'{road_name.replace("_", " ").title()} Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()

        canvas = FigureCanvas(fig)
        setattr(self, f"{base_name}_chart", canvas)
        getattr(self, f"{base_name}_form_layout").addRow(canvas)

    def view_database(self):
        """Displays the contents of the database in a new window."""
        conn = sqlite3.connect('simulation_results.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM results')
        results = cursor.fetchall()

        conn.close()

        # Create a new window to display the results
        db_window = QWidget()
        db_window.setWindowTitle("Database Results")
        layout = QVBoxLayout()

        # Create a scroll area to handle large number of results
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for row in results:
            row_label = QLabel(str(row))
            scroll_layout.addWidget(row_label)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)
        db_window.setLayout(layout)
        db_window.resize(600, 400)
        db_window.show()

        self.db_window = db_window  # Keep a reference to prevent garbage collection

    