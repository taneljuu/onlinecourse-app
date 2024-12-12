from sqlalchemy.sql import text
from flask import render_template, request, redirect, session
from app import app
from db import db


def create_new_course(name, info, teacher_id):
    try:
        sql = text("INSERT INTO courses (name, info, teacher_id, visible) VALUES (:name, :info, :teacher_id, TRUE)")
        db.session.execute(sql, {
            "name": name,
            "info": info,
            "teacher_id": teacher_id
        })
        db.session.commit()
    except:
        return False
    return True

def show_courses(user_id):
    sql = text("SELECT id, name, info FROM courses WHERE teacher_id=:user_id AND visible=TRUE")
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses

def get_course(course_id):
    sql = text("SELECT courses.id AS course_id, courses.name AS name, courses.info AS info, courses.teacher_id AS teacher_id, users.username AS teacher_name  FROM courses LEFT JOIN users ON courses.teacher_id = users.id WHERE courses.id = :course_id")
    result = db.session.execute(sql, {"course_id": course_id})
    course = result.fetchone()
    
    if course:
        # return dict
        return {"id": course[0], "name": course[1], "info": course[2], "teacher_id": course[3], "teacher_name": course[4]}
    return None

def delete_course(course_id):
    sql = text("""
        UPDATE courses 
        SET name = 'DELETED_' || id, visible = FALSE 
        WHERE id = :course_id
    """)
    db.session.execute(sql, {"course_id": course_id})
    db.session.commit()

def get_course_participants(course_id):
    sql = text("""
        SELECT 
            u.id AS student_id,
            u.username AS student_name,
            t.task_type,
            t.task_id,
            t.topic,
            CASE WHEN ct.student_id IS NOT NULL THEN TRUE ELSE FALSE END AS completed, ct.completion_time
        FROM 
            users u
        JOIN 
            course_enrollments ce ON u.id = ce.student_id
        LEFT JOIN (
            SELECT 
                mc.id AS task_id, 
                'mc' AS task_type, 
                mc.topic
            FROM 
                mc_tasks mc
            WHERE 
                mc.course_id = :course_id AND mc.visible = TRUE
            
            UNION ALL
            
            SELECT 
                ot.id AS task_id, 
                'open' AS task_type, 
                ot.topic
            FROM 
                open_tasks ot
            WHERE 
                ot.course_id = :course_id AND ot.visible = TRUE
        ) t ON TRUE -- Yhdistetään kaikki näkyvät tehtävät jokaiseen opiskelijaan
        LEFT JOIN 
            completed_tasks ct ON t.task_id = ct.task_id 
                AND ct.task_type = t.task_type 
                AND ct.student_id = u.id
                AND ct.course_id = :course_id
        WHERE 
            ce.course_id = :course_id
        ORDER BY 
            u.username, t.task_type, t.task_id;
    """)
    result = db.session.execute(sql, {"course_id": course_id})

    student_tasks = {}
    for row in result:
        student_name = row[1]
        task_info = {
            "task_type": row[2],
            "task_id": row[3],
            "topic": row[4],
            "completed": row[5],
            "completion_time": row[6]
        }
        if student_name not in student_tasks:
            student_tasks[student_name] = []
        student_tasks[student_name].append(task_info)

    return student_tasks


def create_content(course_id):
    sql = text("SELECT name FROM courses WHERE id=:course_id")
    result = db.session.execute(sql, {"user_id": course_id})
    name = result.fetchone()
    return name