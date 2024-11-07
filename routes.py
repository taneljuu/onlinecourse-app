from flask import render_template, request, redirect, url_for, session, abort
from app import app
import users

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

        user = users.login(username, password)  # Login function handles session
        if not user:
            return render_template("error.html", errors=["Kirjautuminen ei onnistunut"])

        session["user_id"] = user["id"]
        session["user_name"] = user["username"]
        session["user_role"] = user["role"]

        if user["role"] == 1:
            return redirect(url_for("student"))
        elif user["role"] == 2:
            return redirect(url_for("teacher"))

@app.route("/register", methods=["get", "post"])
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
    users.logout()  # Clear session through the users module
    return redirect("/")

@app.route("/student")
def student():
    if session.get("user_role") != 1:
        abort(403)
    return render_template("student.html", username=session.get("user_name"))

@app.route("/teacher")
def teacher():
    if session.get("user_role") != 2:
        abort(403)
    return render_template("teacher.html", username=session.get("user_name"))

@app.route("/create_course", methods=["post"])
def create_course():
    return render_template("create_course.html")
