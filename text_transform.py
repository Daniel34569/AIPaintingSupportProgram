import argparse
import re

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTextEdit

version = 1.00

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(f"Text Transformer Ver:{version}")

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a text input widget
        self.text_input = QTextEdit()
        self.text_input.setAcceptRichText(False)  # Accept plain text only
        layout.addWidget(self.text_input)

        # Create a horizontal layout for the combo box and button
        hbox = QHBoxLayout()

        # Create a combo box for transformation selection
        self.combo = QComboBox()
        self.combo.addItems(['Transform CivitAI', 'Remove Strength', 'NAI to WebUI', 'Booru to WebUI'])
        hbox.addWidget(self.combo)

        # Create a button that will trigger the transformation
        self.transform_button = QPushButton("Transform Input")
        self.transform_button.clicked.connect(self.transform_input)
        hbox.addWidget(self.transform_button)

        # Add the horizontal layout to the vertical layout
        layout.addLayout(hbox)

        # Create a text output widget
        self.text_output = QTextEdit()
        layout.addWidget(self.text_output)

        # Set the layout on the window
        self.setLayout(layout)

        # Resize the window
        self.resize(500, 400)

    def transform_input(self):
        # Get the transformation type from the combo box
        transformation_type = self.combo.currentText()

        # Get the input text
        input_text = self.text_input.toPlainText()

        # Apply the selected transformation
        if transformation_type == 'Transform CivitAI':
            self.transform_civitAI(input_text)
        elif transformation_type == 'Remove Strength':
            self.transform_NoMoreStrength(input_text)
        elif transformation_type == 'NAI to WebUI':
            self.transform_NAI(input_text)
        elif transformation_type == 'Booru to WebUI':
            self.transform_Booru(input_text)
            
            
    def transform_civitAI(self, input_text):
        # Get the input text, convert to lowercase and replace newline characters
        transformed = input_text.lower().replace('\n', ', ')
        
        # Display the result in the output Text widget
        self.text_output.setPlainText(transformed)

    def transform_NoMoreStrength(self, input_text):

        # Remove weights (e.g., :1.2) inside parentheses
        cleaned_text = re.sub(r'\:\d+(\.\d+)?\)', ')', input_text)

        # Remove opening parentheses not preceded by a backslash
        cleaned_text = re.sub(r'(?<!\\)\(', '', cleaned_text)

        # Remove closing parentheses not preceded by a backslash
        cleaned_text = re.sub(r'(?<!\\)\)', '', cleaned_text)

        # Remove curly braces
        cleaned_text = re.sub(r'\{\{+\s*|\}\}+\s*', '', cleaned_text)

        # Replace multiple spaces with a single space
        cleaned_text = re.sub(' +', ' ', cleaned_text)

        # Display the result in the output Text widget
        self.text_output.setPlainText(cleaned_text)

    def transform_NAI(self, input_text):
        # Find all instances of each type of bracket
        curly_brackets = re.findall(r'\{+[\w\s-]+\}+', input_text)
        square_brackets = re.findall(r'\[+[\w\s-]+\]+', input_text)

        # For each match, calculate the strength and replace the original text
        for match in curly_brackets:
            strength = 1.05 ** (match.count('{'))
            word = re.search(r'[\w\s-]+', match).group()
            formatted_strength = f"{strength:.5f}".rstrip('0')
            input_text = input_text.replace(match, f'({word}:{formatted_strength})')

        for match in square_brackets:
            strength = 0.95 ** (match.count('['))
            word = re.search(r'[\w\s-]+', match).group()
            formatted_strength = f"{strength:.5f}".rstrip('0')
            input_text = input_text.replace(match, f'({word}:{formatted_strength})')

        # Display the result in the output Text widget
        self.text_output.setPlainText(input_text)
            
    def transform_Booru(self, input_text):
        # Get the input text, convert from booru format to webui format
        lines = input_text.strip().split('\n')
        transformed = []
        for line in lines:
            if line == '?':
                continue
            words = line.split(' ')
            word = ' '.join(words[:-1])
            print(word)
            transformed.append(word)
        transformed = ', '.join(transformed)
        
        # Display the result in the output Text widget
        self.text_output.setPlainText(transformed)

if __name__ == '__main__':
    # Create a Qt application
    app = QApplication([])

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Run the main loop
    app.exec_()