import subprocess
import sys

dependencies = [
    "flask", "flask-cors", "mysql-connector-python",
    "pyqt5", "opencv-python", "numpy", "requests", "pandas", "openpyxl"
]

subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)
print("✅ Installation complete!")
