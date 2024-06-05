

```markdown
# Assignment Management System API

This API allows users to manage assignments, submissions, and grades within an educational context. It provides endpoints for user registration, authentication, assignment creation, submission, grading, and more.

## Requirements

- Python 3.x
- Flask
- SQLite3
- PyJWT

## Installation


1. Navigate to the project directory:
   
   cd STUDENTS_ASSIGNMENTS
   

2. Install dependencies:
   
    pip install -r requirements.txt
   

3. Run the application:
   
   python app.py
   

## Usage

- Register a new user: `POST /register`
- Login to get JWT token: `POST /login`
- Create a new assignment: `POST /assignments`
- Get all assignments: `GET /assignments`
- Update an assignment: `PUT /assignments/<id>`
- Delete an assignment: `DELETE /assignments/<id>`
- Submit an assignment: `POST /assignments/<id>/submit`
- Grade an assignment: `PUT /assignments/<id>/grade`

## Testing

For testing the API endpoints, you can use tools like Postman or cURL. a Postman collection:

## Database

- SQL files for table creation: [create_tables.sql]

```


API Documentation : https://docs.google.com/document/d/1vzSJ9EKEC8yunzR0zaR_NY7bXhiIEGT3aB6f04cY4Yc/edit?usp=sharing

