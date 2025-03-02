import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout, QPushButton, QDialog
from inputAndParameterPage import InputAndParameterWidget
from resultsPage import ResultsWidget
from visualisation import ImageViewer
import os

class HomeWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Home")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()
        self.label = QLabel("Welcome to the Traffic Junction Simulator App!\n"
                    "\n"
                    "University of Warwick\n"
                    "\n"
                    "Department of Computer Science 2025\n"
                    "\n"
                    "Authors: Ani Bitri, Krister Hughes, Thomas Phuong, Eshan Sharif, Josh Turner, Antoni Zyla\n"
                    "\n"
                    "Click the button below to go to the Input Parameters page.")
        self.button = QPushButton("Go to Input Parameters")
        self.button.clicked.connect(self.go_to_main_app)

        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def go_to_main_app(self):
        self.accept()

    def closeEvent(self, event):
        print("Home window closed.")
        event.accept()
        sys.exit()

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulation Application")
        self.setGeometry(100, 100, 1400, 850)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.add_tabs()

    def add_tabs(self):
        # Tab 1: Input and Parameters
        self.input_tab = InputAndParameterWidget()
        self.tab_widget.addTab(self.input_tab, "Input Parameters")

        # Tab 2: Simulation 
        self.simulation_tab = ImageViewer()  
        self.tab_widget.addTab(self.simulation_tab, "Simulation")

        # Tab 3: Simulation Results
        self.results_tab = ResultsWidget()  # or ResultsPage, depending on your class
        self.tab_widget.addTab(self.results_tab, "Simulation Results")

        # Connect the "Start Simulation" button to the method to switch to the Simulation tab
        self.input_tab.submit_button.clicked.connect(self.go_to_simulation_tab)

    def go_to_simulation_tab(self):
        self.tab_widget.setCurrentWidget(self.simulation_tab)

    def closeEvent(self, event):
        print("Application closed.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    home_window = HomeWindow()
    if home_window.exec_() == QDialog.Accepted:
        main_app = MainApplication()
        main_app.show()

    sys.exit(app.exec_())
