from flask import Flask, request, jsonify
import sqlite3
import jwt

app = Flask(__name__)

# Secret key for JWT
secret_key = 'your-secret-key'

# SQLite database setup
conn = sqlite3.connect(':memory:', check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, createdBy TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, assignmentId INTEGER, studentId TEXT, submission TEXT, grade INTEGER)")

# Mock user data (for demo purposes)
cur.execute("INSERT INTO users (username, password, role) VALUES ('teacher', 'teacherpassword', 'teacher')")
cur.execute("INSERT INTO users (username, password, role) VALUES ('student', 'studentpassword', 'student')")

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if user:
        return jsonify({'message': 'Username already exists'}), 409
    else:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    
# Login endpoint
# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Debug statement to log received credentials
    print(f"Received credentials - Username: {username}, Password: {password}")

    try:
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()

        if user:
            try:
                token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
                return jsonify({'token': token})
            except jwt.PyJWTError as e:
                print(f"Token generation error: {e}")
                return jsonify({'message': 'Token generation error'}), 500
        else:
            print("Invalid username or password")  # Debug statement
            return jsonify({'message': 'Invalid username or password'}), 401
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
        return jsonify({'message': 'Database error'}), 500

# Middleware to authenticate JWT token
def authenticate_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Authorization header missing'}), 401

        try:
            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            kwargs['user'] = decoded_token
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

# Create new assignment
@app.route('/assignments', methods=['POST'])
@authenticate_token
def create_assignment(user):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    createdBy = user['username']

    cur.execute("INSERT INTO assignments (title, description, createdBy) VALUES (?, ?, ?)", (title, description, createdBy))
    conn.commit()
    return jsonify({'message': 'Assignment created successfully', 'id': cur.lastrowid})

# Get all assignments
@app.route('/assignments', methods=['GET'])
@authenticate_token
def get_assignments(user):
    cur.execute("SELECT * FROM assignments")
    assignments = cur.fetchall()
    return jsonify(assignments)

# Update assignment
@app.route('/assignments/<int:id>', methods=['PUT'])
@authenticate_token
def update_assignment(id, user):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    role = user['role']

    if role != 'teacher':
        return jsonify({'message': 'Only teachers can update assignments'}), 403

    cur.execute("UPDATE assignments SET title = ?, description = ? WHERE id = ? AND createdBy = ?", (title, description, id, user['username']))
    if cur.rowcount == 0:
        return jsonify({'message': 'You are not authorized to update this assignment'}), 403
    conn.commit()
    return jsonify({'message': 'Assignment updated successfully'})

# Delete assignment
@app.route('/assignments/<int:id>', methods=['DELETE'])
@authenticate_token
def delete_assignment(id, user):
    role = user['role']

    if role != 'teacher':
        return jsonify({'message': 'Only teachers can delete assignments'}), 403

    cur.execute("DELETE FROM assignments WHERE id = ? AND createdBy = ?", (id, user['username']))
    if cur.rowcount == 0:
        return jsonify({'message': 'You are not authorized to delete this assignment'}), 403
    conn.commit()
    return jsonify({'message': 'Assignment deleted successfully'})

# Ability for students to submit assignments
@app.route('/assignments/<int:id>/submit', methods=['POST'])
@authenticate_token
def submit_assignment(id, user):
    data = request.json
    submission = data.get('submission')
    studentId = user['username']

    cur.execute("INSERT INTO submissions (assignmentId, studentId, submission) VALUES (?, ?, ?)", (id, studentId, submission))
    conn.commit()
    return jsonify({'message': 'Assignment submitted successfully', 'id': cur.lastrowid})

# Ability for teachers to grade assignments
@app.route('/assignments/<int:id>/grade', methods=['PUT'])
@authenticate_token
def grade_assignment(id, user):
    data = request.json
    grade = data.get('grade')

    cur.execute("UPDATE submissions SET grade = ? WHERE id = ?", (grade, id))
    conn.commit()
    return jsonify({'message': 'Assignment graded successfully'})

# Root URL
@app.route('/')
def root():
    return 'Welcome to the Assignment Management System!'

# Start the server
if __name__ == '__main__':
    app.run(debug=True)
