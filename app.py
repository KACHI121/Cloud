import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, or_
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent
db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"
    __table_args__ = (CheckConstraint("year BETWEEN 1 AND 6", name="valid_year"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    course = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


def database_uri(value):
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


def create_app(database_url=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri(
        database_url or os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'students.db'}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        search = request.args.get("search", "").strip()
        query = db.select(Student)
        if search:
            term = f"%{search}%"
            query = query.where(or_(Student.name.ilike(term), Student.email.ilike(term), Student.course.ilike(term)))
        students = db.session.execute(query.order_by(Student.id.desc())).scalars().all()
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
                    db.session.add(Student(**data))
                    db.session.commit()
                    flash("Student added successfully.", "success")
                    return redirect(url_for("index"))
                except IntegrityError:
                    db.session.rollback()
                    flash("That email address is already registered.", "error")
        return render_template("student_form.html", student=None, form_title="Add student")

    @app.route("/students/<int:student_id>/edit", methods=("GET", "POST"))
    def edit_student(student_id):
        student = db.get_or_404(Student, student_id)
        if request.method == "POST":
            data = student_form_data()
            error = validate_student(data)
            if error:
                flash(error, "error")
            else:
                try:
                    for key, value in data.items():
                        setattr(student, key, value)
                    db.session.commit()
                    flash("Student updated successfully.", "success")
                    return redirect(url_for("index"))
                except IntegrityError:
                    db.session.rollback()
                    flash("That email address is already registered.", "error")
            student = data
        return render_template("student_form.html", student=student, form_title="Edit student")

    @app.post("/students/<int:student_id>/delete")
    def delete_student(student_id):
        student = db.get_or_404(Student, student_id)
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted.", "success")
        return redirect(url_for("index"))

    @app.get("/health")
    def health():
        db.session.execute(db.select(1)).scalar()
        return "ok", 200

    return app


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


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
