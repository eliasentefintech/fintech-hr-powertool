from flask import Flask, render_template, request, redirect, session
from db import get_connection

from config import BACKUP_DIRECTORY, BACKUP_FILE

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with get_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            ).fetchone()

        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        return "Login failed"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])

@app.route("/employees")
def employees():
    if "user" not in session:
        return redirect("/")

    with get_connection() as conn:
        employees = conn.execute("SELECT * FROM employees").fetchall()

    return render_template("employees.html", employees=employees)

@app.route("/employees/<int:employee_id>")
def employee_detail(employee_id):
    if "user" not in session:
        return redirect("/")

    with get_connection() as conn:
        employee = conn.execute(
            "SELECT * FROM employees WHERE id = ?",
            (employee_id,)
        ).fetchone()

    if not employee:
        return "Not found", 404

    return render_template("employee_detail.html", employee=employee)

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "Forbidden", 403

    return render_template(
        "admin.html",
        backup_directory=BACKUP_DIRECTORY,
        backup_file=BACKUP_FILE
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)