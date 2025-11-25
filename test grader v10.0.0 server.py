from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Grading scale
GRADE_SCALE = {
    97: ("A+", "Outstanding! Exceptional mastery!", 4.0),
    93: ("A", "Excellent work! Superior performance!", 4.0),
    90: ("A-", "Great job! Strong understanding!", 3.7),
    87: ("B+", "Very good! Above average work!", 3.3),
    83: ("B", "Good work! Solid performance!", 3.0),
    80: ("B-", "Decent job! Room for growth!", 2.7),
    77: ("C+", "Fair work! Satisfactory!", 2.3),
    73: ("C", "Average performance!", 2.0),
    70: ("C-", "Passing but needs improvement!", 1.7),
    67: ("D+", "Below average. More study needed!", 1.3),
    63: ("D", "Poor performance. Significant improvement needed!", 1.0),
    60: ("D-", "Barely passing. Critical improvement required!", 0.7),
    0: ("F", "Failed. Please seek help immediately!", 0.0)
}

def determine_grade(score):
    for threshold in sorted(GRADE_SCALE.keys(), reverse=True):
        if score >= threshold:
            return GRADE_SCALE[threshold]
    return ("F", "Failed. Please seek help immediately!", 0.0)

def save_grade_report(score, letter_grade, gpa, name="", subject=""):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("grade_history.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Test Grader v10.0.0 - Grade Report\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Student: {name or 'Anonymous'}\n")
            f.write(f"Subject: {subject or 'General'}\n")
            f.write(f"Score: {score:.2f}/100\n")
            f.write(f"Letter Grade: {letter_grade}\n")
            f.write(f"GPA: {gpa:.2f}/4.00\n")
            f.write(f"{'='*60}\n\n")
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Grader v10.0.0 - Web Server</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #4c3f91; }
        input, button { padding: 10px; margin: 10px 0; width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4c3f91; color: white; cursor: pointer; border: none; }
        button:hover { background: #3b2f70; }
        .result { margin-top: 30px; padding: 20px; background: #e8f4fd; border-radius: 4px; display: none; }
        .result.show { display: block; }
        .grade-display { font-size: 36px; color: #4c3f91; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Test Grader v10.0.0</h1>
        <p>Enter student information and grade</p>
        
        <form id="gradeForm">
            <input type="text" id="name" placeholder="Student Name" />
            <input type="text" id="subject" placeholder="Subject/Course" />
            <input type="number" id="score" placeholder="Score (0-100)" min="0" max="100" required />
            <button type="submit">Grade Test</button>
        </form>
        
        <div id="result" class="result">
            <div class="grade-display" id="letterGrade"></div>
            <p><strong>Score:</strong> <span id="scoreDisplay"></span>/100</p>
            <p><strong>GPA Equivalent:</strong> <span id="gpaDisplay"></span>/4.0</p>
            <p><strong>Feedback:</strong> <span id="feedback"></span></p>
        </div>
    </div>

    <script>
        document.getElementById('gradeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const score = parseFloat(document.getElementById('score').value);
            const name = document.getElementById('name').value;
            const subject = document.getElementById('subject').value;
            
            const response = await fetch('/api/grade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ score, name, subject })
            });
            const data = await response.json();
            
            document.getElementById('letterGrade').textContent = data.letter_grade;
            document.getElementById('scoreDisplay').textContent = data.score;
            document.getElementById('gpaDisplay').textContent = data.gpa.toFixed(2);
            document.getElementById('feedback').textContent = data.feedback;
            document.getElementById('result').classList.add('show');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/grade', methods=['POST'])
def grade_test():
    data = request.json
    score = float(data.get('score', 0))
    name = data.get('name', '')
    subject = data.get('subject', '')
    
    letter_grade, feedback, gpa = determine_grade(score)
    save_grade_report(score, letter_grade, gpa, name, subject)
    
    return jsonify({
        'score': score,
        'letter_grade': letter_grade,
        'feedback': feedback,
        'gpa': gpa
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=False)
