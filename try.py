from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class CoordinateLabel(QLabel):
    def __init__(self, parent=None):
        super(CoordinateLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Move the cursor over this label")
        self.setMouseTracking(True)  # Enable mouse tracking for the widget

    def mouseMoveEvent(self, event):
        cursor_pos = event.pos()
        self.setText(f"Cursor Position: ({cursor_pos.x()}, {cursor_pos.y()})")

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        coordinateLabel = CoordinateLabel(self)
        layout.addWidget(coordinateLabel)

        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Cursor Coordinates Example')
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    mainWindow = MainWindow()
    app.exec()
