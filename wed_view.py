from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json

app = Flask(__name__, template_folder='.', static_folder='.')

# Grading system logic
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
    """Determine grade based on score"""
    for threshold in sorted(GRADE_SCALE.keys(), reverse=True):
        if score >= threshold:
            return GRADE_SCALE[threshold]
    return ("F", "Failed. Please seek help immediately!", 0.0)

def save_grade_report(score, letter_grade, gpa, name="", subject=""):
    """Save grade report to grade_history.txt file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = "grade_history.txt"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Test Grader - Grade Report\n")
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
        print(f"Error saving to file: {e}")
        return False

@app.route('/')
def index():
    """Serve the download page"""
    return render_template('test.html')

@app.route('/teacher')
def teacher_console():
    """Serve the teacher console"""
    return render_template('teacher.html')

@app.route('/api/grade', methods=['POST'])
def grade_test():
    """API endpoint to grade a test"""
    try:
        data = request.json
        score = float(data.get('score', 0))
        name = data.get('name', '')
        subject = data.get('subject', '')
        
        if not 0 <= score <= 100:
            return jsonify({'error': 'Score must be between 0 and 100'}), 400
        
        letter_grade, message, gpa = determine_grade(score)
        
        # Save to file
        save_grade_report(score, letter_grade, gpa, name, subject)
        
        return jsonify({
            'success': True,
            'score': score,
            'letter_grade': letter_grade,
            'message': message,
            'gpa': gpa,
            'name': name,
            'subject': subject,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except ValueError:
        return jsonify({'error': 'Invalid score value'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get grade history"""
    try:
        with open('grade_history.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'history': content})
    except FileNotFoundError:
        return jsonify({'history': 'No grade history found yet.'})

if __name__ == '__main__':
    print("🎓 Test Grader Teacher Console Server")
    print("Starting server on http://0.0.0.0:5000")
    print("Open your browser and navigate to the server URL")
    app.run(host='0.0.0.0', port=5000, debug=False)
