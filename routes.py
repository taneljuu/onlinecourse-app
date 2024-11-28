from flask import render_template, request, redirect, url_for, session, abort
from app import app
import random
import users
import teachers
import students
import text_content
import tasks
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
    courses = students.get_available_courses(session["user_id"])
    own_courses = students.get_own_courses(session["user_id"])
    return render_template("student.html", username=session.get("username"), courses=courses, own_courses=own_courses)

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
    all_tasks = tasks.get_tasks(course_id)
    
    if not course:
        abort(404)  

    return render_template("create_content.html", name=course["name"], sections=sections, tasks=all_tasks, course_id=course_id, )

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
        if section_id == 0:  # if section_id == 0, create new section
            text_content.create_section(course_id, title, content)
        else:
            text_content.update_section(section_id, title, content)
        return redirect(url_for("create_content", course_id=course_id))
    
    section = None
    if section_id != 0:
        section = text_content.get_section(section_id)
    return render_template("edit_content.html", course_id=course_id, section=section, course_name=course_name)

@app.route("/teacher/delete_section/<int:course_id>/<int:section_id>", methods=["POST"])
def delete_section(course_id, section_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)
    
    success = text_content.delete_section(section_id)
    
    return redirect(url_for("create_content", course_id=course_id))

@app.route("/teacher/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)
    
    teachers.delete_course(course_id)
    
    return redirect(url_for("teacher"))

"""@app.route("/teacher/create_mc_task/<int:course_id>", methods=["GET", "POST"])
def create_mc_task(course_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    if request.method == "POST":
        topic = request.form["topic"]
        correct_choice = request.form["correct"]
        choices = request.form.getlist("choice")
        task_id = tasks.create_mc_task(topic, course_id) 
        tasks.add_choices(task_id, correct_choice, choices)
        return redirect(url_for("create_content", course_id=course_id))

    return render_template("create_mc_task.html", course_id=course_id)"""

@app.route("/teacher/create_mc_task/<int:course_id>", defaults={"task_id": None}, methods=["GET", "POST"])
@app.route("/teacher/create_mc_task/<int:course_id>/<int:task_id>", methods=["GET", "POST"])
def create_mc_task(course_id, task_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    if request.method == "POST":
        topic = request.form["topic"]
        correct_choice = request.form["correct"]
        choices = request.form.getlist("choice")

        if task_id:  # Muokkaus
            tasks.update_mc_task(task_id, topic, correct_choice, choices)
        else:  # Uusi tehtävä
            task_id = tasks.create_mc_task(topic, course_id)
            tasks.add_choices(task_id, correct_choice, choices)

        return redirect(url_for("create_content", course_id=course_id))

    # GET-pyyntö, tarkista onko kyseessä muokkaus
    task_data = tasks.get_task_with_choices(task_id) if task_id else None

    return render_template("create_mc_task.html", course_id=course_id, task=task_data)



@app.route("/teacher/delete_mc_task/<int:course_id>/<int:task_id>", methods=["POST"])
def delete_mc_task(course_id, task_id):
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    tasks.delete_mc_task(task_id)
    # Redirect back to the content creation page
    return redirect(url_for("create_content", course_id=course_id))

@app.route("/student/course_info/<int:course_id>", methods=["GET"])
def course_info(course_id):
    """if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)"""
    
    course = teachers.get_course(course_id)
    sections = text_content.get_text_sections(course_id)
    
    if not course:
        abort(404)  

    return render_template("course_info.html", course=course, sections=sections)

@app.route("/join_course", methods=["POST"])
def join_course():
    course_id = request.form.get("course_id")
    user_id = session.get("user_id")
    students.join_course(course_id, user_id)    
    return redirect(url_for("student"))

@app.route("/student/course_area/<int:course_id>", methods=["GET"])
def course_area(course_id):
    sections = text_content.get_text_sections(course_id)
    processed_sections = []
    for section in sections:
        # Ota id, section_number ja title normaalisti
        section_id = section[0]
        section_number = section[1]
        title = section[2]
        
        # Pilko sisältö rivinvaihtojen kohdalta
        normalized_content = section[3].replace("\r\n", "\n").replace("\r", "\n")
        content_lines = normalized_content.split("\n")
        
        # Lisää käsitelty osio listaan
        processed_sections.append({
            "id": section_id,
            "number": section_number,
            "title": title,
            "content_lines": content_lines
        })
    tasks_and_choices = tasks.get_tasks_and_choices(course_id)
    for task in tasks_and_choices.values():
        random.shuffle(task["choices"])

    return render_template("course_area.html", sections=processed_sections, tasks=tasks_and_choices, course_id=course_id)

@app.route("/submit_answers", methods=["POST"])
def submit_answers():
    if session.get("role") not in [1, 2]:  
        abort(403)

    # Determine which button submitted the data
    task_id = None
    for key in request.form.keys():
        print(key)
        if key.startswith("submit_"):  # Find the submit button, e.g., submit_3
            task_id = key.split("_")[1]  # Extract the numeric part, e.g., "3"
            print(task_id)
            break

    if not task_id:
        return "Task not found", 400

    # Retrieve the selected option
    choice_id = request.form.get(f"task_{task_id}")
    if not choice_id:
        return "No choice selected", 400

    user_id = session.get("user_id")
    course_id = request.form.get("course_id")
    is_correct = tasks.is_correct(choice_id, user_id, task_id, course_id)

    # Fetch the task details
    task = tasks.get_task_with_choices(task_id)

    # Find the selected answer option
    selected_choice = next((choice for choice in task["choices"] if choice["choice_id"] == int(choice_id)), None)
    if not selected_choice:
        return "Selected option is not valid", 400

    # Create feedback and return it to the user
    return render_template(
        "answer_feedback.html",
        task=task,
        is_correct=is_correct,
        selected_choice=selected_choice,
        course_id=request.form.get("course_id"),
    )







   
