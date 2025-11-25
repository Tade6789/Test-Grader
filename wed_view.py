from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__, template_folder='.', static_folder='.')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# Version codes for console access
VERSION_CODES = {
    'GRADE10': 'v10.0.0',
    'GRADE11': 'v11.0.0',
    'GRADE12': 'v12.0.0',
    'GRADE13': 'v13.0.0'
}

# Simple in-memory user storage (replace with database in production)
USERS = {}

class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        user_data = USERS[user_id]
        return User(user_id, user_data['email'], user_data['name'])
    return None

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
    """Serve the homepage"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('index.html')

@app.route('/test.html')
@app.route('/downloads')
def downloads():
    """Serve the downloads page"""
    try:
        with open('test.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('test.html')

@app.route('/auth')
def auth():
    """Serve the auth page"""
    if current_user.is_authenticated:
        return redirect(url_for('teacher_console'))
    try:
        with open('auth.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('auth.html')

@app.route('/code')
@login_required
def code_verification():
    """Serve the code verification page"""
    try:
        with open('code.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('code.html')

@app.route('/teacher')
@login_required
def teacher_console():
    """Serve the teacher console"""
    code_verified = request.cookies.get('code_verified')
    if not code_verified:
        return redirect(url_for('code_verification'))
    try:
        with open('teacher.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('teacher.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login API endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        # Find user by email
        user_id = None
        for uid, user_data in USERS.items():
            if user_data['email'] == email:
                user_id = uid
                break

        if not user_id or not check_password_hash(USERS[user_id]['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        user = User(user_id, USERS[user_id]['email'], USERS[user_id]['name'])
        login_user(user)
        return jsonify({'success': True, 'message': 'Logged in successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Signup API endpoint"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Check if email already exists
        for user_data in USERS.values():
            if user_data['email'] == email:
                return jsonify({'error': 'Email already registered'}), 409

        # Create new user
        user_id = str(len(USERS) + 1)
        USERS[user_id] = {
            'email': email,
            'name': name,
            'password': generate_password_hash(password)
        }

        return jsonify({'success': True, 'message': 'Account created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-code', methods=['POST'])
@login_required
def verify_code():
    """Verify version code"""
    try:
        data = request.json
        code = data.get('code', '').upper().strip()

        if not code:
            return jsonify({'error': 'Code required'}), 400

        if code not in VERSION_CODES:
            return jsonify({'error': 'Invalid code. Please try again.'}), 401

        response = jsonify({'success': True, 'version': VERSION_CODES[code]})
        response.set_cookie('code_verified', code, max_age=3600, httponly=True)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """Logout API endpoint"""
    logout_user()
    response = jsonify({'success': True, 'message': 'Logged out successfully'})
    response.delete_cookie('code_verified')
    return response

@app.route('/api/grade', methods=['POST'])
@login_required
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
@login_required
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
    print("Go to /auth for login/signup or /teacher for the console")
    app.run(host='0.0.0.0', port=5000, debug=False)
