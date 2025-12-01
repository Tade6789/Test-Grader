from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class GradeServer(db.Model):
    """Model for grader servers"""
    __tablename__ = 'grade_servers'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    grades = db.relationship('GradeReport', backref='server', lazy=True, cascade='all, delete-orphan')

class GradeReport(db.Model):
    """Model for storing grade reports"""
    __tablename__ = 'grade_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('grade_servers.id'), nullable=False)
    student_name = db.Column(db.String(255), default='Anonymous')
    subject = db.Column(db.String(255), default='General')
    score = db.Column(db.Float, nullable=False)
    letter_grade = db.Column(db.String(2), nullable=False)
    feedback = db.Column(db.Text)
    gpa = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'subject': self.subject,
            'score': self.score,
            'letter_grade': self.letter_grade,
            'feedback': self.feedback,
            'gpa': self.gpa,
            'created_at': self.created_at.isoformat()
        }

class User(db.Model):
    """Model for storing teacher/admin users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    plan = db.Column(db.String(20), default='free')
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'plan': self.plan,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
