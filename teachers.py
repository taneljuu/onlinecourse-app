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













def create_content(course_id):
    sql = text("SELECT name FROM courses WHERE id=:course_id")
    result = db.session.execute(sql, {"user_id": course_id})
    name = result.fetchone()
    return name