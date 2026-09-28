import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "students.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = get_db()
    db.execute(
        """CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    db.commit()


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    query = "SELECT * FROM students"
    params = []
    if search:
        query += " WHERE name LIKE ? OR email LIKE ? OR course LIKE ?"
        value = f"%{search}%"
        params = [value, value, value]
    query += " ORDER BY id DESC"
    students = get_db().execute(query, params).fetchall()
    return render_template("index.html", students=students, search=search)


@app.route("/students/new", methods=("GET", "POST"))
def create_student():
    if request.method == "POST":
        data = student_form_data()
        error = validate_student(data)
        if error:
            flash(error, "error")
        else:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO students (name, email, course, year) VALUES (?, ?, ?, ?)",
                    (data["name"], data["email"], data["course"], data["year"]),
                )
                db.commit()
                flash("Student added successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("That email address is already registered.", "error")
    return render_template("student_form.html", student=None, form_title="Add student")


@app.route("/students/<int:student_id>/edit", methods=("GET", "POST"))
def edit_student(student_id):
    student = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if student is None:
        return "Student not found", 404
    if request.method == "POST":
        data = student_form_data()
        error = validate_student(data)
        if error:
            flash(error, "error")
        else:
            try:
                db = get_db()
                db.execute(
                    "UPDATE students SET name = ?, email = ?, course = ?, year = ? WHERE id = ?",
                    (data["name"], data["email"], data["course"], data["year"], student_id),
                )
                db.commit()
                flash("Student updated successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("That email address is already registered.", "error")
        student = {**dict(student), **data}
    return render_template("student_form.html", student=student, form_title="Edit student")


@app.post("/students/<int:student_id>/delete")
def delete_student(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("index"))


def student_form_data():
    return {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
        "course": request.form.get("course", "").strip(),
        "year": request.form.get("year", "").strip(),
    }


def validate_student(data):
    if not all((data["name"], data["email"], data["course"], data["year"])):
        return "Please complete all fields."
    if "@" not in data["email"]:
        return "Please enter a valid email address."
    try:
        year = int(data["year"])
    except ValueError:
        return "Year must be a number between 1 and 6."
    if not 1 <= year <= 6:
        return "Year must be a number between 1 and 6."
    data["year"] = year
    return None


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
