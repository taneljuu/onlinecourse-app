from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import abort, request, session
from sqlalchemy.sql import text
import string

def register(username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password, role) VALUES (:username, :password, :role) ")
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
    except:
        return False
    return True

def check_username_and_password(username, password, password2):
    errors = []
    if len(username) < 3 or len(username) > 20:
        errors.append("Käyttäjätunnuksen pituuden on oltava 3-20 merkkiä")
    if password != password2:
        errors.append("Antamasi salasanat eroavat")
    if len(password) < 6:
        errors.append("Salasanan pituuden on oltava vähintään 6 merkkiä")
    if not any(char.isalpha() for char in password):
        errors.append("Salasanan pitää sisältää kirjain")
    if not any(char.isdigit() for char in password):
        errors.append("Salasanan pitää sisältää numero")
    if not any(char in string.punctuation for char in password):
        errors.append("Salasanan pitää sisältää erikoismerkki")
    return errors

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
