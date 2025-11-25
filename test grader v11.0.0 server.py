from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)
DATABASE = 'grades_v11.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY,
            score REAL, letter_grade TEXT, gpa REAL,
            student_name TEXT, subject TEXT, timestamp DATETIME,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

GRADE_SCALE = {
    97: ("A+", "Outstanding!", 4.0), 93: ("A", "Excellent!", 4.0),
    90: ("A-", "Great job!", 3.7), 87: ("B+", "Very good!", 3.3),
    83: ("B", "Good work!", 3.0), 80: ("B-", "Decent job!", 2.7),
    77: ("C+", "Fair work!", 2.3), 73: ("C", "Average!", 2.0),
    70: ("C-", "Passing!", 1.7), 67: ("D+", "Below average!", 1.3),
    63: ("D", "Poor!", 1.0), 60: ("D-", "Critical!", 0.7), 0: ("F", "Failed!", 0.0)
}

def determine_grade(score):
    for threshold in sorted(GRADE_SCALE.keys(), reverse=True):
        if score >= threshold:
            return GRADE_SCALE[threshold]
    return ("F", "Failed!", 0.0)

def save_to_db(score, letter_grade, gpa, name, subject, feedback):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO grades (score, letter_grade, gpa, student_name, subject, timestamp, feedback)
        VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
    ''', (score, letter_grade, gpa, name, subject, feedback))
    conn.commit()
    conn.close()

HTML = '''<!DOCTYPE html><html><head><title>Test Grader v11.0.0 - Database</title><style>
body{font-family:Arial;max-width:600px;margin:50px auto;background:#f5f5f5}
.container{background:white;padding:30px;border-radius:8px;box-shadow:0 2px 10px}
h1{color:#4c3f91}input,button{padding:10px;margin:10px 0;width:100%;border:1px solid #ddd;border-radius:4px}
button{background:#4c3f91;color:white;cursor:pointer;border:none}button:hover{background:#3b2f70}
.result{margin-top:30px;padding:20px;background:#e8f4fd;border-radius:4px;display:none}.result.show{display:block}
.grade{font-size:36px;color:#4c3f91;font-weight:bold}</style></head><body>
<div class="container"><h1>📊 Test Grader v11.0.0 - Database Edition</h1>
<form id="f"><input type="text" id="n" placeholder="Student Name"/><input type="text" id="s" placeholder="Subject"/>
<input type="number" id="g" placeholder="Score (0-100)" min="0" max="100" required/><button type="submit">Grade</button></form>
<div id="r" class="result"><div class="grade" id="l"></div><p>Score: <span id="sc"></span>/100</p>
<p>GPA: <span id="gp"></span>/4.0</p><p>Feedback: <span id="fb"></span></p></div></div>
<script>
document.getElementById('f').addEventListener('submit', async (e) => {
    e.preventDefault();
    const response = await fetch('/api/grade', {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({score: parseFloat(document.getElementById('g').value), name: document.getElementById('n').value, subject: document.getElementById('s').value})});
    const data = await response.json();
    document.getElementById('l').textContent = data.letter_grade;
    document.getElementById('sc').textContent = data.score;
    document.getElementById('gp').textContent = data.gpa.toFixed(2);
    document.getElementById('fb').textContent = data.feedback;
    document.getElementById('r').classList.add('show');
});
</script></body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/grade', methods=['POST'])
def grade():
    data = request.json
    score = float(data.get('score', 0))
    name = data.get('name', '')
    subject = data.get('subject', '')
    letter_grade, feedback, gpa = determine_grade(score)
    save_to_db(score, letter_grade, gpa, name, subject, feedback)
    return jsonify({'score': score, 'letter_grade': letter_grade, 'feedback': feedback, 'gpa': gpa})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=False)
