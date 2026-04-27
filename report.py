from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import os
import gc
import shutil

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Limits uploads to 5MB

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "Error: No file part in the request."
            
        file = request.files["file"]
        if file.filename == "":
            return "Error: No selected file."
            
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                file.save(path)
                df = pd.read_excel(path)

                # CLEANUP: Delete old reports before making new ones
                if os.path.exists(REPORT_FOLDER):
                    shutil.rmtree(REPORT_FOLDER)
                os.makedirs(REPORT_FOLDER, exist_ok=True)

                for _, row in df.iterrows():
                    student_name = str(row.get("Name", "Unknown_Student"))
                    out_filename = student_name.replace(" ", "_") + ".html"
                    filepath = os.path.join(REPORT_FOLDER, out_filename)
                    
                    online = row.get('Online', 0)
                    physical = row.get('Physical', 0)
                    total = online + physical
                    
                    online_percent = f"{(online/50)*100:.1f}" if online else "0.0"
                    physical_percent = f"{(physical/50)*100:.1f}" if physical else "0.0"
                    
                    rendered_html = render_template(
                        "report.html",
                        name=student_name,
                        student_class=row.get('Class', 'Unknown'),
                        online=online,
                        online_percent=online_percent,
                        physical=physical,
                        physical_percent=physical_percent,
                        total=total,
                        comment=row.get('Comment', '')
                    )

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(rendered_html)

                # MEMORY MANAGEMENT: Clear data from RAM after processing
                del df
                gc.collect()

                return "HTML Reports Generated Successfully! <br><br> <a href='/dashboard' style='padding: 10px 20px; background: #1f4e79; color: white; text-decoration: none; border-radius: 5px;'>Go to Dashboard</a>"
            
            except Exception as e:
                return f"Error processing file: {str(e)}"

    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    reports = []
    if os.path.exists(REPORT_FOLDER):
        reports = [f for f in os.listdir(REPORT_FOLDER) if f.endswith('.html')]
    return render_template("dashboard.html", reports=reports)

@app.route("/reports/<filename>")
def serve_report(filename):
    return send_from_directory(REPORT_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
