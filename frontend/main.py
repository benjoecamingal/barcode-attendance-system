import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QStackedWidget,
    QDesktopWidget, QSizePolicy, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QFrame, QScrollArea,
    QScrollArea, QHBoxLayout, QGridLayout
)


from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIcon, QFont
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
        self.setWindowIcon(QIcon("static/favicon.ico"))
        self.setWindowTitle("Creo.log")
        self.resize(800, 600)
        self.center_window()
        
        # Set window background to white
        self.setStyleSheet("background-color: white;")

        # Create Stacked Layout
        self.stack = QStackedWidget(self)
        
        # Create all screens
        self.login_screen = self.create_login_screen()
        self.menu_screen = self.create_menu_screen()
        self.upload_screen = self.create_upload_screen()
        self.add_student_screen = self.create_add_student_screen()
        self.attendance_history_screen = self.create_attendance_history_screen()

        # Add Screens to Stack
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.upload_screen)
        self.stack.addWidget(self.add_student_screen)
        self.stack.addWidget(self.attendance_history_screen)

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
        """Creates the Login UI with updated design"""
        login_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Create a container for the logo
        logo_container = QWidget()
        logo_layout = QVBoxLayout()
        
        # Create and style the CREOTEC text
        company_name = QLabel("CREOTEC")
        company_name.setStyleSheet("""
            QLabel {
                color: #000080;
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        company_name.setAlignment(Qt.AlignCenter)
        
        # Create and style the subtitle
        subtitle = QLabel("PHILIPPINES, INC.")
        subtitle.setStyleSheet("""
            QLabel {
                color: #000080;
                font-size: 12px;
                letter-spacing: 1px;
                margin-top: -10px;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Add logo elements to logo container
        logo_layout.addWidget(company_name)
        logo_layout.addWidget(subtitle)
        logo_container.setLayout(logo_layout)
        
        # Create login form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border-radius: 8px;
                padding: 20px;
                min-width: 300px;
                max-width: 400px;
            }
        """)
        form_layout = QVBoxLayout()
        
        # Style the input fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #4f46e5;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #4f46e5;
            }
        """)
        
        # Style the login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #312e81;
                color: white;
                padding: 12px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #312e81;
            }
        """)
        
        # Add widgets to form layout
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        form_container.setLayout(form_layout)
        
        # Add all elements to main layout with proper spacing
        layout.addStretch(1)
        layout.addWidget(logo_container)
        layout.addSpacing(40)  # Space between logo and form
        layout.addWidget(form_container, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        
        # Connect login button
        self.login_button.clicked.connect(self.handle_login)
        
        login_widget.setLayout(layout)
        return login_widget

    
    def create_add_student_screen(self):
        """Creates a compact, scrollable 'Add Student' screen"""
        # Create main widget
        student_widget = QWidget()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Create container widget for scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        title_label = QLabel("Add New Student")
        title_label.setStyleSheet("""
            QLabel {
                color: #312e81;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)
        
        # Input styles
        input_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4f46e5;
            }
        """
        
        label_style = """
            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: bold;
            }
        """
        
        # Create and style input fields
        fields = [
            ("Name:", "name_input", "Enter student's full name"),
            ("Batch:", "batch_input", "Enter batch number/name"),
            ("Position:", "position_input", "Enter student's position"),
            ("Department:", "department_input", "Enter department name"),
            ("School:", "school_input", "Enter school name")
        ]
        
        for label_text, input_name, placeholder in fields:
            field_container = QWidget()
            field_layout = QHBoxLayout()
            field_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setFixedWidth(80)  # Fixed width for labels
            
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setStyleSheet(input_style)
            setattr(self, input_name, input_field)
            
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)
            field_container.setLayout(field_layout)
            form_layout.addWidget(field_container)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Submit button
        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #312e81;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                padding: 8px 16px;
                border-radius: 4px;
                border: 1px solid #e5e7eb;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        
        button_layout.addWidget(back_btn)
        button_layout.addWidget(submit_btn)
        button_container.setLayout(button_layout)
        
        # Connect buttons
        submit_btn.clicked.connect(self.submit_student)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        # Add everything to layouts
        form_container.setLayout(form_layout)
        layout.addWidget(title_label)
        layout.addWidget(form_container)
        layout.addWidget(button_container)
        layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(student_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        return student_widget

    def create_menu_screen(self):
        """Creates a modern, clean Menu UI"""
        menu_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Add space between elements
        
        # Create header container
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: #312e81;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QVBoxLayout()
        
        # Welcome text
        welcome_label = QLabel("Welcome to Creo.log")
        welcome_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Select an option to get started")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #e5e7eb;
                font-size: 14px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(welcome_label)
        header_layout.addWidget(subtitle_label)
        header_container.setLayout(header_layout)
        
        # Create button container
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        button_layout = QVBoxLayout()
        
        # Style for all menu buttons
        button_style = """
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                border: 1px solid #d1d5db;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
        """
        
        # Create menu buttons
        self.add_student_btn = QPushButton("➕  Add Students Individually")
        self.upload_button = QPushButton("📊  Upload Excel File")
        self.attendance_history_btn = QPushButton("📋  View Attendance History")
        self.logout_button = QPushButton("🚪  Logout")
        
        # Apply styles
        for button in [self.add_student_btn, self.upload_button, 
                    self.attendance_history_btn, self.logout_button]:
            button.setStyleSheet(button_style)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button_layout.addWidget(button)
        
        # Style logout button differently
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                color: #dc2626;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background-color: #fecaca;
                border: 1px solid #fca5a5;
            }
        """)
        
        button_container.setLayout(button_layout)
        
        # Add everything to main layout
        layout.addWidget(header_container)
        layout.addWidget(button_container)
        
        # Connect button actions
        self.upload_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.logout_button.clicked.connect(self.logout)
        self.attendance_history_btn.clicked.connect(lambda: self.load_attendance_data())
        self.add_student_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        menu_widget.setLayout(layout)
        return menu_widget
    

    def create_upload_screen(self):
        """Creates a modern Upload UI screen matching add_student style"""
        upload_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Upload Excel File")
        title_label.setStyleSheet("""
            QLabel {
                color: #312e81;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # File selection label
        self.label_upload = QLabel("No file selected")
        self.label_upload.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 13px;
                padding: 10px;
                background-color: #f3f4f6;
                border-radius: 4px;
                border: 1px solid #e5e7eb;
            }
        """)
        self.label_upload.setAlignment(Qt.AlignCenter)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Style buttons
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
        """
        
        # Upload button
        self.upload_button = QPushButton("Select File")
        self.upload_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #312e81;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        
        # Process button
        self.process_button = QPushButton("Submit")
        self.process_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #312e81;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        
        # Back button
        self.back_button = QPushButton("Back to Menu")
        self.back_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #e5e7eb;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        
        # Add buttons to layout
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.process_button)
        button_container.setLayout(button_layout)
        
        # Add widgets to form layout
        form_layout.addWidget(self.label_upload)
        form_container.setLayout(form_layout)
        
        # Add everything to main layout
        layout.addWidget(title_label)
        layout.addWidget(form_container)
        layout.addWidget(button_container)
        layout.addStretch()
        
        # Connect buttons
        self.upload_button.clicked.connect(self.select_file)
        self.process_button.clicked.connect(self.upload_file)
        self.back_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        self.file_path = None
        upload_widget.setLayout(layout)
        return upload_widget

    def create_attendance_history_screen(self):
        """Creates a modern Attendance History screen with properly initialized components"""
        history_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Initialize filter components first
        self.batch_filter = QComboBox()
        self.position_filter = QComboBox()
        self.department_filter = QComboBox()


        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())

        calendar = self.date_filter.calendarWidget()
        calendar.setStyleSheet("""
            QCalendarWidget {
                min-width: 250px;
                min-height: 250px;
            }
            QCalendarWidget QToolButton {
                height: 30px;
                width: 100px;
                color: black;
                font-size: 12px;
                icon-size: 24px;
                background-color: white;
            }
            QCalendarWidget QMenu {
                width: 150px;
                left: 20px;
                color: black;
                font-size: 12px;
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                width: 60px;
                font-size: 12px;
                color: black;
                background-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 12px;
                color: black;
                background-color: white;
                selection-background-color: #312e81;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #808080;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f3f4f6;
            }
        """)
        
        # Title
        title_label = QLabel("Attendance History")
        title_label.setStyleSheet("""
            QLabel {
                color: #312e81;
                font-size: 18px;
                font-weight: bold;
                padding-bottom: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Filter container
        filter_container = QFrame()
        filter_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        filter_layout = QGridLayout()
        filter_layout.setSpacing(10)
        
        # Style for labels and comboboxes
        label_style = """
            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: bold;
            }
        """
        
        combo_style = """
            QComboBox {
                padding: 8px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid #4338ca;
            }
        """
        
        # Create and style filters
        filters = [
            ("Batch:", self.batch_filter),
            ("Position:", self.position_filter),
            ("Department:", self.department_filter)
        ]
        
        for row, (label_text, combo) in enumerate(filters):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            combo.setStyleSheet(combo_style)
            filter_layout.addWidget(label, row, 0)
            filter_layout.addWidget(combo, row, 1)
        
        # Date filter
        date_label = QLabel("Date:")
        date_label.setStyleSheet(label_style)
        self.date_filter.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
            }
        """)
        filter_layout.addWidget(date_label, 3, 0)
        filter_layout.addWidget(self.date_filter, 3, 1)
        
        filter_container.setLayout(filter_layout)
        
        # Initialize and style table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Name", "Batch", "Position", "Department", "Date", "Time In", "Time Out"])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 8px;
                border: none;
                border-right: 1px solid #e5e7eb;
                border-bottom: 1px solid #e5e7eb;
                font-weight: bold;
                color: #374151;
            }
        """)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout()
        
        # Style buttons
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
        """
        
        # Create buttons
        filter_button = QPushButton("Apply Filter")
        filter_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #312e81;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)

        download_button = QPushButton("Download Results")
        download_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #047857;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #312e81;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
        """)
        
        back_button = QPushButton("Back to Menu")
        back_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #e5e7eb;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        
        # Add buttons to layout
        button_layout.addWidget(back_button)
        button_layout.addStretch()
        button_layout.addWidget(filter_button)
        button_layout.addWidget(download_button)
        button_layout.addWidget(refresh_button)
        button_container.setLayout(button_layout)
        
        # Connect buttons
        filter_button.clicked.connect(self.load_attendance_data)
        refresh_button.clicked.connect(self.load_attendance_data)
        back_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        download_button.clicked.connect(self.download_attendance_data)
        
        # Load initial filter data
        self.load_filters()
        
        # Add everything to main layout
        layout.addWidget(title_label)
        layout.addWidget(filter_container)
        layout.addWidget(self.table)
        layout.addWidget(button_container)
        
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


    # Add new method to handle downloading attendance data
    def download_attendance_data(self):
        """Downloads filtered attendance data as Excel file"""
        # Get current filter values
        batch = self.batch_filter.currentText()
        position = self.position_filter.currentText()
        department = self.department_filter.currentText()
        date = self.date_filter.date().toString("yyyy-MM-dd")
        
        # Only include non-"All" values
        params = {}
        if batch and batch != "All":
            params["batch"] = batch
        if position and position != "All":
            params["position"] = position
        if department and department != "All":
            params["department"] = department
        if date:
            params["date"] = date
            
        response = session.get(f"{API_ATTENDANCE}/download", params=params)
        
        if response.status_code == 200:
            # Open file dialog to choose save location
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Save Attendance Report",
                "",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                    
                # Save the file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Attendance report has been downloaded to:\n{file_path}"
                )
        elif response.status_code == 404:
            QMessageBox.warning(
                self,
                "No Data",
                "No attendance records found for the selected filters."
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to download attendance report."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
