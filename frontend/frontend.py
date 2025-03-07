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
                    "Authors: Ani Bitri, Krister Hughes, Thomas Phuong, Josh Turner, Antoni Zyla\n"
                    "\n"
                    "Click the button below to go to the Input Parameters page.")
        
        self.button = QPushButton("Go to Input Parameters")
        self.button.setObjectName("go_to_input_button")
        self.button.clicked.connect(self.go_to_main_app)

        self.exit_button = QPushButton("Exit Application")
        self.exit_button.setStyleSheet("background-color: #FF3B30; color: white; border: none; border-radius: 6px; font-family: Helvetica Neue, sans-serif; padding: 2px;")
        self.exit_button.clicked.connect(self.close)

        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.exit_button)
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
        #self.setGeometry(100, 100, 1400, 850)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.add_tabs()

        self.showMaximized()

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
        self.simulation_tab.go_results_button.clicked.connect(self.go_to_results_tab)
        self.results_tab.go_inputs_button.clicked.connect(self.go_to_input_tab)
        self.results_tab.exit_button.clicked.connect(self.exit_app)

    def go_to_simulation_tab(self):
        self.tab_widget.setCurrentWidget(self.simulation_tab)

    def go_to_results_tab(self):
        self.tab_widget.setCurrentWidget(self.results_tab)

    def go_to_input_tab(self):
        self.tab_widget.setCurrentWidget(self.input_tab)

    def exit_app(self):
        sys.exit()

    def closeEvent(self, event):
        print("Application closed.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    def apply_stylesheet(self):
        """Loads and applies the stylesheet."""
        try:
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'inputAndParameterPageStyleSheet.qss')
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print("Stylesheet file not found. Using default styles.")
    
    home_window = HomeWindow()
    if home_window.exec_() == QDialog.Accepted:
        main_app = MainApplication()
        main_app.show()
        main_app.showMaximized()

    sys.exit(app.exec_())
