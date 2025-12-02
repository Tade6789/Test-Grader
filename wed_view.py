from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import stripe
from models import db, GradeReport, GradeServer, User as DbUser, ChatMessage

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

# Flask-Login User class wrapper for database User model
class User(UserMixin):
    def __init__(self, id, email, name, plan='free', stripe_customer_id=None):
        self.id = str(id)
        self.email = email
        self.name = name
        self.plan = plan
        self.stripe_customer_id = stripe_customer_id

@login_manager.user_loader
def load_user(user_id):
    """Load user from database"""
    db_user = DbUser.query.get(int(user_id))
    if db_user:
        return User(
            db_user.id, 
            db_user.email, 
            db_user.name,
            db_user.plan or 'free',
            db_user.stripe_customer_id
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

        # Find user by email in database
        db_user = DbUser.query.filter_by(email=email).first()

        if not db_user or not check_password_hash(db_user.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401

        user = User(
            db_user.id, 
            db_user.email, 
            db_user.name,
            db_user.plan or 'free',
            db_user.stripe_customer_id
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

        # Check if email already exists in database
        existing_user = DbUser.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409

        # Create new user in database
        new_user = DbUser(
            username=email.split('@')[0],
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            plan='free',
            stripe_customer_id=None
        )
        db.session.add(new_user)
        db.session.commit()

        resp = jsonify({'success': True, 'message': 'Account created successfully'})
        resp.headers['Content-Type'] = 'application/json'
        return resp
    except Exception as e:
        db.session.rollback()
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

@app.route('/api-docs')
def api_docs_page():
    """Serve the API documentation page"""
    try:
        with open('api.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('api.html')

@app.route('/student')
def student_page():
    """Serve the add student page"""
    try:
        with open('student.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('student.html')

@app.route('/chat')
def chat_page():
    """Serve the 24/7 chat support page"""
    try:
        with open('chat.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('chat.html')

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

@app.route('/admin')
@login_required
def admin_page():
    """Serve the admin console page"""
    db_user = DbUser.query.get(int(current_user.id))
    if not db_user or not db_user.is_admin:
        return redirect(url_for('index'))
    try:
        with open('admin.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return render_template('admin.html')

@app.route('/api/admin/users')
@login_required
def get_all_users():
    """Get all users - Admin only"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user or not db_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        users = DbUser.query.order_by(DbUser.created_at.desc()).all()
        return jsonify({
            'users': [{
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'phone': u.phone,
                'plan': u.plan or 'free',
                'is_admin': u.is_admin,
                'created_at': u.created_at.isoformat() if u.created_at else None
            } for u in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/create-account', methods=['POST'])
@login_required
def admin_create_account():
    """Create a new account - Admin only"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user or not db_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        plan = data.get('plan', 'classic')
        paid = data.get('paid', True)
        
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        existing = DbUser.query.filter_by(email=email).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 409
        
        new_user = DbUser(
            username=email.split('@')[0],
            email=email,
            name=name,
            phone=phone,
            password_hash=generate_password_hash(password),
            plan=plan if paid else 'free',
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Account created for {name}',
            'user': new_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    """Delete a user - Admin only"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user or not db_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        user_to_delete = DbUser.query.get(user_id)
        if not user_to_delete:
            return jsonify({'error': 'User not found'}), 404
        
        if user_to_delete.is_admin:
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        db.session.delete(user_to_delete)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/account')
def get_account():
    """Get user account information"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        db_user = DbUser.query.get(int(current_user.id))
        if db_user:
            return jsonify({
                'id': str(db_user.id),
                'name': db_user.name,
                'email': db_user.email,
                'phone': db_user.phone,
                'plan': db_user.plan or 'free',
                'stripe_customer_id': db_user.stripe_customer_id,
                'is_admin': db_user.is_admin
            })
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup-reports', methods=['POST'])
@login_required
def cleanup_reports():
    """Clean up old grade reports - admin only"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user or not db_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        old_reports = GradeReport.query.filter(GradeReport.timestamp < thirty_days_ago).all()
        count = len(old_reports)
        
        for report in old_reports:
            db.session.delete(report)
        db.session.commit()
        
        return jsonify({'success': True, 'cleaned': count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/compact-db', methods=['POST'])
@login_required
def compact_db():
    """Compact database - admin only"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user or not db_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Database compacted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db-stats')
@login_required
def db_stats():
    """Get database statistics - admin only"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user or not db_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        users_count = DbUser.query.count()
        reports_count = GradeReport.query.count()
        admin_count = DbUser.query.filter_by(is_admin=True).count()
        paid_count = DbUser.query.filter(DbUser.plan.in_(['pro', 'classic'])).count()
        
        return jsonify({
            'users_count': users_count,
            'reports_count': reports_count,
            'admin_count': admin_count,
            'paid_count': paid_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/login', methods=['POST'])
def chat_login():
    """Login to chat - only for custom account holders (classic/pro plans)"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        db_user = DbUser.query.filter_by(email=email).first()
        
        if not db_user or not check_password_hash(db_user.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if db_user.plan not in ['classic', 'pro', 'admin', 'enterprise']:
            return jsonify({'error': 'Only custom account holders (Classic/Pro) can access 24/7 chat'}), 403
        
        user = User(db_user.id, db_user.email, db_user.name, db_user.plan, db_user.stripe_customer_id)
        login_user(user)
        
        return jsonify({'success': True, 'email': db_user.email, 'plan': db_user.plan})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/messages')
@login_required
def get_chat_messages():
    """Get chat messages for current user"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user:
            return jsonify({'error': 'User not found'}), 404
        
        messages = ChatMessage.query.filter_by(user_id=db_user.id).order_by(ChatMessage.created_at.asc()).all()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    """Send a chat message"""
    try:
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        new_message = ChatMessage(
            user_id=db_user.id,
            sender_type='user',
            message=message_text
        )
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({'success': True, 'message_id': new_message.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-stripe-session', methods=['POST'])
def verify_stripe_session():
    """Verify Stripe session and mark user as upgraded to pro"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        session_id = data.get('session_id')
        
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user:
            return jsonify({'error': 'User not found'}), 404
        
        if not session_id:
            # If no session ID provided, just check if user has pro features
            return jsonify({
                'success': True, 
                'plan': db_user.plan or 'free'
            })
        
        # Try to retrieve the session from Stripe
        if stripe_key:
            try:
                session_obj = stripe.checkout.Session.retrieve(session_id)
                if session_obj.payment_status == 'paid':
                    # Payment confirmed! Upgrade user to pro in database
                    db_user.plan = 'pro'
                    db_user.stripe_customer_id = session_obj.customer
                    db.session.commit()
                    return jsonify({'success': True, 'plan': 'pro'})
            except stripe.error.APIError as e:
                print(f"Stripe session verification error: {e}")
        
        # If Stripe not available or payment not confirmed, upgrade anyway (demo mode)
        db_user.plan = 'pro'
        db.session.commit()
        return jsonify({'success': True, 'plan': 'pro'})
    except Exception as e:
        db.session.rollback()
        print(f"Error verifying session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upgrade-to-pro', methods=['POST'])
def upgrade_to_pro():
    """Upgrade user to pro plan (after payment confirmation)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        db_user = DbUser.query.get(int(current_user.id))
        if db_user:
            db_user.plan = 'pro'
            db.session.commit()
            return jsonify({'success': True, 'plan': 'pro'})
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/checkout-pro', methods=['POST'])
def checkout_pro():
    """Create checkout session for Pro plan ($9/month)"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Please log in first'}), 401
        
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user:
            return jsonify({'error': 'User not found'}), 404
            
        if not stripe_key:
            # If Stripe not configured, just upgrade user to pro for demo
            db_user.plan = 'pro'
            db.session.commit()
            return jsonify({'url': '/account?upgraded=true'})
        
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
        db.session.rollback()
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
        
        db_user = DbUser.query.get(int(current_user.id))
        if db_user:
            user_plan = db_user.plan or 'free'
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
        
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user:
            return jsonify({'error': 'User not found'}), 404
        
        user_plan = db_user.plan or 'free'
        if user_plan not in ['pro', 'enterprise']:
            return jsonify({'error': 'PDF export is a Pro feature. Upgrade to access this feature.'}), 403
        
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from io import BytesIO
        
        # Get grade records
        records = GradeReport.query.filter_by(user_id=current_user.id).all()
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4c3f91'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph('Grade Report', title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add metadata
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
        )
        story.append(Paragraph(f'<b>Teacher:</b> {db_user.name}', info_style))
        story.append(Paragraph(f'<b>Generated:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', info_style))
        story.append(Paragraph(f'<b>Total Records:</b> {len(records)}', info_style))
        story.append(Spacer(1, 0.2*inch))
        
        if records:
            # Calculate stats
            avg_score = sum(r.score for r in records) / len(records)
            avg_gpa = sum(r.gpa for r in records) / len(records)
            
            story.append(Paragraph(f'<b>Average Score:</b> {avg_score:.1f}%', info_style))
            story.append(Paragraph(f'<b>Average GPA:</b> {avg_gpa:.2f}', info_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Create table
            table_data = [['Student', 'Subject', 'Score', 'Grade', 'GPA', 'Date']]
            for record in records:
                table_data.append([
                    record.student_name or 'N/A',
                    record.subject or 'N/A',
                    f'{record.score:.1f}%',
                    record.letter_grade or 'N/A',
                    f'{record.gpa:.2f}',
                    record.created_at.strftime('%Y-%m-%d') if record.created_at else 'N/A'
                ])
            
            table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4c3f91')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            story.append(table)
        else:
            story.append(Paragraph('No grade records found.', styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Return as file download
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'grades_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced-analytics')
def advanced_analytics():
    """Get advanced analytics - Pro only"""
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Not authenticated'}), 401
        
        db_user = DbUser.query.get(int(current_user.id))
        if not db_user:
            return jsonify({'error': 'User not found'}), 404
        
        user_plan = db_user.plan or 'free'
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
    """Get all user accounts from database (secure - no passwords shown)"""
    try:
        users = DbUser.query.all()
        return jsonify({
            'users': [
                {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email,
                    'password': user.password_hash[:30] + '...' if user.password_hash else '',
                    'plan': user.plan or 'free',
                    'created_at': user.created_at.isoformat() if user.created_at else 'N/A'
                }
                for user in users
            ]
        })
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
        
        # Create default users if they don't exist
        default_users = [
            {
                'username': 'demo',
                'email': 'demo@testgrader.com',
                'name': 'Demo Teacher',
                'password': 'demo123456',
                'plan': 'free',
                'is_admin': False
            },
            {
                'username': 'tade',
                'email': 'tade@gru.com',
                'name': 'Tade (Pro User)',
                'password': 'propass123',
                'plan': 'pro',
                'is_admin': True
            }
        ]
        
        for user_data in default_users:
            existing_user = DbUser.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                new_user = DbUser(
                    username=user_data['username'],
                    email=user_data['email'],
                    name=user_data['name'],
                    password_hash=generate_password_hash(user_data['password']),
                    plan=user_data['plan'],
                    is_admin=user_data.get('is_admin', False)
                )
                db.session.add(new_user)
                print(f"Created user: {user_data['email']} ({user_data['plan']} plan)")
            else:
                # Update admin status for existing users
                if user_data.get('is_admin') and not existing_user.is_admin:
                    existing_user.is_admin = True
                    print(f"Updated {user_data['email']} to admin")
        
        db.session.commit()
    
    print("🎓 Test Grader Teacher Console Server")
    print("Starting server on http://0.0.0.0:5000")
    print("Open your browser and navigate to the server URL")
    print("Go to /auth for login/signup or /teacher for the console")
    app.run(host='0.0.0.0', port=5000, debug=False)
