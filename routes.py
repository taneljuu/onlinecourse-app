from flask import render_template, request, redirect, url_for, session, abort
from app import app
import users
import teachers
import students
import text_content
import os


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.login(username, password)  
        if not user:
            return render_template("error.html", errors=["Kirjautuminen ei onnistunut"])

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["csrf_token"] = os.urandom(16).hex()

        if user["role"] == 1:
            return redirect(url_for("student"))
        elif user["role"] == 2:
            return redirect(url_for("teacher"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        role = request.form.get("choice")
        
        errors = []
        if len(username) < 3 or len(username) > 20:
            errors.append("Käyttäjätunnuksen pituuden on oltava 3-20 merkkiä")
        if password != password2:
            errors.append("Antamasi salasanat eroavat")
        if len(password) < 6:
            errors.append("Salasanan pituuden on oltava vähintään 6 merkkiä")
        if len(errors) > 0:
            return render_template("error.html", errors=errors)
        if not users.register(username, password, role):
            return render_template("error.html", errors=["Rekisteröinti ei onnistunut, kokeile toista käyttäjätunnusta"])
    return redirect("/")

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    del session["role"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/student")
def student():
    if session.get("role") != 1:
        abort(403)
    courses = students.get_available_courses()
    return render_template("student.html", username=session.get("username"), courses=courses)

@app.route("/teacher")
def teacher():
    if session.get("role") != 2:
        abort(403)
    courses = teachers.show_courses(session["user_id"])
    return render_template("teacher.html", username=session.get("username"), courses=courses)

@app.route("/teacher/create_course", methods=["GET","POST"])
def create_course():
    if session.get("role") != 2:
        abort(403)
    
    if request.method == "POST":
        name = request.form.get("course_name")
        info = request.form.get("info")
        
        if not teachers.create_new_course(name, info, session["user_id"]):
            return render_template("error.html", errors=["Kurssin luominen ei onnistunut, kokeile toista nimeä"])
        
        return redirect(url_for("teacher"))

    return render_template("create_course.html")

@app.route("/teacher/create_content/<int:course_id>", methods=["GET"])
def create_content(course_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)
    
    course = teachers.get_course(course_id)
    sections = text_content.get_text_sections(course_id)
    
    if not course:
        abort(404)  # Palautetaan 404, jos kurssia ei löydy

    return render_template("create_content.html", name=course["name"], sections=sections, course_id=course_id, )

@app.route("/teacher/edit_content/<int:course_id>/<int:section_id>", methods=["GET", "POST"])
def edit_content(course_id, section_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    course = teachers.get_course(course_id)
    course_name = course["name"] if course else "Kurssi"

    if request.args.get("delete") == "true":
        text_content.delete_section(section_id)
        return redirect(url_for("create_content", course_id=course_id))

    if request.method == "POST":
        title = request.form.get("section_title")
        content = request.form.get("text_content")
        if section_id == 0:  # Jos section_id on 0, luodaan uusi kappale
            text_content.create_section(course_id, title, content)
        else:
            text_content.update_section(section_id, title, content)
        return redirect(url_for("create_content", course_id=course_id))
    
    section = None
    if section_id != 0:
        section = text_content.get_section(section_id)
    return render_template("edit_content.html", course_id=course_id, section=section, course_name=course_name)



   
