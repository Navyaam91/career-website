from flask import Flask,render_template,request
from db_config import get_db_connection
app = Flask(__name__)

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




if __name__ == '__main__':
    app.run(debug=True)