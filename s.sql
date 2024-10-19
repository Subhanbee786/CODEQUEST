-- Table to store students
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    program VARCHAR(50),
    year_of_study INT,
    attendance FLOAT,
    exam_scores FLOAT[],
    assignment_scores FLOAT[],
    health_issues TEXT,
    financial_issues TEXT,
    counseling_recommendations JSONB
);

-- Table to store performance logs
CREATE TABLE performance_logs (
    log_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    log_date DATE,
    attendance FLOAT,
    exam_score FLOAT,
    assignment_score FLOAT
);
