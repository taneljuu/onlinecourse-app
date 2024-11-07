CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role INTEGER CHECK (role IN (1, 2)) 
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    info TEXT,
    teacher_id INTEGER REFERENCES users(id),
    visible BOOLEAN
);

CREATE TABLE course_enrollments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    student_id INTEGER REFERENCES users(id)
);