import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout
from inputAndParameterPage import InputAndParameterWidget
from resultsPage import ResultsWidget  # or ResultsPage, depending on which one you are using

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
        input_tab = InputAndParameterWidget()
        self.tab_widget.addTab(input_tab, "Input Parameters")

        # Tab 2: Simulation 
        simulation_tab = QWidget()
        simulation_layout = QVBoxLayout()
        simulation_label = QLabel("Simulation will be displayed here.")
        simulation_layout.addWidget(simulation_label)
        simulation_tab.setLayout(simulation_layout)
        self.tab_widget.addTab(simulation_tab, "Simulation")

        # Tab 3: Simulation Results
        results_tab = ResultsWidget()  # or ResultsPage, depending on your class
        self.tab_widget.addTab(results_tab, "Simulation Results")

    def closeEvent(self, event):
        print("Application closed.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec_())
