import os
import sys
import json
from datetime import datetime
import sqlite3

# Test Grader v11.0.0 - Database Edition
# Advanced grading system with SQLite database storage

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class GradeDatabase:
    def __init__(self, db_name="grades.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database with grades table"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score REAL NOT NULL,
                letter_grade TEXT NOT NULL,
                gpa REAL NOT NULL,
                student_name TEXT,
                subject TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                feedback TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_grade(self, score, letter_grade, gpa, student_name="", subject="", feedback=""):
        """Save grade to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO grades (score, letter_grade, gpa, student_name, subject, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (score, letter_grade, gpa, student_name, subject, feedback))
        conn.commit()
        conn.close()
    
    def get_all_grades(self):
        """Retrieve all grades from database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM grades ORDER BY timestamp DESC')
        grades = cursor.fetchall()
        conn.close()
        return grades
    
    def get_statistics(self):
        """Get grade statistics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_grades,
                AVG(score) as avg_score,
                MAX(score) as highest_score,
                MIN(score) as lowest_score,
                AVG(gpa) as avg_gpa
            FROM grades
        ''')
        stats = cursor.fetchone()
        conn.close()
        return stats

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(Colors.BOLD + Colors.OKBLUE + "="*70)
    print("           TEST GRADER v11.0.0 - DATABASE EDITION")
    print("        Professional Grading with Database Storage")
    print("="*70 + Colors.ENDC)

def get_student_info():
    """Get optional student information"""
    student_name = input(f"{Colors.OKCYAN}Student Name (optional): {Colors.ENDC}").strip()
    subject = input(f"{Colors.OKCYAN}Subject (optional): {Colors.ENDC}").strip()
    return student_name, subject

def determine_grade_advanced(score):
    if score >= 97:
        return "A+", "Outstanding! Exceptional mastery!", "🌟", 4.0
    elif score >= 93:
        return "A", "Excellent work! Superior performance!", "⭐", 4.0
    elif score >= 90:
        return "A-", "Great job! Strong understanding!", "✨", 3.7
    elif score >= 87:
        return "B+", "Very good! Above average work!", "🎯", 3.3
    elif score >= 83:
        return "B", "Good work! Solid performance!", "👍", 3.0
    elif score >= 80:
        return "B-", "Decent job! Room for growth!", "📈", 2.7
    elif score >= 77:
        return "C+", "Fair work! Satisfactory!", "✓", 2.3
    elif score >= 73:
        return "C", "Average performance!", "📝", 2.0
    elif score >= 70:
        return "C-", "Passing but needs improvement!", "⚠️", 1.7
    elif score >= 67:
        return "D+", "Below average. More study needed!", "📚", 1.3
    elif score >= 63:
        return "D", "Poor performance. Significant improvement needed!", "⚡", 1.0
    elif score >= 60:
        return "D-", "Barely passing. Critical improvement required!", "🔻", 0.7
    else:
        return "F", "Failed. Please seek help immediately!", "❌", 0.0

def display_database_stats(db):
    """Display database statistics"""
    stats = db.get_statistics()
    if stats[0] > 0:
        print(f"\n{Colors.BOLD}📊 DATABASE STATISTICS{Colors.ENDC}")
        print("─" * 50)
        print(f"Total Grades Recorded: {stats[0]}")
        print(f"Average Score: {stats[1]:.2f}%")
        print(f"Highest Score: {stats[2]:.2f}%")
        print(f"Lowest Score: {stats[3]:.2f}%")
        print(f"Average GPA: {stats[4]:.2f}/4.0")

def display_recent_grades(db, limit=5):
    """Display recent grades from database"""
    grades = db.get_all_grades()
    if grades:
        print(f"\n{Colors.BOLD}📚 RECENT GRADES (Last {min(limit, len(grades))}){Colors.ENDC}")
        print("─" * 70)
        print(f"{'Date':<12} {'Score':<8} {'Grade':<6} {'GPA':<5} {'Student':<15} {'Subject'}")
        print("─" * 70)
        for grade in grades[:limit]:
            date_str = grade[6][:10] if grade[6] else "N/A"
            student = grade[4][:14] if grade[4] else "Anonymous"
            subject = grade[5][:10] if grade[5] else "General"
            print(f"{date_str:<12} {grade[1]:<8.1f} {grade[2]:<6} {grade[3]:<5.2f} {student:<15} {subject}")

def save_grade_report(score, letter_grade, gpa, student_name="", subject="", timestamp=None):
    """Save grade report to grade_history.txt file"""
    try:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = "grade_history.txt"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Test Grader v11.0.0 - Grade Report\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Student: {student_name or 'Anonymous'}\n")
            f.write(f"Subject: {subject or 'General'}\n")
            f.write(f"Score: {score:.2f}/100\n")
            f.write(f"Letter Grade: {letter_grade}\n")
            f.write(f"GPA: {gpa:.2f}/4.00\n")
            f.write(f"{'='*60}\n\n")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error saving to file: {e}{Colors.ENDC}")
        return False

def main():
    print_banner()
    db = GradeDatabase()
    
    while True:
        try:
            print(f"\n{Colors.BOLD}🎯 DATABASE GRADING SYSTEM{Colors.ENDC}")
            print("1. Grade a test")
            print("2. View database statistics")
            print("3. View recent grades")
            print("4. View grade history (from file)")
            print("5. Export grades to JSON")
            print("6. Exit")
            
            choice = input(f"\n{Colors.OKBLUE}Enter choice (1-6): {Colors.ENDC}").strip()
            
            if choice == "1":
                # Get student info
                student_name, subject = get_student_info()
                
                # Get grade
                try:
                    score = float(input(f"{Colors.OKBLUE}Enter score (0-100): {Colors.ENDC}"))
                    if not 0 <= score <= 100:
                        print(f"{Colors.FAIL}Score must be between 0 and 100!{Colors.ENDC}")
                        continue
                except ValueError:
                    print(f"{Colors.FAIL}Invalid score format!{Colors.ENDC}")
                    continue
                
                # Calculate grade
                letter_grade, message, emoji, gpa = determine_grade_advanced(score)
                
                # Display results
                print(f"\n{Colors.BOLD}📝 RESULTS{Colors.ENDC}")
                print("="*50)
                print(f"Student: {student_name or 'Anonymous'}")
                print(f"Subject: {subject or 'General'}")
                print(f"Score: {score:.1f}%")
                print(f"Grade: {letter_grade} - {message}")
                print(f"GPA: {gpa:.2f}/4.0")
                print(f"Performance: {emoji}")
                
                # Save to database
                db.save_grade(score, letter_grade, gpa, student_name, subject, message)
                print(f"\n{Colors.OKGREEN}✅ Grade saved to database!{Colors.ENDC}")
                
                # Save to grade_history.txt
                if save_grade_report(score, letter_grade, gpa, student_name, subject):
                    print(f"{Colors.OKGREEN}✅ Grade saved to grade_history.txt!{Colors.ENDC}")
                
            elif choice == "2":
                display_database_stats(db)
                input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                
            elif choice == "3":
                display_recent_grades(db, 10)
                input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                
            elif choice == "4":
                # View grade history from file
                try:
                    with open("grade_history.txt", "r", encoding="utf-8") as f:
                        print("\n" + Colors.BOLD + "📚 GRADE HISTORY (from file)" + Colors.ENDC)
                        print("─" * 60)
                        print(f.read())
                        input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                except FileNotFoundError:
                    print(f"{Colors.WARNING}No grade history file found yet.{Colors.ENDC}")
                    input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                
            elif choice == "5":
                # Export to JSON
                grades = db.get_all_grades()
                export_data = []
                for grade in grades:
                    export_data.append({
                        'id': grade[0],
                        'score': grade[1],
                        'letter_grade': grade[2],
                        'gpa': grade[3],
                        'student_name': grade[4],
                        'subject': grade[5],
                        'timestamp': grade[6],
                        'feedback': grade[7]
                    })
                
                with open('grades_export.json', 'w') as f:
                    json.dump(export_data, f, indent=2)
                print(f"{Colors.OKGREEN}✅ Grades exported to grades_export.json!{Colors.ENDC}")
                input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                
            elif choice == "6":
                print(f"\n{Colors.OKGREEN}Thank you for using Test Grader v11.0.0!{Colors.ENDC}")
                break
            else:
                print(f"{Colors.WARNING}Invalid choice!{Colors.ENDC}")
                
            print_banner()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Program interrupted. Goodbye!{Colors.ENDC}")
            break

if __name__ == "__main__":
    main()