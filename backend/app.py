from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import os
import random
import string
from db_config import get_db_connection  # Import MySQL database connection
from barcode_generator import generate_barcode

# Flask App Configuration
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management
app.config['SESSION_COOKIE_NAME'] = 'my_session'  # Ensures session persistence
CORS(app, supports_credentials=True)  # Allow session cookies in CORS requests

UPLOAD_FOLDER = "../uploads/"
PROCESSED_FOLDER = "../processed_files/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Function to generate random barcodes
def generate_barcode():
    """Generates a random barcode (8 characters)"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Login Route
@app.route("/login", methods=["POST"])
def login():
    """Handles user login"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    db.close()

    if user:
        session["user"] = username  # Store session
        session.permanent = True  # Ensure session persists
        print("Session after login:", session)  # Debugging
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# File Upload & Barcode Processing
@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles file upload and barcode generation"""
    print("Session at /upload:", session)  # Debugging

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403  # This is causing the issue

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the uploaded file
        original_filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, original_filename)
        file.save(file_path)

        # Debug: Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not saved properly"}), 500

        # Read Excel file with error handling
        try:
            df = pd.read_excel(file_path, engine="openpyxl")  # Ensures compatibility with newer Excel formats
        except Exception as e:
            return jsonify({"error": "Failed to read Excel file", "details": str(e)}), 500

        # Debug: Print column names
        df.columns = df.columns.str.strip()
        print("Excel Columns:", df.columns.tolist())

        # Ensure "Name" column exists
        if "Name" not in df.columns:
            return jsonify({"error": "Missing 'Name' column in Excel file"}), 400

        # Drop empty rows
        df.dropna(subset=["Name"], inplace=True)

        # Generate and add barcode column
        df["Barcode"] = df["Name"].apply(lambda x: generate_barcode() if pd.notna(x) else "")

        # Save processed file
        processed_filename = f"{os.path.splitext(original_filename)[0]}_processed.xlsx"
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        df.to_excel(processed_path, index=False, engine="openpyxl")

        # Insert each row into the database
        db = get_db_connection()
        cursor = db.cursor()

        for _, row in df.iterrows():
            barcode = generate_barcode()  # Generate unique barcode
            try:
                cursor.execute(
                    "INSERT INTO students (name, batch, position, department, school, barcode) VALUES (%s, %s, %s, %s, %s, %s)",
                    (row["Name"], row["Batch"], row["Position"], row["Department"], row["School"], barcode),
                )
                db.commit()
            except Exception as e:
                db.rollback()
                return jsonify({"error": "Database insertion failed", "details": str(e)}), 500


        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "File processed successfully", "processed_file": processed_filename}), 200

    except Exception as e:
        print("Error processing file:", str(e))
        return jsonify({"error": "Error processing file", "details": str(e)}), 500

# Logout Route
@app.route("/logout", methods=["POST"])
def logout():
    """Handles user logout"""
    session.pop("user", None)  # Remove user from session
    return jsonify({"message": "Logged out successfully"}), 200

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
