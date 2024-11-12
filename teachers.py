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
    sql = text("SELECT id, name, info FROM courses WHERE teacher_id=:user_id")
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses

def get_course(course_id):
    sql = text("SELECT id, name, info, teacher_id FROM courses WHERE id = :course_id")
    result = db.session.execute(sql, {"course_id": course_id})
    course = result.fetchone()
    
    if course:
        # Palauta sanakirja paremman selkeyden vuoksi
        return {"id": course[0], "name": course[1], "info": course[2], "teacher_id": course[3]}
    return None

def create_content(course_id):
    sql = text("SELECT name FROM courses WHERE id=:course_id")
    result = db.session.execute(sql, {"user_id": course_id})
    name = result.fetchone()
    return name