from sqlalchemy.sql import text
from flask import render_template, request, redirect, session
from app import app
from db import db

def get_available_courses(user_id): 
    sql = text("SELECT courses.id AS course_id, courses.name AS course_name, courses.info AS course_info, users.username AS teacher_name, courses.teacher_id AS teacher_id " \
                "FROM courses LEFT JOIN users ON courses.teacher_id=users.id " \
                "WHERE courses.visible=TRUE AND courses.id NOT IN (SELECT course_id FROM course_enrollments WHERE student_id = :user_id) " \
                "ORDER BY teacher_id")
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses

def join_course(course_id, user_id):
    sql = text("INSERT INTO course_enrollments (course_id, student_id) VALUES (:course_id, :user_id);")
    db.session.execute(sql, {
        "course_id": course_id,
        "user_id": user_id,
    })
    db.session.commit()

def get_own_courses(user_id):
    sql = text("SELECT course_enrollments.course_id AS course_id, courses.name AS name " \
               "FROM course_enrollments " \
                "LEFT JOIN courses ON course_enrollments.course_id=courses.id " \
                "WHERE student_id=:user_id")
    result = db.session.execute(sql, {"user_id": user_id})
    courses = result.fetchall()
    return courses

def get_course_name(course_id):
    sql = text("SELECT name FROM courses WHERE id=:course_id")
    result = db.session.execute(sql, {"course_id": course_id})
    name = result.fetchone()
    return name[0]