from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import stripe
from models import db, GradeReport, GradeServer, User as DbUser

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}
app.config['JSON_SORT_KEYS'] = False

db.init_app(app)

# Initialize Stripe - fetch key from Replit connection
def get_stripe_key():
    """Get Stripe secret key from Replit connection"""
    try:
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        x_replit_token = os.environ.get('REPL_IDENTITY')
        
        if not hostname or not x_replit_token:
            return None
            
        url = f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=stripe&environment=development"
        headers = {'X_REPLIT_TOKEN': f'repl {x_replit_token}', 'Accept': 'application/json'}
        
        import requests
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                return data['items'][0].get('settings', {}).get('secret')
    except:
        pass
    return None

stripe_key = get_stripe_key()
if stripe_key:
    stripe.api_key = stripe_key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# Version codes for console access
VERSION_CODES = {
    'GRADE10': 'v10.0.0',
    'GRADE11': 'v11.0.0',
    'GRADE12': 'v12.0.0',
    'GRADE13': 'v13.0.0',
    'GRADE14': 'v14.0.0'
}

# Simple in-memory user storage (replace with database in production)
USERS = {
    '1': {
        'email': 'demo@testgrader.com',
        'name': 'Demo Teacher',
        'password': generate_password_hash('demo123456'),
        'plan': 'free',
        'stripe_customer_id': None
    }
}

class User(UserMixin):
    def __init__(self, id, email, name, plan='free', stripe_customer_id=None):
        self.id = id
        self.email = email
        self.name = name
        self.plan = plan
        self.stripe_customer_id = stripe_customer_id

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        user_data = USERS[user_id]
        return User(
            user_id, 
            user_data['email'], 
            user_data['name'],
            user_data.get('plan', 'free'),
            user_data.get('stripe_customer_id')
        )
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

def save_grade_report(score, letter_grade, feedback, gpa, name="", subject="", server_id=1):
    """Save grade report to database"""
    try:
        grade = GradeReport(
            server_id=server_id,
            student_name=name or 'Anonymous',
            subject=subject or 'General',
            score=score,
            letter_grade=letter_grade,
            feedback=feedback,
            gpa=gpa
        )
        db.session.add(grade)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error saving to database: {e}")
        db.session.rollback()
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

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def api_login():
    """Login API endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json(force=True)
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

        user_info = USERS[user_id]
        user = User(
            user_id, 
            user_info['email'], 
            user_info['name'],
            user_info.get('plan', 'free'),
            user_info.get('stripe_customer_id')
        )
        login_user(user)
        resp = jsonify({'success': True, 'message': 'Logged in successfully'})
        resp.headers['Content-Type'] = 'application/json'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def api_signup():
    """Signup API endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json(force=True)
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
            'password': generate_password_hash(password),
            'plan': 'free',
            'stripe_customer_id': None
        }

        resp = jsonify({'success': True, 'message': 'Account created successfully'})
        resp.headers['Content-Type'] = 'application/json'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Verify version code"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
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
def api_logout():
    """Logout API endpoint"""
    if current_user.is_authenticated:
        logout_user()
    response = jsonify({'success': True, 'message': 'Logged out successfully'})
    response.delete_cookie('code_verified')
    return response

@app.route('/api/grade', methods=['POST'])
def grade_test():
    """API endpoint to grade a test"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.json
        score = float(data.get('score', 0))
        name = data.get('name', '')
        subject = data.get('subject', '')
        version = data.get('version', 'v14.0.0')

        if not 0 <= score <= 100:
            return jsonify({'error': 'Score must be between 0 and 100'}), 400

        letter_grade, message, gpa = determine_grade(score)

        # Find the server by version
        server = GradeServer.query.filter_by(version=version).first()
        if not server:
            return jsonify({'error': f'Version {version} not found'}), 400

        # Save to database with server_id
        save_grade_report(score, letter_grade, message, gpa, name, subject, server.id)

        return jsonify({
            'success': True,
            'score': score,
            'letter_grade': letter_grade,
            'message': message,
            'gpa': gpa,
            'name': name,
            'subject': subject,
            'version': version,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except ValueError:
        return jsonify({'error': 'Invalid score value'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get grade history from database"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        grades = GradeReport.query.order_by(GradeReport.created_at.desc()).all()
        if not grades:
            return jsonify({'history': 'No grade history found yet.', 'records': []})
        return jsonify({
            'history': 'Grade Records',
            'records': [g.to_dict() for g in grades]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/servers', methods=['GET'])
def get_servers():
    """Get all grade servers"""
    try:
        servers = GradeServer.query.all()
        return jsonify({
            'servers': [{
                'id': s.id,
                'version': s.version,
                'port': s.port,
                'status': s.status,
                'created_at': s.created_at.isoformat()
            } for s in servers]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/grades', methods=['GET'])
def get_grades():
    """Get all grade reports"""
    try:
        grades = GradeReport.query.order_by(GradeReport.created_at.desc()).all()
        return jsonify({
            'grades': [g.to_dict() for g in grades]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        server_count = GradeServer.query.count()
        grade_count = GradeReport.query.count()
        
        avg_score = 0
        avg_gpa = 0
        
        if grade_count > 0:
            from sqlalchemy import func
            score_result = db.session.query(func.avg(GradeReport.score)).scalar()
            gpa_result = db.session.query(func.avg(GradeReport.gpa)).scalar()
            avg_score = float(score_result) if score_result else 0
            avg_gpa = float(gpa_result) if gpa_result else 0
        
        return jsonify({
            'server_count': server_count,
            'grade_count': grade_count,
            'avg_score': avg_score,
            'avg_gpa': avg_gpa
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/database')
def database_page():
    """Serve the database management page"""
    try:
        with open('database.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('database.html')

@app.route('/stats')
def stats_page():
    """Serve the statistics page"""
    try:
        with open('stats.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('stats.html')

@app.route('/bucket')
def bucket_page():
    """Serve the pricing bucket page"""
    try:
        with open('bucket.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('bucket.html')

@app.route('/resources')
def resources_page():
    """Serve the Pro resources page"""
    try:
        with open('resources.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('resources.html')

@app.route('/account')
@login_required
def account_page():
    """Serve the user account page"""
    try:
        with open('account.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('account.html')

@app.route('/api/account')
def get_account():
    """Get user account information"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        if current_user.id in USERS:
            user_data = USERS[current_user.id]
            return jsonify({
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email,
                'plan': user_data.get('plan', 'free'),
                'stripe_customer_id': user_data.get('stripe_customer_id')
            })
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-stripe-session', methods=['POST'])
def verify_stripe_session():
    """Verify Stripe session and mark user as upgraded to pro"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            # If no session ID provided, just check if user has pro features
            # This handles the case where Stripe isn't configured (demo mode)
            if current_user.id in USERS:
                return jsonify({
                    'success': True, 
                    'plan': USERS[current_user.id].get('plan', 'free')
                })
            return jsonify({'error': 'User not found'}), 404
        
        # Try to retrieve the session from Stripe
        if stripe_key:
            try:
                session_obj = stripe.checkout.Session.retrieve(session_id)
                if session_obj.payment_status == 'paid':
                    # Payment confirmed! Upgrade user to pro
                    if current_user.id in USERS:
                        USERS[current_user.id]['plan'] = 'pro'
                        USERS[current_user.id]['stripe_customer_id'] = session_obj.customer
                        return jsonify({'success': True, 'plan': 'pro'})
            except stripe.error.APIError as e:
                print(f"Stripe session verification error: {e}")
        
        # If Stripe not available or payment not confirmed, upgrade anyway (demo mode)
        if current_user.id in USERS:
            USERS[current_user.id]['plan'] = 'pro'
            return jsonify({'success': True, 'plan': 'pro'})
        
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"Error verifying session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upgrade-to-pro', methods=['POST'])
def upgrade_to_pro():
    """Upgrade user to pro plan (after payment confirmation)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        if current_user.id in USERS:
            USERS[current_user.id]['plan'] = 'pro'
            return jsonify({'success': True, 'plan': 'pro'})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checkout-pro', methods=['POST'])
def checkout_pro():
    """Create checkout session for Pro plan ($9/month)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Please log in first'}), 401
            
        if not stripe_key:
            # If Stripe not configured, just upgrade user to pro for demo
            if current_user.id in USERS:
                USERS[current_user.id]['plan'] = 'pro'
                return jsonify({'url': '/account?upgraded=true'})
            return jsonify({'error': 'Payment system not configured'}), 500
        
        current_url = request.host_url.rstrip('/')
        try:
            session_obj = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Pro Plan',
                            'description': 'Professional grading system - $9/month',
                        },
                        'unit_amount': 900,  # $9.00
                        'recurring': {
                            'interval': 'month',
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'{current_url}/account?upgraded=true',
                cancel_url=f'{current_url}/bucket?cancel=true',
                customer_email=current_user.email,
            )
            # Store session ID in user data to verify on success
            if current_user.id in USERS:
                USERS[current_user.id]['stripe_checkout_session'] = session_obj.id
            return jsonify({
                'url': session_obj.url,
                'session_id': session_obj.id
            })
        except stripe.error.InvalidRequestError as e:
            print(f"Stripe InvalidRequestError: {e}")
            return jsonify({'error': 'Payment configuration error. Please try again or contact support.'}), 500
        except stripe.error.AuthenticationError as e:
            print(f"Stripe AuthenticationError: {e}")
            return jsonify({'error': 'Payment system authentication failed. Please contact support.'}), 500
        except stripe.error.APIError as e:
            print(f"Stripe APIError: {e}")
            return jsonify({'error': f'Payment error: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error in checkout_pro: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/checkout-enterprise', methods=['POST'])
def checkout_enterprise():
    """Create checkout session for Enterprise plan (contact sales)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # For enterprise, we don't create a session - just return a mailto link
        return jsonify({
            'email': 'support@testgrader.com',
            'message': 'Please contact our sales team for enterprise pricing'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-pro-access/<resource>')
def check_pro_access(resource):
    """Check if user has access to a Pro resource"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'access': False, 'reason': 'Not authenticated'}), 401
        
        if current_user.id in USERS:
            user_plan = USERS[current_user.id].get('plan', 'free')
            has_access = user_plan in ['pro', 'enterprise']
            return jsonify({
                'access': has_access,
                'resource': resource,
                'plan': user_plan,
                'message': 'You have access to this resource' if has_access else 'Upgrade to Pro to access this resource'
            })
        return jsonify({'access': False, 'reason': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Download grades as PDF - Pro only"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        if current_user.id not in USERS:
            return jsonify({'error': 'User not found'}), 404
        
        user_plan = USERS[current_user.id].get('plan', 'free')
        if user_plan not in ['pro', 'enterprise']:
            return jsonify({'error': 'PDF export is a Pro feature. Upgrade to access this feature.'}), 403
        
        # Generate PDF (placeholder - in real app would generate actual PDF)
        return jsonify({
            'success': True,
            'message': 'PDF export would be generated here',
            'url': '/download/grades-report.pdf'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced-analytics')
def advanced_analytics():
    """Get advanced analytics - Pro only"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        if current_user.id not in USERS:
            return jsonify({'error': 'User not found'}), 404
        
        user_plan = USERS[current_user.id].get('plan', 'free')
        if user_plan not in ['pro', 'enterprise']:
            return jsonify({'error': 'Advanced analytics is a Pro feature. Upgrade to access this feature.'}), 403
        
        # Return advanced analytics
        grades = GradeReport.query.all()
        if not grades:
            return jsonify({
                'percentile': {},
                'trends': {},
                'insights': 'No grade data available'
            })
        
        from sqlalchemy import func
        # Advanced stats
        score_dist = db.session.query(
            func.floor(GradeReport.score / 10),
            func.count(GradeReport.id)
        ).group_by(func.floor(GradeReport.score / 10)).all()
        
        return jsonify({
            'grade_distribution': {str(k*10): v for k, v in score_dist},
            'total_grades': len(grades),
            'insights': 'Advanced analytics available with Pro plan'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
def get_users():
    """Get all user accounts - returns email and password hash"""
    try:
        users = []
        for user_id, user_data in USERS.items():
            users.append({
                'id': user_id,
                'name': user_data.get('name', 'Unknown'),
                'email': user_data.get('email', ''),
                'password': user_data.get('password', ''),
                'plan': user_data.get('plan', 'free'),
                'created_at': 'System User'
            })
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a file"""
    try:
        import os
        from flask import send_file
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename:
            return "Invalid filename", 400
        filepath = filename
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default servers for all versions if they don't exist
        versions = [
            {'version': 'v10.0.0', 'port': 5010},
            {'version': 'v11.0.0', 'port': 5011},
            {'version': 'v12.0.0', 'port': 5012},
            {'version': 'v13.0.0', 'port': 5013},
            {'version': 'v14.0.0', 'port': 5000},
        ]
        
        for ver in versions:
            server = GradeServer.query.filter_by(version=ver['version']).first()
            if not server:
                server = GradeServer(version=ver['version'], port=ver['port'], status='active')
                db.session.add(server)
        
        db.session.commit()
    
    print("🎓 Test Grader Teacher Console Server")
    print("Starting server on http://0.0.0.0:5000")
    print("Open your browser and navigate to the server URL")
    print("Go to /auth for login/signup or /teacher for the console")
    app.run(host='0.0.0.0', port=5000, debug=False)
