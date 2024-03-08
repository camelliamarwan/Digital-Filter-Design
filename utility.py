import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLabel
from PyQt5.QtCore import QObject, pyqtSignal



class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()

        self.layout = QVBoxLayout()
        self.checked_checkbox_names = []  # List to store names of checked checkboxes

        # Create a button to add checkbox with a button dynamically
        self.addButton = QPushButton('Add CheckBox with Button')
        self.addButton.clicked.connect(self.add_checkbox_with_button)

        # QLabel to display the checkbox name
        self.label = QLabel('Checkbox Name: ')

        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def add_checkbox_with_button(self):
        # Create a QWidget as a container
        container_widget = QWidget()

        # Create a QCheckBox
        checkbox = QCheckBox('NewCheckBox')

        # Connect checkbox clicked event to a custom action
        checkbox.clicked.connect(lambda: self.update_label_and_list(checkbox))

        # Create a QPushButton
        button = QPushButton('Action Button')

        # Connect button click event to a custom action (modify this as needed)
        button.clicked.connect(lambda: self.delete_checkbox_with_button(container_widget))

        # Arrange checkbox and button horizontally
        container_layout = QHBoxLayout()
        container_layout.addWidget(checkbox)
        container_layout.addWidget(button)
        container_widget.setLayout(container_layout)

        # Store a reference to the checkbox inside the container widget
        container_widget.checkbox = checkbox

        # Add the container to the main layout vertically
        self.layout.addWidget(container_widget)

    def update_label_and_list(self, checkbox):
        if checkbox.isChecked():
            self.checked_checkbox_names.append(checkbox.text())
        else:
            self.checked_checkbox_names.remove(checkbox.text())

        # Print the updated list (you can modify this part as needed)
        print("Checked Checkboxes:", self.checked_checkbox_names)

    def delete_checkbox_with_button(self, container_widget):
        # Remove the checkbox name from the list
        self.checked_checkbox_names.remove(container_widget.checkbox.text())

        # Create a signal to delete the container widget
        delete_signal = DeleteSignal()

        # Connect the signal to the slot to delete the container widget
        delete_signal.connect(container_widget.deleteLater)

        # Emit the signal to delete the container widget
        delete_signal.emit()


class DeleteSignal(QObject):
    # Signal to trigger the deletion of the container widget
    delete_signal = pyqtSignal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())
