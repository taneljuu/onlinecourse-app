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

CREATE TABLE text_sections (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    section_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    visible BOOLEAN
);

CREATE TABLE mc_tasks (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    topic TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN 
);

CREATE TABLE choices (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES mc_tasks(id),
    choice TEXT NOT NULL,
    correct BOOLEAN DEFAULT FALSE
);

CREATE TABLE completed_tasks (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    task_id INTEGER NOT NULL REFERENCES mc_tasks(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    UNIQUE (student_id, task_id)
);
