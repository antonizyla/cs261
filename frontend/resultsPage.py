import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, 
                             QSpinBox, QCheckBox, QGroupBox, QFormLayout, QToolButton, QHBoxLayout)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

# Sample results
overall = 50
max_wait = 100
avg_wait = 75
max_length = 25

alt_overall = 75
alt_max_wait = 150
alt_avg_wait = 125
alt_max_length = 50

class ResultsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simulation Results')
        
        layout = QVBoxLayout()


        # Table with matplotlib
        fig, ax = plt.subplots()

        ax.xaxis.set_visible(False) 
        ax.yaxis.set_visible(False)
        ax.set_frame_on(False)

        # Table data
        data = [
            ["Metric", "Input Simulation", "Alternative Simulation"],
            ["Overall", str(overall), str(alt_overall)],
            ["Max Wait Time", str(max_wait), str(alt_max_wait)],
            ["Average Wait Time", str(avg_wait), str(alt_avg_wait)],
            ["Max Length", str(max_length), str(alt_max_length)]
        ]

        table = ax.table(cellText=data, cellLoc='center', loc='center')
       
        table.scale(1, 1.5)
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        self.create_bar_chart(layout)
    
        # Add a button to close the results page
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        
    # Bar Chart for results
    def create_bar_chart(self, layout):
        categories = ['Overall', 'Max Wait Time', 'Average Wait Time', 'Max Length']
        input_simulation = [overall, max_wait, avg_wait, max_length]
        alt_simulation = [alt_overall, alt_max_wait, alt_avg_wait, alt_max_length]
    
        x = range(len(categories))
        x2 = [x + 0.4 for x in x]
    
        fig, ax = plt.subplots()
        ax.bar(x, input_simulation, width=0.4, label='Input Simulation')
        ax.bar(x2, alt_simulation, width=0.4, label='Alternative Simulation')
    
        ax.set_xlabel('Categories')
        ax.set_ylabel('Values')
        ax.set_title('Simulation Results Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
    
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
