from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'v10-secret-key-change-in-production'

USERS = {}
GRADES = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Grader v10.0.0 - Account Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); width: 100%; max-width: 500px; padding: 40px; }
        h1 { color: #4c3f91; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #333; font-weight: 600; }
        input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 10px; }
        button:hover { background: #4c3f91; }
        .toggle { text-align: center; margin-top: 20px; }
        .toggle a { color: #667eea; cursor: pointer; text-decoration: none; }
        .toggle a:hover { text-decoration: underline; }
        .auth-form { display: none; }
        .auth-form.show { display: block; }
        .message { padding: 12px; margin-bottom: 20px; border-radius: 5px; text-align: center; }
        .success { background: #4caf50; color: white; }
        .error { background: #f44336; color: white; }
        .dashboard { display: none; }
        .dashboard.show { display: block; }
        .user-info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .logout-btn { background: #f44336; }
        .logout-btn:hover { background: #da190b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Test Grader v10.0.0</h1>
        
        <div id="authSection">
            <div id="message"></div>
            
            <div id="loginForm" class="auth-form show">
                <h2 style="font-size: 20px; color: #666; margin-bottom: 20px;">Sign In</h2>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="loginEmail" placeholder="Enter your email">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="loginPassword" placeholder="Enter your password">
                </div>
                <button onclick="login()">Sign In</button>
                <div class="toggle">
                    Don't have an account? <a onclick="toggleForms()">Sign Up</a>
                </div>
            </div>
            
            <div id="signupForm" class="auth-form">
                <h2 style="font-size: 20px; color: #666; margin-bottom: 20px;">Create Account</h2>
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="signupName" placeholder="Your name">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="signupEmail" placeholder="Enter your email">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="signupPassword" placeholder="Create a password">
                </div>
                <button onclick="signup()">Sign Up</button>
                <div class="toggle">
                    Already have an account? <a onclick="toggleForms()">Sign In</a>
                </div>
            </div>
        </div>
        
        <div id="dashboard" class="dashboard">
            <div class="user-info">
                <p><strong>Welcome, <span id="userName"></span>!</strong></p>
                <p>Email: <span id="userEmail"></span></p>
            </div>
            <button onclick="window.location.href='/grader'">Go to Grader</button>
            <button class="logout-btn" onclick="logout()">Sign Out</button>
        </div>
    </div>

    <script>
        function toggleForms() {
            document.getElementById('loginForm').classList.toggle('show');
            document.getElementById('signupForm').classList.toggle('show');
        }
        
        function showMessage(msg, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = msg;
            messageDiv.className = 'message ' + type;
            setTimeout(() => messageDiv.className = '', 3000);
        }
        
        function signup() {
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            
            if (!name || !email || !password) {
                showMessage('All fields required', 'error');
                return;
            }
            
            fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showMessage('Account created! Signing in...', 'success');
                    setTimeout(() => login(), 1000);
                } else {
                    showMessage(data.error, 'error');
                }
            });
        }
        
        function login() {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    sessionStorage.setItem('user', JSON.stringify(data.user));
                    showDashboard(data.user);
                } else {
                    showMessage(data.error, 'error');
                }
            });
        }
        
        function logout() {
            sessionStorage.removeItem('user');
            document.getElementById('dashboard').classList.remove('show');
            document.getElementById('authSection').style.display = 'block';
            document.getElementById('loginForm').classList.add('show');
        }
        
        function showDashboard(user) {
            document.getElementById('authSection').style.display = 'none';
            document.getElementById('userName').textContent = user.name;
            document.getElementById('userEmail').textContent = user.email;
            document.getElementById('dashboard').classList.add('show');
        }
        
        window.addEventListener('load', () => {
            const user = JSON.parse(sessionStorage.getItem('user') || 'null');
            if (user) showDashboard(user);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email', '').lower()
    
    if email in USERS:
        return jsonify({'success': False, 'error': 'Email already registered'})
    
    USERS[email] = {
        'name': data.get('name'),
        'email': email,
        'password': generate_password_hash(data.get('password'))
    }
    
    return jsonify({'success': True, 'user': {'name': USERS[email]['name'], 'email': email}})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email', '').lower()
    
    if email not in USERS or not check_password_hash(USERS[email]['password'], data.get('password')):
        return jsonify({'success': False, 'error': 'Invalid email or password'})
    
    return jsonify({'success': True, 'user': {'name': USERS[email]['name'], 'email': email}})

@app.route('/grader')
def grader():
    return '''
    <html>
    <head>
        <title>Grader - v10.0.0</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 8px; }
            h1 { color: #4c3f91; }
            input, button { padding: 10px; margin: 10px 0; width: 100%; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #667eea; color: white; cursor: pointer; border: none; }
            button:hover { background: #4c3f91; }
            .result { margin-top: 30px; padding: 20px; background: #e8f4fd; border-radius: 4px; display: none; }
            .result.show { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Grade Students</h1>
            <form id="gradeForm">
                <input type="text" placeholder="Student Name" id="name">
                <input type="text" placeholder="Subject" id="subject">
                <input type="number" placeholder="Score (0-100)" min="0" max="100" id="score" required>
                <button type="submit">Grade Test</button>
            </form>
            <div id="result" class="result">
                <div id="grade" style="font-size: 36px; font-weight: bold; color: #4c3f91;"></div>
                <p id="feedback"></p>
            </div>
            <button style="background: #f44336; margin-top: 30px;" onclick="window.location.href='/'">Back</button>
        </div>
        <script>
            const GRADES = {97:("A+",4.0),93:("A",4.0),90:("A-",3.7),87:("B+",3.3),83:("B",3.0),80:("B-",2.7),77:("C+",2.3),73:("C",2.0),70:("C-",1.7),67:("D+",1.3),63:("D",1.0),60:("D-",0.7),0:("F",0.0)};
            document.getElementById('gradeForm').addEventListener('submit', (e) => {
                e.preventDefault();
                const score = parseInt(document.getElementById('score').value);
                let grade = "F";
                for (let t of [97,93,90,87,83,80,77,73,70,67,63,60,0]) {
                    if (score >= t) { grade = GRADES[t][0]; break; }
                }
                document.getElementById('grade').textContent = grade;
                document.getElementById('feedback').textContent = 'Score: ' + score + '/100';
                document.getElementById('result').classList.add('show');
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6010, debug=False)
