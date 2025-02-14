import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QStackedWidget,
    QDesktopWidget, QSizePolicy
)
import requests

API_LOGIN = "http://127.0.0.1:5000/login"
API_UPLOAD = "http://127.0.0.1:5000/upload"

session = requests.Session()

class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Barcode Attendance System")
        self.resize(750, 500)  # ✅ Step 2: Set larger size
        self.center_window()    # ✅ Step 1: Center the window


        # Create Stacked Layout (to switch between Login and Upload UI)
        self.stack = QStackedWidget(self)

        # Create Login and Upload Screens
        self.login_screen = self.create_login_screen()
        self.menu_screen = self.create_menu_screen() 
        self.upload_screen = self.create_upload_screen()

        # Add Screens to Stack
        self.stack.addWidget(self.login_screen)  # Index 0
        self.stack.addWidget(self.menu_screen)   # Index 1
        self.stack.addWidget(self.upload_screen) # Index 2

        # Set Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def center_window(self):
        """Centers the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())


    def create_login_screen(self):
        """Creates the Login UI"""
        login_widget = QWidget()
        layout = QVBoxLayout()

        self.label_login = QLabel("Enter your credentials:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")

        # ✅ Make widgets expand responsively
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(self.label_login)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.login_button.clicked.connect(self.handle_login)

        login_widget.setLayout(layout)
        return login_widget
    

    def create_menu_screen(self):
        """Creates the Main Menu UI after login"""
        menu_widget = QWidget()
        layout = QVBoxLayout()

        self.label_menu = QLabel("Welcome! Select an option:")
        self.attendance_button = QPushButton("Take Attendance")
        self.upload_button = QPushButton("Upload Excel File")
        self.logout_button = QPushButton("Logout")

        # Add to Layout
        layout.addWidget(self.label_menu)
        layout.addWidget(self.attendance_button)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.logout_button)

        # Set Button Actions
        self.upload_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))  # ✅ Switch to Upload Screen
        self.logout_button.clicked.connect(self.logout)  # ✅ Logout

        menu_widget.setLayout(layout)
        return menu_widget


    def create_upload_screen(self):
        """Creates the Upload UI"""
        upload_widget = QWidget()
        layout = QVBoxLayout()

        self.label_upload = QLabel("Upload an Excel file:")
        self.upload_button = QPushButton("Select File")
        self.process_button = QPushButton("Submit")
        self.back_button = QPushButton("Back to Menu")  # ✅ New Back Button

        layout.addWidget(self.label_upload)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.process_button)
        layout.addWidget(self.back_button)  # ✅ Add Back Button

        self.upload_button.clicked.connect(self.select_file)
        self.process_button.clicked.connect(self.upload_file)
        self.back_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))  # ✅ Switch to Menu Screen

        self.file_path = None
        upload_widget.setLayout(layout)
        return upload_widget

    def handle_login(self):
        """Handles user login"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Username and Password are required.")
            return

        response = session.post(API_LOGIN, json={"username": username, "password": password})

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Login Successful!")
            print("Login Cookies:", session.cookies.get_dict())  # Debugging
            self.stack.setCurrentIndex(1)  # ✅ Redirect to Main Menu
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def select_file(self):
        """Opens file selection dialog"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            self.file_path = file_path
            self.label_upload.setText(f"Selected: {file_path}")

    def upload_file(self):
        """Uploads selected file to backend"""
        if not self.file_path:
            self.label_upload.setText("Please select a file first.")
            return

        with open(self.file_path, "rb") as file:
            files = {"file": file}
            response = session.post(API_UPLOAD, files=files)  # ✅ Now session is defined

        print("Upload Response:", response.status_code, response.text)  # Debugging

        if response.status_code == 200:
            self.label_upload.setText("File processed successfully!")
        else:
            self.label_upload.setText(f"Error processing file: {response.text}")

    def logout(self):
        """Logs out the user and returns to login screen"""
        self.stack.setCurrentIndex(0)  # ✅ Go back to Login Screen
        self.username_input.clear()
        self.password_input.clear()
        QMessageBox.information(self, "Logged Out", "You have been logged out.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
