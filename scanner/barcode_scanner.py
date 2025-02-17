import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

API_URL = "http://127.0.0.1:5000/scan"  # Flask backend URL

class BarcodeScanner(QWidget):
    def __init__(self):
        super().__init__()

        # Setup UI
        self.setWindowTitle("Barcode Scanner - Time In/Out")
        self.showFullScreen()  # Make the window fullscreen

        # Display Scan Status
        self.label = QLabel("Scan a barcode...", self)
        self.label.setFont(QFont("Arial", 24))
        self.label.setAlignment(Qt.AlignCenter)

        # Manual input field
        self.input_barcode = QLineEdit(self)
        self.input_barcode.setFont(QFont("Arial", 18))
        self.input_barcode.setPlaceholderText("Enter barcode manually...")
        self.input_barcode.setAlignment(Qt.AlignCenter)
        self.input_barcode.returnPressed.connect(self.manual_submit)  # Submit on Enter

        # Submit button for manual input
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setFont(QFont("Arial", 18))
        self.submit_button.clicked.connect(self.manual_submit)

        # Info Panel (Name, Department, Time)
        self.info_label = QLabel("", self)
        self.info_label.setFont(QFont("Arial", 20))
        self.info_label.setAlignment(Qt.AlignCenter)

        # Add ESC instruction label
        self.esc_label = QLabel("Press ESC to exit", self)
        self.esc_label.setFont(QFont("Arial", 12))
        self.esc_label.setAlignment(Qt.AlignCenter)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_barcode)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.info_label)
        layout.addWidget(self.esc_label)  # Add ESC instruction to layout
        self.setLayout(layout)

    def keyPressEvent(self, event):
        """Capture barcode input from scanner and handle ESC key"""
        # Check for ESC key
        if event.key() == Qt.Key_Escape:
            self.close()  # Close the application
            return

        # Original barcode scanning logic
        barcode = event.text().strip()
        if barcode:
            self.send_barcode(barcode)

    def manual_submit(self):
        """Send manually entered barcode"""
        barcode = self.input_barcode.text().strip()
        if barcode:
            self.send_barcode(barcode)
            self.input_barcode.clear()

    def send_barcode(self, barcode):
        """Send barcode to backend"""
        try:
            response = requests.post(API_URL, json={"barcode": barcode})
            data = response.json()

            if data["success"]:
                self.label.setText(f"✅ {data['message']}")
                self.info_label.setText(
                    f"👤 {data['name']} | 🏢 {data['department']}\n🕒 {data['status']} - {data['time']} | 📅 {data['date']}"
                )
            else:
                self.label.setText(f"❌ {data['message']}")
                self.info_label.setText("")

        except requests.exceptions.ConnectionError:
            self.label.setText("❌ Error: Cannot connect to server.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scanner = BarcodeScanner()
    scanner.show()
    sys.exit(app.exec_())