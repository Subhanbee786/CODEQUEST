from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(_name_)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name' # Update with your credentials
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change to a secure key
db = SQLAlchemy(app)
jwt = JWTManager(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # Store hashed password
    academic_performance = db.Column(db.Text)
    interests = db.Column(db.Text)
    career_preferences = db.Column(db.Text)

class Counselor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # Store hashed password

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    counselor_id = db.Column(db.Integer, db.ForeignKey('counselor.id'))
    appointment_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    new_student = Student(
        name=data['name'],
        email=data['email'],
        password=data['password'],  # Hash this before storing
        academic_performance='{}',
        interests='',
        career_preferences=''
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(message="Student registered successfully."), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    student = Student.query.filter_by(email=data['email']).first()
    if student and student.password == data['password']:  # Check hashed password in a real app
        access_token = create_access_token(identity=student.id)
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401

@app.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_data(student_id):
    student = Student.query.get(student_id)
    if student:
        return jsonify({
            'name': student.name,
            'email': student.email,
            'academic_performance': student.academic_performance,
            'interests': student.interests,
            'career_preferences': student.career_preferences
        }), 200
    return jsonify(message="Student not found"), 404

# Add more routes for counselors, appointments, and analytics

if _name_ == '_main_':
    db.create_all()  # Create tables
    app.run(debug=True)