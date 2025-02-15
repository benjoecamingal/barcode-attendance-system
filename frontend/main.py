import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QStackedWidget,
    QDesktopWidget, QSizePolicy, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
import requests

API_LOGIN = "http://127.0.0.1:5000/login"
API_UPLOAD = "http://127.0.0.1:5000/upload"
API_STUDENT = "http://127.0.0.1:5000/add_student"
API_ATTENDANCE = "http://127.0.0.1:5000/attendance"
API_FILTERS = "http://127.0.0.1:5000/filters"

session = requests.Session()

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        # Set Window Icon
        self.setWindowIcon(QIcon("static/favicon.ico"))  # Use PNG or ICO file

        self.setWindowTitle("Creo.log")
        self.resize(1000, 600)  # ✅ Step 2: Set larger size
        self.center_window()    # ✅ Step 1: Center the window


        # Create Stacked Layout (to switch between Login and Upload UI)
        self.stack = QStackedWidget(self)

        # Create Login and Upload Screens
        self.login_screen = self.create_login_screen()
        self.menu_screen = self.create_menu_screen() 
        self.upload_screen = self.create_upload_screen()
        self.add_student_screen = self.create_add_student_screen()
        self.attendance_history_screen = self.create_attendance_history_screen()

        # Add Screens to Stack
        self.stack.addWidget(self.login_screen)  # Index 0
        self.stack.addWidget(self.menu_screen)   # Index 1
        self.stack.addWidget(self.upload_screen) # Index 2
        self.stack.addWidget(self.add_student_screen) # Index 3
        self.stack.addWidget(self.attendance_history_screen)  # Index 4


        

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
    
    def create_add_student_screen(self):
        """Creates the 'Add Student Individually' screen"""
        student_widget = QWidget()
        layout = QVBoxLayout(student_widget)

        self.name_input = QLineEdit()
        self.batch_input = QLineEdit()
        self.position_input = QLineEdit()
        self.department_input = QLineEdit()
        self.school_input = QLineEdit()

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit_student)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))  # Go back to the menu

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Batch:"))
        layout.addWidget(self.batch_input)
        layout.addWidget(QLabel("Position:"))
        layout.addWidget(self.position_input)
        layout.addWidget(QLabel("Department:"))
        layout.addWidget(self.department_input)
        layout.addWidget(QLabel("School:"))
        layout.addWidget(self.school_input)
        layout.addWidget(submit_btn)
        layout.addWidget(back_btn)

        return student_widget

    

    def create_menu_screen(self):
        """Creates the Main Menu UI after login"""
        menu_widget = QWidget()
        layout = QVBoxLayout()

        self.label_menu = QLabel("Welcome! Select an option:")
        self.add_student_btn = QPushButton("Add Students Individually")
        self.upload_button = QPushButton("Upload Excel File")
        self.attendance_history_btn = QPushButton("View Attendance History")  # ✅ New Button
        self.logout_button = QPushButton("Logout")

        # Add to Layout
        layout.addWidget(self.label_menu)
        layout.addWidget(self.add_student_btn)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.attendance_history_btn)  # ✅ Add Attendance History Button
        layout.addWidget(self.logout_button)

        # Set Button Actions
        self.upload_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))  # ✅ Switch to Upload Screen
        self.logout_button.clicked.connect(self.logout)  # ✅ Logout
        self.attendance_history_btn.clicked.connect(lambda: self.load_attendance_data())  # ✅ Load attendance table
        self.add_student_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3)) 

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
    
    def create_attendance_history_screen(self):
        """Creates the Attendance History Screen with dynamic filters"""
        history_widget = QWidget()
        layout = QVBoxLayout()

        self.label_history = QLabel("Attendance History")

        self.batch_filter = QComboBox()      # 🟢 Define batch_filter
        self.position_filter = QComboBox()   # 🟢 Define position_filter
        self.department_filter = QComboBox() # 🟢 Define department_filter

        # Date Picker
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())

        # Load filter options from the database
        self.load_filters()

        # Filter Button
        self.filter_button = QPushButton("Apply Filter")
        self.refresh_button = QPushButton("Refresh")
        self.filter_button.clicked.connect(self.load_attendance_data)
        self.refresh_button.clicked.connect(self.load_attendance_data)

        # Create the Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # Name, Batch, Position, Department, Date, Time In, Time Out
        self.table.setHorizontalHeaderLabels(["Name", "Batch", "Position", "Department", "Date", "Time In", "Time Out"])

        layout.addWidget(self.label_history)
        layout.addWidget(QLabel("Batch:"))
        layout.addWidget(self.batch_filter)
        layout.addWidget(QLabel("Position:"))
        layout.addWidget(self.position_filter)
        layout.addWidget(QLabel("Department:"))
        layout.addWidget(self.department_filter)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.date_filter)
        layout.addWidget(self.filter_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.table)

        # Back Button
        self.back_to_menu_button = QPushButton("Back to Menu")
        self.back_to_menu_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(self.back_to_menu_button)

        history_widget.setLayout(layout)
        return history_widget

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

        # print("Upload Response:", response.status_code, response.text)  # Debugging

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

    def submit_student(self):
        """Handles adding a student to the database"""
        data = {
            "name": self.name_input.text(),
            "batch": self.batch_input.text(),
            "position": self.position_input.text(),
            "department": self.department_input.text(),
            "school": self.school_input.text(),
        }

        response = session.post(API_STUDENT, json=data)

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Student added successfully!")
            self.stack.setCurrentIndex(1)  # Return to menu
        else:
            QMessageBox.critical(self, "Error", "Failed to add student.")

    

    def load_attendance_data(self):
        """Fetch attendance data from backend with selected filters"""
        params = {
            "batch": self.batch_filter.currentData(),  # Get selected batch value
            "position": self.position_filter.currentData(),  # Get selected position value
            "department": self.department_filter.currentData(),  # Get selected department value
            "date": self.date_filter.date().toString("yyyy-MM-dd"),
        }

        response = session.get(API_ATTENDANCE, params=params)

        if response.status_code == 200:
            data = response.json()

            # Populate Table
            self.table.setRowCount(len(data))

            for row_idx, record in enumerate(data):
                self.table.setItem(row_idx, 0, QTableWidgetItem(record["name"]))
                self.table.setItem(row_idx, 1, QTableWidgetItem(record["batch"]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(record["position"]))
                self.table.setItem(row_idx, 3, QTableWidgetItem(record["department"]))
                self.table.setItem(row_idx, 4, QTableWidgetItem(record["date"]))
                self.table.setItem(row_idx, 5, QTableWidgetItem(record["time_in"] or "N/A"))
                self.table.setItem(row_idx, 6, QTableWidgetItem(record["time_out"] or "N/A"))

            self.stack.setCurrentIndex(4)  # ✅ Switch to Attendance History Panel
        else:
            QMessageBox.critical(self, "Error", "Failed to load attendance records.")

    def load_filters(self):
        """Fetch batch, position, and department options from database"""
        response = session.get(API_FILTERS)

        if response.status_code == 200:
            data = response.json()

            # ✅ Populate Batch Dropdown (Remove Extra Spaces)
            self.batch_filter.clear()
            self.batch_filter.addItem("All", "")
            for batch in data["batches"]:
                self.batch_filter.addItem(batch.strip(), batch.strip())

            # ✅ Populate Position Dropdown (Remove Extra Spaces)
            self.position_filter.clear()
            self.position_filter.addItem("All", "")
            for position in data["positions"]:
                self.position_filter.addItem(position.strip(), position.strip())

            # ✅ Populate Department Dropdown (Remove Extra Spaces)
            self.department_filter.clear()
            self.department_filter.addItem("All", "")
            for department in data["departments"]:
                self.department_filter.addItem(department.strip(), department.strip())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
