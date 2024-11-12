from sqlalchemy.sql import text
from flask import render_template, request, redirect, session
from app import app
from db import db

def get_text_sections(course_id):
    sql = text("SELECT id, section_number, title FROM text_sections WHERE course_id = :course_id AND visible = TRUE ORDER BY section_number")
    result = db.session.execute(sql, {"course_id": course_id})
    return result.fetchall()

def create_section(course_id, title, content):
    sql = text("INSERT INTO text_sections (course_id, section_number, title, content, visible) VALUES (:course_id, (SELECT COALESCE(MAX(section_number), 0) + 1 FROM text_sections WHERE course_id=:course_id), :title, :content, :visible)")
    db.session.execute(sql, {"course_id": course_id, "title": title, "content": content, "visible": True})
    db.session.commit()

def get_section(section_id):
    sql = text("SELECT id, section_number, title, content FROM text_sections WHERE id=:section_id") 
    result = db.session.execute(sql, {"section_id": section_id})
    return result.fetchone()

def update_section(section_id, title, content):
    sql = text("UPDATE text_sections SET title=:title, content=:content WHERE id=:section_id")
    db.session.execute(sql, {"title": title, "content": content, "section_id": section_id})
    db.session.commit()

def delete_section(section_id):
    sql = text("UPDATE text_sections SET visible=FALSE WHERE id=:section_id")
    db.session.execute(sql, {"section_id": section_id})
    db.session.commit()