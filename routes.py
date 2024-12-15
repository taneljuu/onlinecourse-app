from flask import render_template, request, redirect, url_for, session, abort
from app import app
import random
import users
import teachers
import students
import text_content
import tasks
import os


def verify_csrf_token():
    """
    Validate the CSRF token to protect against cross-site request forgery.
    Abort the request with a 403 status if the token is invalid.
    """
    if session["csrf_token"] != request.form.get("csrf_token"):
        abort(403)


@app.route("/")
def index():
    """
    Render the index page.
    """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login, generate a new CSRF token, and redirect based on user role.
    """
    if request.method == "GET":
        session["csrf_token"] = os.urandom(16).hex()
        return render_template("login.html", csrf_token=session["csrf_token"])

    if request.method == "POST":
        verify_csrf_token()

        username = request.form.get("username")
        password = request.form.get("password")

        user = users.login(username, password)
        if not user:
            return render_template("error.html", errors=["Login failed"])

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
    """
    Handle user registration, validate inputs, and create a new user.
    """
    if request.method == "GET":
        session["csrf_token"] = os.urandom(16).hex()
        return render_template("register.html", csrf_token=session["csrf_token"])

    if request.method == "POST":
        verify_csrf_token()

        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        role = request.form.get("choice")

        errors = users.check_username_and_password(username, password, password2)
        if errors:
            return render_template("error.html", errors=errors)

        if not users.register(username, password, role):
            return render_template("error.html", errors=["Registration failed, try another username"])

        return redirect("/")

@app.route('/logout', methods=["GET"])
def logout():
    del session["user_id"]
    del session["username"]
    del session["role"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/student")
def student():
    """
    Render the student dashboard with available and enrolled courses.
    """
    if session.get("role") != 1:
        abort(403)

    courses = students.get_available_courses(session["user_id"])
    own_courses = students.get_own_courses(session["user_id"])
    return render_template("student.html", username=session.get("username"), courses=courses, own_courses=own_courses)


@app.route("/teacher")
def teacher():
    """
    Render the teacher dashboard with their courses.
    """
    if session.get("role") != 2:
        abort(403)

    courses = teachers.show_courses(session["user_id"])
    return render_template("teacher.html", username=session.get("username"), courses=courses)


@app.route("/teacher/create_course", methods=["GET", "POST"])
def create_course():
    """
    Allow teachers to create a new course.
    """
    if session.get("role") != 2:
        abort(403)

    if request.method == "POST":
        verify_csrf_token()

        name = request.form.get("course_name")
        info = request.form.get("info")

        if not teachers.create_new_course(name, info, session["user_id"]):
            return render_template("error.html", errors=["Course creation failed, try another name"])

        return redirect(url_for("teacher"))

    return render_template("create_course.html")


@app.route("/teacher/create_content/<int:course_id>", methods=["GET"])
def create_content(course_id):
    """
    Render the content creation page for a specific course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    course = teachers.get_course(course_id)
    sections = text_content.get_text_sections(course_id)
    mc_tasks = tasks.get_tasks(course_id)
    open_tasks = tasks.get_open_tasks(course_id)

    completed_mcs = tasks.completed_mcs(session.get("user_id"), course_id)
    completed_opens = tasks.completed_opens(session.get("user_id"), course_id)
    participants = teachers.get_course_participants(course_id)

    if not course:
        abort(404)

    return render_template(
        "create_content.html",
        name=course["name"],
        sections=sections,
        tasks=mc_tasks,
        open_tasks=open_tasks,
        course_id=course_id,
        participants=participants,
        completed_mcs=completed_mcs,
        completed_opens=completed_opens
    )


@app.route("/teacher/create_content/participants/<int:course_id>", methods=["GET"])
def participants(course_id):
    """
    Render the participants list for a specific course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    participants = teachers.get_course_participants(course_id)
    course = teachers.get_course(course_id)

    return render_template("participants.html", course_name=course["name"], course_id=course_id, participants=participants)


@app.route("/teacher/edit_content/<int:course_id>/<int:section_id>", methods=["GET", "POST"])
def edit_content(course_id, section_id):
    """
    Allow teachers to create or edit a course section.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    course = teachers.get_course(course_id)
    course_name = course["name"] if course else "Course"

    if request.args.get("delete") == "true":
        text_content.delete_section(section_id)
        return redirect(url_for("create_content", course_id=course_id))

    if request.method == "POST":
        verify_csrf_token()

        title = request.form.get("section_title")
        content = request.form.get("text_content")

        if section_id == 0:
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
    """
    Allow teachers to delete a course section.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    verify_csrf_token()
    text_content.delete_section(section_id)
    return redirect(url_for("create_content", course_id=course_id))


@app.route("/teacher/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    """
    Allow teachers to delete a course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    verify_csrf_token()
    teachers.delete_course(course_id)
    return redirect(url_for("teacher"))


@app.route("/teacher/create_mc_task/<int:course_id>", defaults={"task_id": None}, methods=["GET", "POST"])
@app.route("/teacher/create_mc_task/<int:course_id>/<int:task_id>", methods=["GET", "POST"])
def create_mc_task(course_id, task_id):
    """
    Allow teachers to create or edit a multiple-choice task for a course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    if request.method == "POST":
        verify_csrf_token()

        topic = request.form["topic"]
        correct_choice = request.form["correct"]
        choices = request.form.getlist("choice")

        if task_id:
            tasks.update_mc_task(task_id, topic, correct_choice, choices)  # Update existing task.
        else:
            task_id = tasks.create_mc_task(topic, course_id)  # Create new task.
            tasks.add_choices(task_id, correct_choice, choices)

        return redirect(url_for("create_content", course_id=course_id))

    task_data = tasks.get_task_with_choices(task_id) if task_id else None  # Check if editing an existing task.

    return render_template("create_mc_task.html", course_id=course_id, task=task_data)


@app.route("/teacher/create_open_task/<int:course_id>", defaults={"task_id": None}, methods=["GET", "POST"])
@app.route("/teacher/create_open_task/<int:course_id>/<int:task_id>", methods=["GET", "POST"])
def create_open_task(course_id, task_id):
    """
    Allow teachers to create or edit an open-ended task for a course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    if request.method == "POST":
        verify_csrf_token()

        topic = request.form["topic"]
        answer = request.form["answer"]

        if task_id:
            tasks.update_open_task(task_id, topic, answer)  # Update existing task.
        else:
            tasks.create_open_task(topic, answer, course_id)  # Create new task.

        return redirect(url_for("create_content", course_id=course_id))

    task_data = tasks.get_open_task_data(task_id) if task_id else None  # Check if editing an existing task.

    return render_template("create_open_task.html", course_id=course_id, task=task_data)


@app.route("/teacher/delete_mc_task/<int:course_id>/<int:task_id>", methods=["POST"])
def delete_mc_task(course_id, task_id):
    """
    Allow teachers to delete a multiple-choice task from a course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    verify_csrf_token()
    tasks.delete_mc_task(task_id)

    return redirect(url_for("create_content", course_id=course_id))


@app.route("/teacher/delete_open_task/<int:course_id>/<int:task_id>", methods=["POST"])
def delete_open_task(course_id, task_id):
    """
    Allow teachers to delete an open-ended task from a course.
    """
    if session.get("role") != 2 or teachers.get_course(course_id)["teacher_id"] != session.get("user_id"):
        abort(403)

    verify_csrf_token()
    tasks.delete_open_task(task_id)

    return redirect(url_for("create_content", course_id=course_id))


@app.route("/student/course_info/<int:course_id>", methods=["GET"])
def course_info(course_id):
    """
    Allow students to view course information before joining the course.
    """
    if session.get("role") != 1:
        abort(403)

    course = teachers.get_course(course_id)

    if not course:
        abort(404)

    return render_template("course_info.html", course=course)


@app.route("/join_course", methods=["POST"])
def join_course():
    """
    Allow students to join a course.
    """
    if session.get("role") != 1:
        abort(403)

    verify_csrf_token()

    course_id = request.form.get("course_id")
    user_id = session.get("user_id")
    students.join_course(course_id, user_id)

    return redirect(url_for("student"))


@app.route("/leave_course", methods=["POST"])
def leave_course():
    """
    Allow students to leave a course.
    """
    if session.get("role") != 1:
        abort(403)

    verify_csrf_token()

    course_id = request.form.get("course_id")
    user_id = session.get("user_id")
    students.leave_course(course_id, user_id)

    return redirect(url_for("student"))


@app.route("/student/course_area/<int:course_id>", methods=["GET"])
def course_area(course_id):
    """
    Allow students to access the course area, including text sections and tasks.
    """
    if session.get("role") != 1:
        abort(403)

    course_name = students.get_course_name(course_id)
    sections = text_content.get_text_sections(course_id)

    processed_sections = []
    for section in sections:
        section_id = section[0]
        section_number = section[1]
        title = section[2]

        normalized_content = section[3].replace("\r\n", "\n").replace("\r", "\n")
        content_lines = normalized_content.split("\n")

        processed_sections.append({
            "id": section_id,
            "number": section_number,
            "title": title,
            "content_lines": content_lines
        })

    tasks_and_choices = tasks.get_tasks_and_choices(course_id)  # Fetch multiple-choice tasks.
    for task in tasks_and_choices.values():
        random.shuffle(task["choices"])

    open_tasks = tasks.get_open_tasks(course_id)  # Fetch open-ended tasks.

    completed_mcs = tasks.completed_mcs(session.get("user_id"), course_id)  # Completed multiple-choice tasks.
    completed_opens = tasks.completed_opens(session.get("user_id"), course_id)  # Completed open-ended tasks.

    return render_template(
        "course_area.html",
        sections=processed_sections,
        tasks=tasks_and_choices,
        open_tasks=open_tasks,
        completed_mcs=completed_mcs,
        completed_opens=completed_opens,
        course_id=course_id,
        course_name=course_name
    )


@app.route("/submit_answers", methods=["POST"])
def submit_answers():
    """
    Allow students to submit answers for multiple-choice tasks.
    """
    if session.get("role") != 1:
        abort(403)

    verify_csrf_token()

    task_id = None
    for key in request.form.keys():
        if key.startswith("submit_"):
            task_id = key.split("_")[1]  # Extract the task ID.
            break

    if not task_id:
        return "Task not found", 400

    choice_id = request.form.get(f"task_{task_id}")
    if not choice_id:
        return "No choice selected", 400

    user_id = session.get("user_id")
    course_id = request.form.get("course_id")
    is_correct = tasks.is_correct(choice_id, user_id, task_id, course_id, "mc")

    task = tasks.get_task_with_choices(task_id)  # Fetch task details.

    selected_choice = next((choice for choice in task["choices"] if choice["choice_id"] == int(choice_id)), None)
    if not selected_choice:
        return "Selected option is not valid", 400

    return render_template(
        "answer_feedback.html",
        task=task,
        is_correct=is_correct,
        selected_choice=selected_choice,
        course_id=request.form.get("course_id"),
        multichoice=True
    )


@app.route("/submit_open_tasks", methods=["POST"])
def submit_open_tasks():
    """
    Allow students to submit answers for open-ended tasks.
    """
    if session.get("role") != 1:
        abort(403)

    verify_csrf_token()

    task_id = None
    for key in request.form.keys():
        if key.startswith("open_"):
            task_id = key.split("_")[1]  # Extract the task ID.
            break

    if not task_id:
        return "Task not found", 400

    answer = request.form.get(f"answer_{task_id}")
    if not answer:
        return "No answer provided", 400

    user_id = session.get("user_id")
    course_id = request.form.get("course_id")
    is_correct = tasks.is_correct_open(answer.strip(), task_id, user_id, course_id, "open")

    task = tasks.get_open_task_data(task_id)  # Fetch task details.
    if not task:
        return "Task not found in database", 404

    return render_template(
        "answer_feedback.html",
        task=task,
        is_correct=is_correct,
        selected_choice=answer,
        course_id=request.form.get("course_id"),
        multichoice=False
    )
