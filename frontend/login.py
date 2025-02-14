import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog

API_URL = "http://127.0.0.1:5000"
session = requests.Session()  # Store session

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)

        # UI Elements
        self.label = QLabel("Enter your credentials:", self)
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        # Event Handling
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
      username = self.username_input.text()
      password = self.password_input.text()

      if not username or not password:
          QMessageBox.warning(self, "Login Failed", "Username and Password are required.")
          return

      response = session.post(
          f"{API_URL}/login",
          json={"username": username, "password": password},
          headers={"Content-Type": "application/json"},  # Ensures proper format
      )

      if response.status_code == 200:
          QMessageBox.information(self, "Success", "Login Successful!")
          print("Login Cookies:", session.cookies.get_dict())  # Debugging
          self.open_upload_window()  # Proceed to upload
      else:
          QMessageBox.warning(self, "Error", "Invalid credentials")


    def open_upload_window(self):
        self.upload_window = UploadWindow()
        self.upload_window.show()
        self.close()

class UploadWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Upload")
        self.setGeometry(100, 100, 400, 200)

        # UI Elements
        self.label = QLabel("Select a file to upload:", self)
        self.upload_button = QPushButton("Choose File", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

        # Event Handling
        self.upload_button.clicked.connect(self.upload_file)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")

        if file_path:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = session.post(f"{API_URL}/upload", files=files)

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "File uploaded successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Upload failed: {response.text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
