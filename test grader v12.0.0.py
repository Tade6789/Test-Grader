import os
import sys
import json
import csv
from datetime import datetime
import statistics

# Test Grader v12.0.0 - Professional Plus Edition
# Advanced grading with export features and analytics

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestGraderV12:
    def __init__(self):
        self.all_grades = []
        self.session_start = datetime.now()
        self.grade_history = []
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Display the application banner"""
        self.clear_screen()
        print(Colors.BOLD + Colors.HEADER + "="*65)
        print("        TEST GRADER v12.0.0 - PROFESSIONAL PLUS EDITION")
        print("         Advanced Analytics & Export Capabilities")
        print("="*65 + Colors.ENDC)
        print()
    
    def get_student_info(self):
        """Get student information"""
        print(Colors.OKBLUE + "📝 Student Information" + Colors.ENDC)
        print("-" * 40)
        name = input("Student Name (or press Enter to skip): ").strip()
        student_id = input("Student ID (or press Enter to skip): ").strip()
        subject = input("Subject/Course (or press Enter to skip): ").strip()
        return name or "Anonymous", student_id or "N/A", subject or "General"
    
    def get_valid_grade(self):
        """Get a valid grade input with enhanced validation"""
        while True:
            try:
                grade_input = input(f"\n{Colors.OKBLUE}Enter grade (0-100) or 'q' to quit:{Colors.ENDC} ")
                if grade_input.lower() == 'q':
                    return None
                    
                grade = float(grade_input)
                if 0 <= grade <= 100:
                    return grade
                else:
                    print(f"{Colors.WARNING}⚠️ Grade must be between 0 and 100.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.FAIL}❌ Invalid input! Please enter a number.{Colors.ENDC}")
    
    def determine_grade_advanced(self, score):
        """Advanced grading system with detailed categorization"""
        grades = [
            (97, "A+", "Outstanding! Exceptional mastery!", "🏆", Colors.OKGREEN),
            (93, "A", "Excellent work! Superior performance!", "⭐", Colors.OKGREEN),
            (90, "A-", "Great job! Strong understanding!", "✨", Colors.OKGREEN),
            (87, "B+", "Very good! Above average work!", "🎯", Colors.OKCYAN),
            (83, "B", "Good work! Solid performance!", "👍", Colors.OKCYAN),
            (80, "B-", "Decent job! Room for growth!", "📈", Colors.OKCYAN),
            (77, "C+", "Fair work! Satisfactory!", "✓", Colors.WARNING),
            (73, "C", "Average performance!", "📝", Colors.WARNING),
            (70, "C-", "Passing but needs improvement!", "⚠️", Colors.WARNING),
            (67, "D+", "Below average. More study needed!", "📚", Colors.WARNING),
            (63, "D", "Poor performance. Significant improvement needed!", "⚡", Colors.FAIL),
            (60, "D-", "Barely passing. Critical improvement required!", "🔻", Colors.FAIL),
            (0, "F", "Failed. Please seek help immediately!", "❌", Colors.FAIL)
        ]
        
        for min_score, grade, message, emoji, color in grades:
            if score >= min_score:
                return grade, message, emoji, color
    
    def calculate_gpa(self, letter_grade):
        """Calculate GPA equivalent"""
        gpa_map = {
            "A+": 4.0, "A": 4.0, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "D-": 0.7,
            "F": 0.0
        }
        return gpa_map.get(letter_grade, 0.0)
    
    def calculate_statistics(self, grades_list):
        """Calculate comprehensive statistics"""
        if not grades_list:
            return None
            
        stats = {
            'mean': statistics.mean(grades_list),
            'median': statistics.median(grades_list),
            'mode': None,
            'std_dev': statistics.stdev(grades_list) if len(grades_list) > 1 else 0,
            'variance': statistics.variance(grades_list) if len(grades_list) > 1 else 0,
            'min': min(grades_list),
            'max': max(grades_list),
            'range': max(grades_list) - min(grades_list),
            'count': len(grades_list)
        }
        
        try:
            stats['mode'] = statistics.mode(grades_list)
        except:
            stats['mode'] = "N/A"
            
        return stats
    
    def export_to_csv(self, data, filename=None):
        """Export grades to CSV file"""
        if not filename:
            filename = f"grades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Timestamp', 'Name', 'ID', 'Subject', 'Score', 'Grade', 'GPA']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in data:
                    writer.writerow({
                        'Timestamp': entry['timestamp'],
                        'Name': entry['name'],
                        'ID': entry['student_id'],
                        'Subject': entry['subject'],
                        'Score': entry['score'],
                        'Grade': entry['letter_grade'],
                        'GPA': entry['gpa']
                    })
            return filename
        except Exception as e:
            print(f"{Colors.FAIL}Error exporting to CSV: {e}{Colors.ENDC}")
            return None
    
    def export_to_json(self, data, filename=None):
        """Export grades to JSON file"""
        if not filename:
            filename = f"grades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=4, default=str)
            return filename
        except Exception as e:
            print(f"{Colors.FAIL}Error exporting to JSON: {e}{Colors.ENDC}")
            return None
    
    def display_analytics_dashboard(self):
        """Display comprehensive analytics dashboard"""
        if not self.all_grades:
            print(f"{Colors.WARNING}No grades to analyze yet.{Colors.ENDC}")
            return
            
        scores = [g['score'] for g in self.all_grades]
        stats = self.calculate_statistics(scores)
        
        print("\n" + Colors.BOLD + Colors.OKCYAN + "📊 ANALYTICS DASHBOARD" + Colors.ENDC)
        print("="*65)
        
        # Basic Statistics
        print(Colors.BOLD + "\n📈 Statistical Summary:" + Colors.ENDC)
        print(f"  • Mean Score:      {stats['mean']:.2f}")
        print(f"  • Median Score:    {stats['median']:.2f}")
        print(f"  • Mode Score:      {stats['mode']}")
        print(f"  • Std Deviation:   {stats['std_dev']:.2f}")
        print(f"  • Variance:        {stats['variance']:.2f}")
        print(f"  • Score Range:     {stats['min']:.2f} - {stats['max']:.2f}")
        print(f"  • Total Tests:     {stats['count']}")
        
        # Grade Distribution
        print(Colors.BOLD + "\n📊 Grade Distribution:" + Colors.ENDC)
        grade_counts = {}
        for g in self.all_grades:
            grade = g['letter_grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        for grade in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']:
            if grade in grade_counts:
                count = grade_counts[grade]
                percentage = (count / len(self.all_grades)) * 100
                bar = '█' * int(percentage / 2)
                print(f"  {grade:3} [{count:2}] {bar} {percentage:.1f}%")
        
        # Performance Trends
        if len(self.all_grades) > 1:
            print(Colors.BOLD + "\n📈 Performance Trend:" + Colors.ENDC)
            recent_avg = statistics.mean(scores[-5:])
            overall_avg = statistics.mean(scores)
            trend = recent_avg - overall_avg
            
            if trend > 0:
                print(f"  ↗️ Recent performance is {trend:.2f} points above average")
            elif trend < 0:
                print(f"  ↘️ Recent performance is {abs(trend):.2f} points below average")
            else:
                print(f"  → Performance is stable")
    
    def display_advanced_visualization(self, score, letter_grade):
        """Display enhanced visual representation"""
        max_bars = 50
        filled_bars = int((score / 100) * max_bars)
        empty_bars = max_bars - filled_bars
        
        print("\n" + Colors.BOLD + "📊 SCORE VISUALIZATION" + Colors.ENDC)
        print("─" * 65)
        
        # Determine color
        if score >= 90:
            bar_color = Colors.OKGREEN
        elif score >= 80:
            bar_color = Colors.OKCYAN
        elif score >= 70:
            bar_color = Colors.WARNING
        else:
            bar_color = Colors.FAIL
        
        print(f"Score: {score:.1f}% | Grade: {letter_grade}")
        print(f"0{'─' * (max_bars-2)}100")
        print(f"[{bar_color}{'█' * filled_bars}{Colors.ENDC}{'░' * empty_bars}]")
        
        # Show percentile
        if self.all_grades:
            scores = [g['score'] for g in self.all_grades]
            percentile = sum(1 for s in scores if s <= score) / len(scores) * 100
            print(f"Percentile: {percentile:.1f}th (better than {percentile:.0f}% of all grades)")
        
        print()
    
    def save_grade_report(self, score, letter_grade, gpa, name="", subject="", timestamp=None):
        """Save grade report to grade_history.txt file"""
        try:
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = "grade_history.txt"
            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Test Grader v12.0.0 - Grade Report\n")
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
            print(f"{Colors.FAIL}Error saving to file: {e}{Colors.ENDC}")
            return False
    
    def run(self):
        """Main application loop"""
        self.print_banner()
        
        while True:
            print("\n" + Colors.BOLD + "🎯 MAIN MENU" + Colors.ENDC)
            print("─" * 40)
            print("1. Grade a new test")
            print("2. View analytics dashboard")
            print("3. Export grades to CSV")
            print("4. Export grades to JSON")
            print("5. View all grades")
            print("6. View grade history (from file)")
            print("7. Clear session")
            print("8. Exit")
            
            choice = input(f"\n{Colors.OKBLUE}Select option (1-8):{Colors.ENDC} ").strip()
            
            if choice == "1":
                # Grade a new test
                self.print_banner()
                name, student_id, subject = self.get_student_info()
                grade = self.get_valid_grade()
                
                if grade is not None:
                    letter_grade, message, emoji, color = self.determine_grade_advanced(grade)
                    gpa = self.calculate_gpa(letter_grade)
                    
                    # Store grade
                    grade_entry = {
                        'timestamp': datetime.now(),
                        'name': name,
                        'student_id': student_id,
                        'subject': subject,
                        'score': grade,
                        'letter_grade': letter_grade,
                        'gpa': gpa
                    }
                    self.all_grades.append(grade_entry)
                    
                    # Display result
                    print("\n" + "="*65)
                    print(color + Colors.BOLD + f"   {emoji} RESULT: {letter_grade} - {message}" + Colors.ENDC)
                    print("="*65)
                    
                    self.display_advanced_visualization(grade, letter_grade)
                    
                    print(f"\n{Colors.OKGREEN}✓ Grade recorded successfully!{Colors.ENDC}")
                    
                    # Save to grade_history.txt
                    if self.save_grade_report(grade, letter_grade, gpa, name, subject):
                        print(f"{Colors.OKGREEN}✓ Grade saved to grade_history.txt!{Colors.ENDC}")
                
            elif choice == "2":
                self.display_analytics_dashboard()
                
            elif choice == "3":
                if self.all_grades:
                    filename = self.export_to_csv(self.all_grades)
                    if filename:
                        print(f"{Colors.OKGREEN}✓ Exported to {filename}{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}No grades to export.{Colors.ENDC}")
                    
            elif choice == "4":
                if self.all_grades:
                    filename = self.export_to_json(self.all_grades)
                    if filename:
                        print(f"{Colors.OKGREEN}✓ Exported to {filename}{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}No grades to export.{Colors.ENDC}")
                    
            elif choice == "5":
                if self.all_grades:
                    print("\n" + Colors.BOLD + "📋 ALL GRADES" + Colors.ENDC)
                    print("="*65)
                    for i, g in enumerate(self.all_grades, 1):
                        print(f"{i}. {g['name']} | {g['subject']} | Score: {g['score']:.1f} | Grade: {g['letter_grade']}")
                else:
                    print(f"{Colors.WARNING}No grades recorded yet.{Colors.ENDC}")
            
            elif choice == "6":
                # View grade history from file
                try:
                    with open("grade_history.txt", "r", encoding="utf-8") as f:
                        print("\n" + Colors.BOLD + "📚 GRADE HISTORY (from file)" + Colors.ENDC)
                        print("─" * 65)
                        print(f.read())
                        input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                except FileNotFoundError:
                    print(f"{Colors.WARNING}No grade history file found yet.{Colors.ENDC}")
                    input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                    
            elif choice == "7":
                self.all_grades.clear()
                self.print_banner()
                print(f"{Colors.OKGREEN}✓ Session cleared!{Colors.ENDC}")
                
            elif choice == "8":
                session_duration = datetime.now() - self.session_start
                print(f"\n{Colors.OKGREEN}Thank you for using Test Grader v12.0.0!{Colors.ENDC}")
                print(f"Session Duration: {session_duration}")
                print(f"Total Grades: {len(self.all_grades)}")
                print(f"{Colors.BOLD}Goodbye! 👋{Colors.ENDC}\n")
                break
            else:
                print(f"{Colors.WARNING}Invalid choice. Please try again.{Colors.ENDC}")

if __name__ == "__main__":
    grader = TestGraderV12()
    grader.run()