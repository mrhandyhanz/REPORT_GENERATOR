from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import json
from datetime import datetime
import mimetypes

mimetypes.add_type('text/css', '.css')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'

REQUIRED_COLUMNS = ['NAME', 'REG NO', 'GRADE', 'COMMENT', 'ONLINE ASSESSMENT', 'PHYSICAL EXAM', 'TOTAL', 'SIGNATURE']

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/test-image")
def test_image():
    return '<img src="/static/icrp_logo.png">'

@app.route('/upload', methods=['POST'])
def upload():                                  # Fixed: was 'index' (duplicate name)
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        return jsonify({'error': 'Only Excel files (.xlsx, .xls) are supported'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)
        df.columns = [str(c).strip().upper() for c in df.columns]

        # Flexible column matching
        col_map = {}
        for required in REQUIRED_COLUMNS:
            for actual in df.columns:
                if required in actual or actual in required:
                    col_map[required] = actual
                    break

        missing = [c for c in REQUIRED_COLUMNS if c not in col_map]
        if missing:
            return jsonify({'error': f'Missing columns: {", ".join(missing)}. Found: {", ".join(df.columns.tolist())}'}), 400

        df = df.rename(columns={v: k for k, v in col_map.items()})
        df = df[REQUIRED_COLUMNS].dropna(subset=['NAME', 'REG NO'])

        students = []
        for _, row in df.iterrows():
            student = {
                'name': str(row['NAME']).strip(),
                'reg_no': str(row['REG NO']).strip(),
                'grade': str(row['GRADE']).strip(),
                'comment': str(row['COMMENT']).strip() if pd.notna(row['COMMENT']) else '',
                'online_assessment': float(row['ONLINE ASSESSMENT']) if pd.notna(row['ONLINE ASSESSMENT']) else 0,
                'physical_exam': float(row['PHYSICAL EXAM']) if pd.notna(row['PHYSICAL EXAM']) else 0,
                'total': float(row['TOTAL']) if pd.notna(row['TOTAL']) else 0,
                'signature': '/static/sign.png',
                'score': get_score(float(row['TOTAL']) if pd.notna(row['TOTAL']) else 0),
                'position': 0
            }
            students.append(student)

        # Rank students by total
        students.sort(key=lambda x: x['total'], reverse=True)
        for i, s in enumerate(students):
            s['position'] = i + 1

        school_name = request.form.get('school_name', 'Excellence Academy')
        term = request.form.get('term', 'Term 1')
        year = request.form.get('year', str(datetime.now().year))
        grade_level = students[0]['grade'] if students else 'N/A'

        return jsonify({
            'success': True,
            'students': students,
            'meta': {
                'school_name': school_name,
                'term': term,
                'year': year,
                'grade': grade_level,
                'total_students': len(students),
                'generated_at': datetime.now().strftime('%B %d, %Y')
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500


def get_score(total):
    if total >= 90: return ('A+', 'Distinction')
    if total >= 80: return ('A', 'Excellent')
    if total >= 70: return ('B', 'Very Good')
    if total >= 60: return ('C', 'Good')
    if total >= 50: return ('D', 'Average')
    return ('F', 'Below Average')

@app.route('/report')
def report_page():
    return render_template('report.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
