from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import re
from datetime import datetime

app = Flask(_name_)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------
# Database Models
# ----------------------

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employee.employee_id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)

# ----------------------
# Routes
# ----------------------

@app.route('/')
def home():
    return render_template("index.html")

# ----------------------
# Add Employee
# ----------------------

@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.json

    if not all(k in data for k in ("employee_id", "full_name", "email", "department")):
        return jsonify({"error": "All fields are required"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({"error": "Invalid email format"}), 400

    if Employee.query.filter_by(employee_id=data['employee_id']).first():
        return jsonify({"error": "Employee ID already exists"}), 409

    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409

    new_employee = Employee(
        employee_id=data['employee_id'],
        full_name=data['full_name'],
        email=data['email'],
        department=data['department']
    )

    db.session.add(new_employee)
    db.session.commit()

    return jsonify({"message": "Employee added successfully"}), 201

# ----------------------
# Get Employees
# ----------------------

@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    result = []
    for emp in employees:
        result.append({
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "email": emp.email,
            "department": emp.department
        })
    return jsonify(result), 200

# ----------------------
# Delete Employee
# ----------------------

@app.route('/api/employees/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    emp = Employee.query.filter_by(employee_id=employee_id).first()
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    db.session.delete(emp)
    db.session.commit()
    return jsonify({"message": "Employee deleted"}), 200

# ----------------------
# Mark Attendance
# ----------------------

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.json

    if not all(k in data for k in ("employee_id", "date", "status")):
        return jsonify({"error": "All fields are required"}), 400

    if data['status'] not in ["Present", "Absent"]:
        return jsonify({"error": "Status must be Present or Absent"}), 400

    emp = Employee.query.filter_by(employee_id=data['employee_id']).first()
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    attendance = Attendance(
        employee_id=data['employee_id'],
        date=data['date'],
        status=data['status']
    )

    db.session.add(attendance)
    db.session.commit()

    return jsonify({"message": "Attendance marked"}), 201

# ----------------------
# Get Attendance
# ----------------------

@app.route('/api/attendance/<employee_id>', methods=['GET'])
def get_attendance(employee_id):
    records = Attendance.query.filter_by(employee_id=employee_id).all()
    result = []
    for rec in records:
        result.append({
            "date": rec.date,
            "status": rec.status
        })
    return jsonify(result), 200


if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)