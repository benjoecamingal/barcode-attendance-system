import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer

API_URL = "http://127.0.0.1:5000/scan"

class BarcodeScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Initialize status message timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.clear_status)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Creo.log Scanner")
        self.setWindowIcon(QIcon("static/favicon.ico"))
        self.showFullScreen()
        
        # Set window background to white
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header container
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: #312e81;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout()
        
        # Company name
        company_name = QLabel("CREOTEC")
        company_name.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        company_name.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("PHILIPPINES, INC.")
        subtitle.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(company_name)
        header_layout.addWidget(subtitle)
        header_container.setLayout(header_layout)
        
        # Status container
        status_container = QFrame()
        status_container.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border-radius: 8px;
                padding: 30px;
            }
        """)
        status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready to Scan")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 18px;
                margin-top: 10px;
            }
        """)
        self.info_label.setAlignment(Qt.AlignCenter)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.info_label)
        status_container.setLayout(status_layout)
        
        # Manual input container
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        input_layout = QVBoxLayout()
        
        # Manual input label
        manual_label = QLabel("Manual Entry")
        manual_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        manual_label.setAlignment(Qt.AlignCenter)
        
        # Input field
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Enter barcode manually...")
        self.input_barcode.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #4f46e5;
            }
        """)
        self.input_barcode.returnPressed.connect(self.manual_submit)
        
        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #312e81;
                color: white;
                padding: 12px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        self.submit_button.clicked.connect(self.manual_submit)
        
        input_layout.addWidget(manual_label)
        input_layout.addWidget(self.input_barcode)
        input_layout.addWidget(self.submit_button)
        input_container.setLayout(input_layout)
        
        # Exit instruction
        exit_label = QLabel("Press ESC to exit")
        exit_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
            }
        """)
        exit_label.setAlignment(Qt.AlignCenter)
        
        # Add all components to main layout
        layout.addWidget(header_container)
        layout.addWidget(status_container)
        layout.addWidget(input_container)
        layout.addStretch()
        layout.addWidget(exit_label)
        
        self.setLayout(layout)
        
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == Qt.Key_Escape:
            self.close()
            return
            
        barcode = event.text().strip()
        if barcode:
            self.send_barcode(barcode)
            
    def manual_submit(self):
        """Handle manual barcode submission"""
        barcode = self.input_barcode.text().strip()
        if barcode:
            self.send_barcode(barcode)
            self.input_barcode.clear()
            
    def send_barcode(self, barcode):
        """Process barcode and update UI"""
        try:
            response = requests.post(API_URL, json={"barcode": barcode})
            data = response.json()
            
            if data["success"]:
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #059669;
                        font-size: 24px;
                        font-weight: bold;
                    }
                """)
                self.status_label.setText(f"✅ {data['message']}")
                
                # Format info text
                info_text = (
                    f"Name: {data['name']}\n"
                    f"Department: {data['department']}\n"
                    f"{data['status']} at {data['time']} on {data['date']}"
                )
                self.info_label.setText(info_text)
            else:
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #dc2626;
                        font-size: 24px;
                        font-weight: bold;
                    }
                """)
                self.status_label.setText(f"❌ {data['message']}")
                self.info_label.clear()
                
            # Reset status after 5 seconds
            self.status_timer.start(5000)
            
        except requests.exceptions.ConnectionError:
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            self.status_label.setText("❌ Error: Cannot connect to server")
            self.info_label.clear()
            self.status_timer.start(5000)
            
    def clear_status(self):
        """Reset status display"""
        self.status_timer.stop()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.status_label.setText("Ready to Scan")
        self.info_label.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scanner = BarcodeScanner()
    scanner.show()
    sys.exit(app.exec_())