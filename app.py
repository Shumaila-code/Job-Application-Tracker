
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

ALLOWED_STATUSES = ["Applied", "Interview", "Offer", "Rejected"]


# HOME PAGE + SEARCH + FILTER + STATISTICS
@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")

    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Search and filter applications
    query = "SELECT * FROM jobs WHERE 1=1"
    parameters = []

    if search:
        query += " AND company LIKE ?"
        parameters.append(f"%{search}%")

    if status in ALLOWED_STATUSES:
        query += " AND status = ?"
        parameters.append(status)

    query += " ORDER BY id DESC"

    cursor.execute(query, parameters)
    jobs = cursor.fetchall()

    # Dashboard statistics
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = ?",
        ("Interview",)
    )
    interviews = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = ?",
        ("Offer",)
    )
    offers = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = ?",
        ("Rejected",)
    )
    rejected = cursor.fetchone()[0]

    # FOLLOW-UP REMINDER STATISTICS
    today = date.today().isoformat()

    # Follow-ups due today
    cursor.execute(
        """
        SELECT COUNT(*) FROM jobs
        WHERE follow_up_date = ?
        AND status NOT IN ('Offer', 'Rejected')
        """,
        (today,)
    )
    due_today = cursor.fetchone()[0]

    # Overdue follow-ups
    cursor.execute(
        """
        SELECT COUNT(*) FROM jobs
        WHERE follow_up_date < ?
        AND follow_up_date IS NOT NULL
        AND follow_up_date != ''
        AND status NOT IN ('Offer', 'Rejected')
        """,
        (today,)
    )
    overdue = cursor.fetchone()[0]

    # Upcoming follow-ups
    cursor.execute(
        """
        SELECT COUNT(*) FROM jobs
        WHERE follow_up_date > ?
        AND status NOT IN ('Offer', 'Rejected')
        """,
        (today,)
    )
    upcoming = cursor.fetchone()[0]

    # FOLLOW-UP ALERTS TABLE
    cursor.execute(
        """
        SELECT id, company, title, status, follow_up_date
        FROM jobs
        WHERE follow_up_date IS NOT NULL
        AND follow_up_date != ''
        AND follow_up_date <= ?
        AND status NOT IN ('Offer', 'Rejected')
        ORDER BY follow_up_date ASC
        """,
        (today,)
    )

    follow_up_alerts = cursor.fetchall()

    print("Follow-up alerts found:", len(follow_up_alerts))

    connection.close()

    return render_template(
        "index.html",
        jobs=jobs,
        search=search,
        selected_status=status,
        total_jobs=total_jobs,
        interviews=interviews,
        offers=offers,
        rejected=rejected,
        due_today=due_today,
        overdue=overdue,
        upcoming=upcoming,
        follow_up_alerts=follow_up_alerts,
        today=today
    )


# ADD NEW JOB
@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":

        company = request.form.get("company", "").strip()
        title = request.form.get("title", "").strip()
        status = request.form.get("status", "Applied")

        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip()
        application_date = request.form.get(
            "application_date", ""
        ).strip()
        job_url = request.form.get("job_url", "").strip()
        notes = request.form.get("notes", "").strip()
        follow_up_date = request.form.get(
            "follow_up_date", ""
        ).strip()

        if not company or not title:
            return "Company and job title are required.", 400

        if status not in ALLOWED_STATUSES:
            return "Invalid application status.", 400

        connection = sqlite3.connect("jobs.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO jobs (
                company,
                title,
                status,
                location,
                salary,
                application_date,
                job_url,
                notes,
                follow_up_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                title,
                status,
                location,
                salary,
                application_date or None,
                job_url,
                notes,
                follow_up_date or None
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    return render_template("add_job.html")


# DELETE JOB
@app.route("/delete-job/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM jobs WHERE id = ?",
        (job_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


# EDIT JOB
@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    )
    job = cursor.fetchone()

    if job is None:
        connection.close()
        return "Job not found", 404

    if request.method == "POST":

        company = request.form.get("company", "").strip()
        title = request.form.get("title", "").strip()
        status = request.form.get("status", "Applied")

        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip()
        application_date = request.form.get(
            "application_date", ""
        ).strip()
        job_url = request.form.get("job_url", "").strip()
        notes = request.form.get("notes", "").strip()
        follow_up_date = request.form.get(
            "follow_up_date", ""
        ).strip()

        if not company or not title:
            connection.close()
            return "Company and job title are required.", 400

        if status not in ALLOWED_STATUSES:
            connection.close()
            return "Invalid application status.", 400

        cursor.execute(
            """
            UPDATE jobs
            SET company = ?,
                title = ?,
                status = ?,
                location = ?,
                salary = ?,
                application_date = ?,
                job_url = ?,
                notes = ?,
                follow_up_date = ?
            WHERE id = ?
            """,
            (
                company,
                title,
                status,
                location,
                salary,
                application_date or None,
                job_url,
                notes,
                follow_up_date or None,
                job_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    connection.close()

    return render_template("edit_job.html", job=job)


# VIEW JOB DETAILS
@app.route("/job/<int:job_id>")
def job_details(job_id):
    connection = sqlite3.connect("jobs.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    )

    job = cursor.fetchone()
    connection.close()

    if job is None:
        return "Job not found", 404

    return render_template("job_details.html", job=job)


if __name__ == "__main__":
    app.run(debug=True)
