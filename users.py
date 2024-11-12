from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import abort, request, session
import os
from sqlalchemy.sql import text

def register(username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password, role) VALUES (:username, :password, :role) ")
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
    except:
        return False
    return True

def login(username, password):
    sql = text("SELECT id, username, password, role FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if user is None or not check_password_hash(user[2], password):
        return False
    
    return {"id": user[0], "username": user[1], "role": user[3]}

def logout():
    del session["user_id"]
    del session["user_name"]
    del session["user_role"]

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)


def check_role(role):
    if role != session.get("user_role"):
        abort(403)

def get_name():
    return session.get("user_name")
