from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import get_db_connection
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/resumes'
app.secret_key = 'supersecret123'

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # cursor.execute("SELECT * FROM jobs WHERE is_featured = TRUE ORDER BY date_posted DESC LIMIT 6")
    cursor.execute("SELECT * FROM jobs left join company on jobs.company_id=company.company_id WHERE is_featured = TRUE ORDER BY date_posted DESC LIMIT 6")

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('index.html', jobs=jobs)

@app.route("/about")
def about():
    return render_template('about.html')
@app.route("/job-details/<int:job_id>")
def job_details(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs left join company on jobs.company_id=company.company_id WHERE id = %s", (job_id,))
    job = cursor.fetchone()

    cursor.close()
    conn.close()

    if job:
        return render_template('job-details.html', job=job)
    else:
        return "Job not found", 404

@app.route("/apply/<int:job_id>")
def apply(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # ✅ dictionary cursor
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("apply.html", job=job)

@app.route("/submit-application/<int:job_id>", methods=["POST"])
def submit_application(job_id):
    conn = get_db_connection()
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    resume = request.files['resume']

    if resume:
        filename = secure_filename(resume.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(filepath)

        # Optional: Save application info in DB
        cursor = conn.cursor()
        cursor.execute("INSERT INTO applications (job_id, name, email, mobile, resume_path) VALUES (%s, %s, %s, %s, %s)",
                       (job_id, name, email, mobile, filename))
        conn.commit()

        flash("Application submitted successfully!", "success")
        return redirect(url_for('apply', job_id=job_id))
    else:
        flash("Resume upload failed", "danger")
        return redirect(url_for('apply', job_id=job_id))



if __name__ == '__main__':
    app.run(debug=True)