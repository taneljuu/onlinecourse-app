from sqlalchemy.sql import text
from app import app
from db import db
from collections import defaultdict
import random

def get_tasks(course_id):
    sql = text("SELECT id, topic, created_at FROM mc_tasks WHERE course_id = :course_id AND visible = TRUE ORDER BY created_at")
    result = db.session.execute(sql, {"course_id": course_id})
    return result.fetchall()

def create_mc_task(topic, course_id):
    sql = text("INSERT INTO mc_tasks (course_id, topic, created_at, visible) VALUES (:course_id, :topic, NOW(), TRUE) RETURNING id")
    result = db.session.execute(sql, {"course_id":course_id, "topic":topic})
    task_id = result.fetchone()[0]
    return task_id

def delete_mc_task(task_id):
    sql = text("UPDATE mc_tasks SET visible = FALSE WHERE id = :task_id")
    db.session.execute(sql, {"task_id": task_id})
    db.session.commit()

def add_choices(task_id, correct_choice, choices):
    sql = text("INSERT INTO choices (task_id, choice, correct) VALUES (:task_id, :choice, TRUE)")
    db.session.execute(sql, {"task_id":task_id, "choice":correct_choice})
    db.session.commit()

    for choice in choices:
        if choice != "":
            sql = text("INSERT INTO choices (task_id, choice) VALUES (:task_id, :choice)")
            db.session.execute(sql, {"task_id":task_id, "choice":choice})
    db.session.commit()

def get_tasks_and_choices(course_id):
    sql = text("SELECT mc_tasks.id AS task_id, mc_tasks.topic AS topic, choices.id AS choice_id, choices.choice AS choice, choices.correct AS correct " \
               "FROM mc_tasks " \
               "JOIN choices ON mc_tasks.id = choices.task_id " \
               "WHERE mc_tasks.course_id = :course_id AND mc_tasks.visible = TRUE " \
               "ORDER BY mc_tasks.id, choices.id;")
    result = db.session.execute(sql, {"course_id": course_id}).mappings().fetchall()

    tasks = defaultdict(lambda: {"topic": "", "choices": []})
    for row in result:
        task_id = row["task_id"]
        if tasks[task_id]["topic"] == "":
            tasks[task_id]["topic"] = row["topic"]
        tasks[task_id]["choices"].append({
            "choice_id": row["choice_id"],
            "choice": row["choice"],
            "correct": row["correct"]
        })
    return tasks

def get_task_with_choices(task_id):
    int(task_id)  
    sql = text("""
        SELECT mc_tasks.id AS task_id, mc_tasks.topic AS topic, 
               choices.id AS choice_id, choices.choice AS choice, choices.correct AS correct
        FROM mc_tasks
        JOIN choices ON mc_tasks.id = choices.task_id
        WHERE mc_tasks.id = :task_id
    """)
    result = db.session.execute(sql, {"task_id": task_id}).fetchall()

    # return the task details and choices
    task = {
        "task_id": result[0][0],  # task_id
        "topic": result[0][1],    # topic
        "choices": [{"choice_id": row[2], "choice": row[3], "correct": row[4]} for row in result]
    }
    return task

def update_mc_task(task_id, topic, correct_choice, choices):
    # Update the topic of the question
    sql_task = text("UPDATE mc_tasks SET topic = :topic WHERE id = :task_id")
    db.session.execute(sql_task, {"topic": topic, "task_id": task_id})

    # Update the choices
    update_choices(task_id, correct_choice, choices)
    db.session.commit()

def update_choices(task_id, correct_choice, choices):
    # Delete old choices
    sql_delete = text("DELETE FROM choices WHERE task_id = :task_id")
    db.session.execute(sql_delete, {"task_id": task_id})

    # Add new choices
    add_choices(task_id, correct_choice, choices)

def is_correct(choice_id, student_id, task_id, course_id):
    # Check if the selected choice is correct
    sql = text("SELECT correct FROM choices WHERE id = :choice_id")
    result = db.session.execute(sql, {"choice_id": choice_id}).fetchone()
    if result:
        if result[0] == True:
            print(task_id)
            add_completed_task(student_id, task_id, course_id)
        return result[0]  # Return True/False based on whether the answer is correct
    return False  # If no result, return False (incorrect answer)

def add_completed_task(student_id, task_id, course_id):
    sql = text("INSERT INTO completed_tasks (student_id, task_id, course_id) VALUES (:student_id, :task_id, :course_id) ON CONFLICT (student_id, task_id) DO NOTHING")
    db.session.execute(sql, {"student_id": student_id, "task_id": task_id, "course_id": course_id})
    db.session.commit()