import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QEvent

# Update API_URL to your PythonAnywhere Flask app URL
API_URL = "https://http://127.0.0.1:5000/scan"  

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller runtime: files are in temp folder
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Normal Python runtime: use current directory
        return os.path.join(os.path.abspath("."), relative_path)

class BarcodeScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Initialize status message timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.clear_status)
        
        # Initialize scan cooldown timer (5 seconds)
        self.scan_cooldown_timer = QTimer()
        self.scan_cooldown_timer.timeout.connect(self.enable_scanning)
        
        # Initialize countdown timer (updates every second)
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        self.is_scanning_enabled = True  # Track if scanning is enabled
        self.cooldown_duration = 5000  # 5 seconds in milliseconds
        self.remaining_cooldown = 0  # Track remaining cooldown in milliseconds
        self.barcode_buffer = ""  # Buffer to collect barcode characters
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Creo.log Scanner")
        self.setWindowIcon(QIcon(resource_path("favicon.ico")))
        self.showFullScreen()
        
        # Set window background to white
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Reduced spacing for compactness
        layout.setContentsMargins(40, 20, 40, 20)  # Reduced margins for compactness
        
        # Header container (smaller size, white background to match logo)
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 10px;  /* Reduced padding */
            }
        """)
        header_layout = QVBoxLayout()
        
        # Logo image (replace "CREOTEC" text with logo)
        logo_label = QLabel()
        try:
            pixmap = QPixmap(resource_path("creo-logo.png"))
            if pixmap.isNull():
                raise ValueError("Image file is invalid or cannot be loaded")
            pixmap = pixmap.scaled(500, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Scale to fit, maintaining aspect ratio
            logo_label.setPixmap(pixmap)
        except Exception as e:
            # Fallback to text if image fails to load
            logo_label.setText("CREOTEC")
            logo_label.setStyleSheet("""
                QLabel {
                    color: #312e81;
                    font-size: 28px;
                    font-weight: bold;
                    letter-spacing: 2px;
                }
            """)
            logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Subtitle (commented out as per your document)
        # subtitle = QLabel("PHILIPPINES, INC.")
        # subtitle.setStyleSheet("""
        #     QLabel {
        #         color: white;
        #         font-size: 12px;  /* Reduced font size */
        #         letter-spacing: 1px;
        #     }
        # """)
        # subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(logo_label)
        # header_layout.addWidget(subtitle)
        header_container.setLayout(header_layout)
        
        # Status container
        self.status_container = QFrame()
        self.status_container.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border-radius: 8px;
                padding: 20px;
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
        
        # Info label (set to rich text for HTML formatting)
        self.info_label = QLabel("")
        self.info_label.setTextFormat(Qt.RichText)  # Enable rich text for HTML formatting
        self.info_label.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 18px;
                margin-top: 10px;
            }
            QLabel > b {
                color: #312e81;  /* Blue for bold Time In/Time Out */
                font-weight: bold;
            }
        """)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)  # Enable word wrap for better formatting
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.info_label)
        self.status_container.setLayout(status_layout)
        
        # Manual input container (borderless, compact, and centered)
        self.input_container = QFrame()
        self.input_container.setStyleSheet("""
            QFrame {
                background-color: white;
                padding: 15px;  /* Reduced padding */
            }
        """)
        input_layout = QVBoxLayout()
        
        # Manual input label
        manual_label = QLabel("Manual Entry")
        manual_label.setStyleSheet("""
            QLabel {
                color: #312e81;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        manual_label.setAlignment(Qt.AlignCenter)
        
        # Input field and submit button in a horizontal layout for better alignment
        input_hbox = QHBoxLayout()
        input_hbox.setSpacing(10)
        
        # Input field
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Enter barcode manually... (12 digits)")
        self.input_barcode.setStyleSheet("""
            QLineEdit {
                padding: 10px;  /* Reduced padding */
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                font-size: 16px;
                min-width: 300px;  /* Ensure minimum width */
            }
            QLineEdit:focus {
                border: 2px solid #312e81;  /* Blue border on focus */
            }
        """)
        self.input_barcode.returnPressed.connect(self.manual_submit)
        
        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #312e81;
                color: white;
                padding: 10px 15px;  /* Reduced padding */
                border-radius: 4px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;  /* Ensure button has a minimum width */
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        self.submit_button.clicked.connect(self.manual_submit)
        
        input_hbox.addWidget(self.input_barcode)
        input_hbox.addWidget(self.submit_button)
        
        input_layout.addWidget(manual_label)
        input_layout.addLayout(input_hbox)
        
        # Exit instruction
        exit_label = QLabel("Press ESC to exit")
        exit_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        exit_label.setAlignment(Qt.AlignCenter)
        
        input_layout.addWidget(exit_label)
        self.input_container.setLayout(input_layout)
        
        # Add all components to main layout
        layout.addWidget(header_container)
        layout.addWidget(self.status_container)
        layout.addWidget(self.input_container)
        
        self.setLayout(layout)
        
    def focusInEvent(self, event):
        """Handle window regaining focus"""
        if self.remaining_cooldown <= 0 and not self.is_scanning_enabled:
            self.enable_scanning()  # Force re-enable scanning if cooldown is over and scanning is disabled
        self.input_barcode.setFocus()  # Set focus to input field when regaining focus
        super().focusInEvent(event)
        
    def event(self, event):
        """Override event to filter out key press events during cooldown"""
        if event.type() == QEvent.KeyPress and not self.is_scanning_enabled:
            # Ignore key press events during cooldown and show countdown
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #dc2626;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            seconds_remaining = self.remaining_cooldown // 1000 if self.remaining_cooldown > 0 else 5
            self.status_label.setText(f"Please wait {seconds_remaining} seconds before next scan")
            return True  # Event handled, prevent further processing
        return super().event(event)
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == Qt.Key_Escape:
            self.close()
            return
            
        if self.is_scanning_enabled:  # Only process scans if enabled
            char = event.text().strip()
            if char:  # Collect characters into a barcode buffer
                self.barcode_buffer += char
                
                # Check if the buffer forms a complete 12-digit barcode
                if len(self.barcode_buffer) == 12 and self.barcode_buffer.isdigit():
                    barcode = self.barcode_buffer
                    self.send_barcode(barcode)
                    self.barcode_buffer = ""  # Reset buffer after sending
                elif not self.barcode_buffer.isdigit() or len(self.barcode_buffer) > 12:
                    self.barcode_buffer = ""  # Reset buffer if non-digit or too long
    
    def manual_submit(self):
        """Handle manual barcode submission"""
        if self.is_scanning_enabled:  # Only process manual submits if enabled
            barcode = self.input_barcode.text().strip()
            if barcode and len(barcode) == 12 and barcode.isdigit():
                self.send_barcode(barcode)
                self.input_barcode.clear()
            else:
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #dc2626;
                        font-size: 24px;
                        font-weight: bold;
                    }
                """)
                self.status_label.setText("❌ Invalid barcode: Must be 12 digits")
                self.status_timer.start(5000)  # Show error for 5 seconds
        
    def send_barcode(self, barcode):
        """Process barcode and update UI"""
        if not self.is_scanning_enabled:
            return  # Prevent sending barcodes during cooldown
            
        try:
            response = requests.post(API_URL, json={"barcode": barcode}, timeout=10)  # Added timeout for better error handling
            data = response.json()
            
            self.is_scanning_enabled = False  # Disable scanning immediately after a scan
            self.input_barcode.setEnabled(False)  # Disable manual input
            self.submit_button.setEnabled(False)  # Disable submit button
            self.remaining_cooldown = self.cooldown_duration  # Set initial cooldown duration
            
            # Apply unique styles based on status
            if data["success"]:
                # Time In or Time Out (successful scans)
                if data["status"] == "Time In":
                    self.status_container.setStyleSheet("""
                        QFrame {
                            background-color: #aed4ae;  /* Light green */
                            border: 2px solid #06c206;  /* Dark green border */
                            border-radius: 8px;
                            padding: 20px;
                        }
                    """)
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #0f5132;
                            font-size: 24px;
                            font-weight: bold;
                        }
                    """)
                    self.status_label.setText(f"✅ {data['message']}")
                elif data["status"] == "Time Out":
                    self.status_container.setStyleSheet("""
                        QFrame {
                            background-color: #cce5ff;  /* Light blue */
                            border: 2px solid #084298;  /* Dark blue border */
                            border-radius: 8px;
                            padding: 20px;
                        }
                    """)
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #084298;
                            font-size: 24px;
                            font-weight: bold;
                        }
                    """)
                    self.status_label.setText(f"✅ {data['message']}")
                
                # Format info text for successful scans, highlighting Time In and Time Out with rich text
                info_text = (
                    f"Name: {data['name']}<br>"
                    f"Department: {data['department']}<br>"
                    f"<b>Status:</b> {data['status']}<br>"
                    f"<b>Time In:</b> {data.get('time_in', 'N/A')}<br>"
                    f"<b>Time Out:</b> {data.get('time_out', 'N/A')}<br>"
                    f"Date: {data['date']}"
                )
                self.info_label.setText(info_text)
                self.status_timer.start(10000)  # Extend status reset to 10 seconds for visibility
            else:
                # Handle "Already Timed Out" or other failures
                if data.get("message") == "Already Timed Out for Today":
                    self.status_container.setStyleSheet("""
                        QFrame {
                            background-color: #fff3cd;  /* Light yellow */
                            border: 2px solid #856404;  /* Dark yellow border */
                            border-radius: 8px;
                            padding: 20px;
                        }
                    """)
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #856404;
                            font-size: 24px;
                            font-weight: bold;
                        }
                    """)
                    self.status_label.setText(f"❌ {data['message']}")
                    
                    # Display attendance details even for "Already Timed Out"
                    info_text = (
                        f"Name: {data['name']}<br>"
                        f"Department: {data['department']}<br>"
                        f"<b>Status:</b> {data['status']}<br>"
                        f"<b>Time In:</b> {data.get('time_in', 'N/A')}<br>"
                        f"<b>Time Out:</b> {data.get('time_out', 'N/A')}<br>"
                        f"Date: {data['date']}"
                    )
                    self.info_label.setText(info_text)
                    self.status_timer.start(10000)  # Extend status reset to 10 seconds
                else:
                    self.status_container.setStyleSheet("""
                        QFrame {
                            background-color: #f8d7da;  /* Light red */
                            border: 2px solid #721c24;  /* Dark red border */
                            border-radius: 8px;
                            padding: 20px;
                        }
                    """)
                    self.status_label.setStyleSheet("""
                        QLabel {
                            color: #721c24;
                            font-size: 24px;
                            font-weight: bold;
                        }
                    """)
                    self.status_label.setText(f"❌ {data['message']}")
                    self.info_label.clear()
                    self.status_timer.start(5000)  # Show error for 5 seconds
            # Start countdown timer (updates every 1000 ms = 1 second)
            self.countdown_timer.start(1000)
            # Start 5-second cooldown timer
            self.scan_cooldown_timer.start(self.cooldown_duration)  # 5000 ms = 5 seconds
            
        except requests.exceptions.ConnectionError:
            self.status_container.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;  /* Light red */
                    border: 2px solid #721c24;  /* Dark red border */
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #721c24;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            self.status_label.setText("❌ Error: Cannot connect to server")
            self.info_label.clear()
            self.remaining_cooldown = self.cooldown_duration  # Set initial cooldown duration
            self.countdown_timer.start(1000)  # Start countdown on connection error
            self.scan_cooldown_timer.start(self.cooldown_duration)  # Start cooldown on connection error too
        except requests.exceptions.Timeout:
            self.status_container.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;  /* Light red */
                    border: 2px solid #721c24;  /* Dark red border */
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #721c24;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            self.status_label.setText("❌ Request timed out. Please try again.")
            self.info_label.clear()
            self.remaining_cooldown = self.cooldown_duration  # Set initial cooldown duration
            self.countdown_timer.start(1000)  # Start countdown on timeout error
            self.scan_cooldown_timer.start(self.cooldown_duration)  # Start cooldown on timeout error too
        except requests.exceptions.RequestException as e:
            self.status_container.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;  /* Light red */
                    border: 2px solid #721c24;  /* Dark red border */
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #721c24;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            self.status_label.setText(f"❌ Network error: {str(e)}")
            self.info_label.clear()
            self.remaining_cooldown = self.cooldown_duration  # Set initial cooldown duration
            self.countdown_timer.start(1000)  # Start countdown on general request error
            self.scan_cooldown_timer.start(self.cooldown_duration)  # Start cooldown on general request error too
            
    def update_countdown(self):
        """Update the countdown display every second"""
        if self.remaining_cooldown > 0:
            self.remaining_cooldown -= 1000  # Decrease by 1 second (1000 ms)
            seconds_remaining = self.remaining_cooldown // 1000 if self.remaining_cooldown > 0 else 0
            self.status_container.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;  /* Light red */
                    border: 2px solid #721c24;  /* Dark red border */
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #721c24;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            self.status_label.setText(f"Please wait {seconds_remaining} seconds before next scan")
        else:
            self.countdown_timer.stop()  # Stop countdown when it reaches 0
            
    def enable_scanning(self):
        """Re-enable scanning after 5-second cooldown"""
        self.scan_cooldown_timer.stop()
        self.countdown_timer.stop()
        self.is_scanning_enabled = True
        self.input_barcode.setEnabled(True)  # Re-enable manual input
        self.submit_button.setEnabled(True)  # Re-enable submit button
        self.status_container.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.status_label.setText("Ready to Scan")  # Reset status to indicate readiness
        self.remaining_cooldown = 0  # Reset remaining cooldown
        self.barcode_buffer = ""  # Reset barcode buffer
        self.info_label.setText("")  # Clear info label on reset
        self.info_label.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 18px;
                margin-top: 10px;
            }
            QLabel > b {
                color: #312e81;  /* Blue for bold Time In/Time Out */
                font-weight: bold;
            }
        """)
        
    def clear_status(self):
        """Reset status display"""
        if not self.status_timer.isActive():
            self.status_timer.stop()
        self.status_container.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.status_label.setText("Ready to Scan")
        # Do not clear info_label here to keep scan results visible longer
        # self.info_label.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scanner = BarcodeScanner()
    scanner.show()
    sys.exit(app.exec_())