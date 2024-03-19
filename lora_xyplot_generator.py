import argparse
import re
import os

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QLabel, QTextEdit, QFileDialog
from PyQt5.QtCore import Qt



class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()

        # Set up layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create a horizontal layout for the combo box and button
        hbox = QHBoxLayout()

        # Set up directory input
        self.dir_input = QLineEdit()
        #layout.addWidget(self.dir_input)
        hbox.addWidget(self.dir_input)

        # Set up button to select directory
        self.select_dir_btn = QPushButton('Select Directory')
        self.select_dir_btn.clicked.connect(self.select_directory)
        #layout.addWidget(self.select_dir_btn)
        hbox.addWidget(self.select_dir_btn)
        layout.addLayout(hbox)

        # Set up parameter input
        self.param_label = QLabel('Weight: ')
        self.param_input = QLineEdit('0.3,0.5,0.7,1.0')  # default value
        param_layout = QHBoxLayout()
        param_layout.addWidget(self.param_label)
        param_layout.addWidget(self.param_input)
        layout.addLayout(param_layout)
        
        # Set up parameter input
        self.param_label2 = QLabel('Dyn:')
        self.param_input2 = QLineEdit('')  # default value
        param_layout2 = QHBoxLayout()
        param_layout2.addWidget(self.param_label2)
        param_layout2.addWidget(self.param_input2)
        layout.addLayout(param_layout2)
        
        #Choose type
        self.combo = QComboBox()
        self.combo.addItems(['Lyco', 'Lora', 'DyLora'])
        layout.addWidget(self.combo)

        # Set up output QTextEdit
        self.output = QTextEdit()
        layout.addWidget(self.output)

        # Set up process button
        self.process_btn = QPushButton('Process')
        self.process_btn.clicked.connect(self.process)
        layout.addWidget(self.process_btn)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if dir_path:
            self.dir_input.setText(dir_path)

    def process(self):
        path = self.dir_input.text()
        weight = self.param_input.text()
        dyn = self.param_input.text()
        result = self.get_target_text(path, weight, dyn)
        self.output.setText(result)
        
    def get_target_text(self, path, interval, dyn):
        # Check if interval is empty
        if not interval:
            return 'No intervals provided.'

        # Split intervals into list of floats
        intervals = [float(i) for i in interval.split(',')]
        
        lora_type = self.combo.currentText()

        # List all files in directory
        files = [f.split('.')[0] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # Generate output string
        output = []
        for file in files:
            for i in intervals:
                if lora_type == 'Lora':
                    output.append(f'<lora:{file}:{i}>')
                elif lora_type == 'Lyco':
                    output.append(f'<lyco:{file}:{i}>')
                else:
                    print(f'Not Support Now!')
                    break

        return ', '.join(output)

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()