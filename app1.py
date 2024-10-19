from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/student_counseling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(50))
    year_of_study = db.Column(db.Integer)
    attendance = db.Column(db.Float)
    exam_scores = db.Column(db.ARRAY(db.Float))
    assignment_scores = db.Column(db.ARRAY(db.Float))
    health_issues = db.Column(db.Text)
    financial_issues = db.Column(db.Text)
    counseling_recommendations = db.Column(JSONB)

class PerformanceLog(db.Model):
    __tablename__ = 'performance_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    log_date = db.Column(db.Date)
    attendance = db.Column(db.Float)
    exam_score = db.Column(db.Float)
    assignment_score = db.Column(db.Float)

# Machine Learning Model for Prediction
def analyze_student_performance(student_data):
    """
    A mock function that analyzes student data and returns recommendations.
    In reality, this would involve machine learning models like decision trees,
    or even simpler rule-based analysis based on the data provided.
    """
    attendance = student_data['attendance']
    avg_exam_score = np.mean(student_data['exam_scores'])
    avg_assignment_score = np.mean(student_data['assignment_scores'])

    if attendance < 75:
        attendance_issue = "Low attendance"
    else:
        attendance_issue = "Attendance is fine"
    
    if avg_exam_score < 50:
        exam_issue = "Poor exam performance"
    else:
        exam_issue = "Exam performance is fine"

    if avg_assignment_score < 60:
        assignment_issue = "Poor assignment performance"
    else:
        assignment_issue = "Assignment performance is fine"

    recommendations = {
        "academic_support": f"{exam_issue}, {assignment_issue}",
        "personal_support": "Consider improving time management skills.",
        "career_support": "Explore tutoring and mentorship programs."
    }

    return recommendations

@app.route('/analyze_student/<int:student_id>', methods=['GET'])
def analyze_student(student_id):
    student = Student.query.get(student_id)
    if student:
        # Prepare student data for analysis
        student_data = {
            "attendance": student.attendance,
            "exam_scores": student.exam_scores,
            "assignment_scores": student.assignment_scores
        }

        # Get recommendations using our model
        recommendations = analyze_student_performance(student_data)

        # Update recommendations in the database
        student.counseling_recommendations = recommendations
        db.session.commit()

        return jsonify(recommendations), 200
    else:
        return jsonify({"error": "Student not found"}), 404

# Graphical visualization of performance
@app.route('/student_performance_graph/<int:student_id>', methods=['GET'])
def student_performance_graph(student_id):
    student = Student.query.get(student_id)
    if student:
        dates = ['2024-01-01', '2024-02-01', '2024-03-01']  # Sample dates
        exam_scores = student.exam_scores
        assignment_scores = student.assignment_scores

        plt.figure(figsize=(10, 5))
        plt.plot(dates, exam_scores, label="Exam Scores", marker='o')
        plt.plot(dates, assignment_scores, label="Assignment Scores", marker='x')
        plt.xlabel('Dates')
        plt.ylabel('Scores')
        plt.title(f'Performance of {student.name}')
        plt.legend()

        # Convert plot to PNG image and return as base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({"graph": image_base64}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

# Add student data (for testing purposes)
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    student = Student(
        name=data['name'],
        program=data['program'],
        year_of_study=data['year_of_study'],
        attendance=data['attendance'],
        exam_scores=data['exam_scores'],
        assignment_scores=data['assignment_scores'],
        health_issues=data.get('health_issues', ''),
        financial_issues=data.get('financial_issues', '')
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Student added successfully!"}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
