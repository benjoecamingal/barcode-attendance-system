from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
import pandas as pd
import os
import random
import string
from db_config import get_db_connection  # Import MySQL database connection
from barcode_generator import generate_barcode
from docx import Document
from docx.shared import Pt
from barcode import Code128
from barcode.writer import ImageWriter
import time
# from barcode_image_generator import generate_barcode_image

# Flask App Configuration
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management
app.config['SESSION_COOKIE_NAME'] = 'my_session'  # Ensures session persistence
CORS(app, supports_credentials=True)  # Allow session cookies in CORS requests

UPLOAD_FOLDER = "../uploads/"
PROCESSED_FOLDER = os.path.abspath("../processed_files/")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


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

def generate_barcode_image(barcode_number, output_path):
    try:
        # Remove .png extension if it exists
        if output_path.endswith('.png'):
            output_path = output_path[:-4]
            
        # Create barcode
        barcode = Code128(str(barcode_number), writer=ImageWriter())
        
        # Make sure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save barcode - python-barcode will add .png extension automatically
        saved_path = barcode.save(output_path)
        print(f"Successfully saved barcode to: {saved_path}")
        
        return True
    except Exception as e:
        print(f"Error generating barcode: {str(e)}")
        return False

from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx import Document

from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx import Document
import os

def generate_word_document(dataframe, output_path, barcode_paths):
    doc = Document()

    section = doc.sections[0]
    section.page_height = Inches(11)  # Letter size height
    section.page_width = Inches(8.5)  # Letter size width
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    student_count = 0

    for index, row in dataframe.iterrows():
        name = row.get("Name", "Unknown")
        position = row.get("Position", "Unknown")
        department = row.get("Department", "Unknown")
        barcode_number = row.get("Barcode", "")

        if not barcode_number:
            continue

        barcode_path = barcode_paths.get(barcode_number)

        if not barcode_path or not os.path.exists(barcode_path):
            continue

        # Add Name (Centered, Large, Bold)
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  
        run = paragraph.add_run(f"{name}\n")
        run.bold = True
        run.font.size = Pt(20)  # Set font size to 20

        # Add Position (Centered)
        p_pos = doc.add_paragraph(f"Position: {position}")
        p_pos.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Add Department (Centered)
        p_dept = doc.add_paragraph(f"Department: {department}")
        p_dept.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Add Barcode Image (Centered)
        try:
            p_img = doc.add_paragraph()
            p_img.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            run_img = p_img.add_run()
            run_img.add_picture(barcode_path, width=Inches(2.5))  # Adjust width to be readable
        except Exception as e:
            error_p = doc.add_paragraph("[ERROR: Could not add barcode image]")
            error_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Add Separator Line (Centered)
        p_line = doc.add_paragraph("-" * 30)  # Create separator line
        p_line.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Ensure it's centered

        # Two students per page
        student_count += 1
        if student_count % 2 == 0:
            doc.add_page_break()

    try:
        doc.save(output_path)
    except Exception as e:
        print(f"Error saving document: {str(e)}")


def generate_unique_barcode(cursor):
    """Generate a unique barcode ensuring no duplicates in the database."""
    while True:
        barcode = generate_barcode()
        cursor.execute("SELECT COUNT(*) FROM students WHERE barcode = %s", (barcode,))
        if cursor.fetchone()[0] == 0:
            return barcode

# File Upload & Barcode Processing
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Read the Excel file
    df = pd.read_excel(file_path, engine="openpyxl")

    # ✅ Remove empty rows
    df.dropna(how="all", inplace=True)

    # ✅ Fill NaN values with empty strings to prevent MySQL errors
    df.fillna("", inplace=True)

    if df.empty:
        return jsonify({"error": "Uploaded file is empty"}), 400

    # ✅ Connect to database
    db = get_db_connection()
    cursor = db.cursor()

    # ✅ Ensure "Barcode" column is auto-generated
    if "Barcode" not in df.columns:
        df["Barcode"] = df.apply(lambda _: generate_unique_barcode(cursor), axis=1)

    # ✅ Generate barcode images BEFORE inserting them into Word
    barcode_paths = {}
    for _, row in df.iterrows():
        barcode_number = row["Barcode"]
        # Construct path without .png extension
        base_path = os.path.join(PROCESSED_FOLDER, f"barcode_{barcode_number}")
        barcode_path = f"{base_path}.png"  # Add .png for the final path
        
        # Generate barcode (pass path without extension)
        if generate_barcode_image(barcode_number, base_path):
            barcode_paths[barcode_number] = barcode_path
        else:
            print(f"Failed to generate barcode for: {barcode_number}")

    # ✅ Register all students in the database
    for _, row in df.iterrows():
        student_dict = row.to_dict()
        columns = ", ".join(student_dict.keys())
        placeholders = ", ".join(["%s"] * len(student_dict))
        values = tuple(student_dict.values())

        query = f"INSERT INTO students ({columns}) VALUES ({placeholders})"
        try:
            cursor.execute(query, values)
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 400

    db.commit()
    cursor.close()
    db.close()

    # time.sleep(5)
    # ✅ Generate Word File
    output_docx = os.path.join(PROCESSED_FOLDER, "student_barcodes.docx")
    generate_word_document(df, output_docx, barcode_paths)

    return send_file(output_docx, as_attachment=True)


    

@app.route("/add_student", methods=["POST"])
def add_student():
    """Handles adding an individual student to the database"""
    print("Session at /add_student:", session)  # Debugging

    # Check if the user is authenticated
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403  

    # Ensure request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Invalid request format. JSON required"}), 400  

    data = request.get_json()

    # Extract and validate required fields
    required_fields = ["name", "batch", "position", "department", "school"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400  

    name = data["name"].strip()
    batch = data["batch"].strip()
    position = data["position"].strip()
    department = data["department"].strip()
    school = data["school"].strip()

    try:
        # Insert into database
        db = get_db_connection()
        cursor = db.cursor()
        query = """INSERT INTO students (name, batch, position, department, school, barcode)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        barcode = generate_barcode() 
        cursor.execute(query, (name, batch, position, department, school, barcode))
        db.commit()
        cursor.close()

        return jsonify({"message": "Student added successfully!"}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": "Database error", "details": str(e)}), 500


# Logout Route
@app.route("/logout", methods=["POST"])
def logout():
    """Handles user logout"""
    session.pop("user", None)  # Remove user from session
    return jsonify({"message": "Logged out successfully"}), 200


@app.route('/scan', methods=['POST'])
def process_scan():
    """Handles barcode scanning requests from PyQt GUI"""
    data = request.get_json()
    barcode = data.get("barcode")

    if not barcode:
        return jsonify({"success": False, "message": "No barcode received"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if student exists
        cursor.execute("SELECT id, name, department FROM students WHERE barcode = %s", (barcode,))
        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Student not found"}), 404

        student_id, student_name, department = student

        # Clear any unread results before executing the next query
        cursor.fetchall()

        # Check if the student already has a time_in for today
        cursor.execute(
            "SELECT id, time_in, time_out FROM attendance WHERE student_id = %s AND date = CURDATE()",
            (student_id,)
        )
        record = cursor.fetchone()

        if record:
            attendance_id, time_in, time_out = record

            # Clear any unread results before the next query
            cursor.fetchall()

            if time_in and not time_out:
                # Second scan → Time Out
                cursor.execute(
                    "UPDATE attendance SET time_out = CURRENT_TIME WHERE id = %s",
                    (attendance_id,)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({
                    "success": True,
                    "message": f"✅ Time Out recorded for {student_name}",
                    "name": student_name,
                    "department": department,
                    "time": time_out,
                    "status": "Time Out",
                    "date": "Today"
                })
            else:
                cursor.close()
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "❌ Already Timed Out for Today"
                })
        else:
            # First scan → Time In
            cursor.execute(
                "INSERT INTO attendance (student_id, date, time_in) VALUES (%s, CURDATE(), CURRENT_TIME)",
                (student_id,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                "success": True,
                "message": f"✅ Time In recorded for {student_name}",
                "name": student_name,
                "department": department,
                "time": "Now",
                "status": "Time In",
                "date": "Today"
            })

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500
    

@app.route('/attendance', methods=['GET'])
def get_attendance():
    """Fetch attendance records with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get filters from request
        batch = request.args.get('batch')
        position = request.args.get('position')
        department = request.args.get('department')
        date = request.args.get('date')  # Format: YYYY-MM-DD

        # Start SQL Query
        query = """
            SELECT s.name, s.batch, s.position, s.department, 
                   a.date, a.time_in, a.time_out
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE 1=1
        """
        filters = []

        # Add filters dynamically
        if batch:
            query += " AND s.batch = %s"
            filters.append(batch)
        if position:
            query += " AND s.position = %s"
            filters.append(position)
        if department:
            query += " AND s.department = %s"
            filters.append(department)
        if date:
            query += " AND a.date = %s"
            filters.append(date)

        query += " ORDER BY a.date DESC"

        # Execute the query with filters
        cursor.execute(query, tuple(filters))
        records = cursor.fetchall()

        # Convert time fields to string
        for record in records:
            record["time_in"] = str(record["time_in"]) if record["time_in"] else "N/A"
            record["time_out"] = str(record["time_out"]) if record["time_out"] else "N/A"

        return jsonify(records)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/filters', methods=['GET'])
def get_filters():
    """Fetch distinct values for Batch, Position, and Department from database"""
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT DISTINCT batch FROM students WHERE batch IS NOT NULL")
        batches = [row["batch"] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT position FROM students WHERE position IS NOT NULL")
        positions = [row["position"] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT department FROM students WHERE department IS NOT NULL")
        departments = [row["department"] for row in cursor.fetchall()]

        return jsonify({
            "batches": batches,
            "positions": positions,
            "departments": departments
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()
# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
