"""
Grade Calculator v13.0.0
Advanced Features: Graphical reporting, multiple students, weighted categories, PDF reports
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple # type: ignore
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages 

class GradeCategory:
    """Represents a grading category with weight"""
    def __init__(self, name: str, weight: float):
        self.name = name
        self.weight = weight
        self.assignments = []
    
    def add_assignment(self, name: str, score: float, max_score: float):
        """Add an assignment to this category"""
        self.assignments.append({
            'name': name,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100
        })
    
    def get_category_average(self) -> float:
        """Calculate average for this category"""
        if not self.assignments:
            return 0.0
        total_percentage = sum(a['percentage'] for a in self.assignments)
        return total_percentage / len(self.assignments)

class Student:
    """Represents a student with their grades"""
    def __init__(self, name: str, student_id: str):
        self.name = name
        self.student_id = student_id
        self.categories: Dict[str, GradeCategory] = {}
    
    def add_category(self, category: GradeCategory):
        """Add a grading category"""
        self.categories[category.name] = category
    
    def calculate_final_grade(self) -> float:
        """Calculate weighted final grade"""
        total_weight = sum(cat.weight for cat in self.categories.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            cat.get_category_average() * cat.weight 
            for cat in self.categories.values()
        )
        return weighted_sum / total_weight
    
    def get_letter_grade(self) -> str:
        """Convert numerical grade to letter grade"""
        grade = self.calculate_final_grade()
        if grade >= 93: return 'A'
        elif grade >= 90: return 'A-'
        elif grade >= 87: return 'B+'
        elif grade >= 83: return 'B'
        elif grade >= 80: return 'B-'
        elif grade >= 77: return 'C+'
        elif grade >= 73: return 'C'
        elif grade >= 70: return 'C-'
        elif grade >= 67: return 'D+'
        elif grade >= 63: return 'D'
        elif grade >= 60: return 'D-'
        else: return 'F'

class GradeCalculator:
    """Main grade calculator with reporting features"""
    def __init__(self, course_name: str):
        self.course_name = course_name
        self.students: Dict[str, Student] = {}
        self.data_file = f"{course_name.replace(' ', '_')}_grades.json"
    
    def add_student(self, student: Student):
        """Add a student to the course"""
        self.students[student.student_id] = student
    
    def generate_student_report(self, student_id: str) -> str:
        """Generate text report for a student"""
        if student_id not in self.students:
            return "Student not found"
        
        student = self.students[student_id]
        final_grade = student.calculate_final_grade()
        letter = student.get_letter_grade()
        
        report = f"\n{'='*60}\n"
        report += f"GRADE REPORT - {self.course_name}\n"
        report += f"{'='*60}\n"
        report += f"Student: {student.name} (ID: {student.student_id})\n"
        report += f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*60}\n\n"
        
        # Category breakdown
        for cat_name, category in student.categories.items():
            avg = category.get_category_average()
            report += f"{cat_name} (Weight: {category.weight}%)\n"
            report += f"  Category Average: {avg:.2f}%\n"
            
            for assignment in category.assignments:
                report += f"    - {assignment['name']}: {assignment['score']}/{assignment['max_score']} "
                report += f"({assignment['percentage']:.2f}%)\n"
            report += "\n"
        
        report += f"{'='*60}\n"
        report += f"FINAL GRADE: {final_grade:.2f}% ({letter})\n"
        report += f"{'='*60}\n"
        
        return report
    
    def plot_student_performance(self, student_id: str, save_path: str = None):
        """Create visual charts for student performance"""
        if student_id not in self.students:
            print("Student not found")
            return
        
        student = self.students[student_id]
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Grade Report: {student.name} - {self.course_name}', 
                     fontsize=16, fontweight='bold')
        
        # 1. Category Averages Bar Chart
        categories = list(student.categories.keys())
        averages = [cat.get_category_average() for cat in student.categories.values()]
        weights = [cat.weight for cat in student.categories.values()]
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))
        bars = ax1.bar(categories, averages, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Average (%)', fontsize=12)
        ax1.set_title('Category Averages', fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 100)
        ax1.axhline(y=70, color='r', linestyle='--', label='Passing (70%)')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        # 2. Weighted Contribution Pie Chart
        final_grade = student.calculate_final_grade()
        contributions = [
            (cat.get_category_average() * cat.weight / 100) 
            for cat in student.categories.values()
        ]
        
        ax2.pie(contributions, labels=categories, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax2.set_title(f'Grade Contribution\nFinal: {final_grade:.2f}% ({student.get_letter_grade()})',
                     fontsize=14, fontweight='bold')
        
        # 3. Assignment Scores Timeline
        all_assignments = []
        for cat_name, category in student.categories.items():
            for i, assignment in enumerate(category.assignments):
                all_assignments.append({
                    'name': f"{cat_name[:3]}-{assignment['name'][:10]}",
                    'percentage': assignment['percentage'],
                    'category': cat_name
                })
        
        if all_assignments:
            x_pos = range(len(all_assignments))
            percentages = [a['percentage'] for a in all_assignments]
            labels = [a['name'] for a in all_assignments]
            
            ax3.plot(x_pos, percentages, marker='o', linewidth=2, markersize=8)
            ax3.axhline(y=final_grade, color='g', linestyle='--', 
                       label=f'Final Average ({final_grade:.1f}%)')
            ax3.axhline(y=70, color='r', linestyle='--', label='Passing (70%)')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax3.set_ylabel('Score (%)', fontsize=12)
            ax3.set_title('Assignment Performance Timeline', fontsize=14, fontweight='bold')
            ax3.set_ylim(0, 100)
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Grade Distribution (if comparing to class)
        letter_grade = student.get_letter_grade()
        grade_labels = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
        student_index = grade_labels.index(letter_grade)
        
        # Create a mock distribution highlighting student's position
        distribution = [0] * len(grade_labels)
        distribution[student_index] = 1
        
        colors_dist = ['lightgray'] * len(grade_labels)
        colors_dist[student_index] = 'gold'
        
        ax4.bar(grade_labels, distribution, color=colors_dist, edgecolor='black')
        ax4.set_ylabel('Student Position', fontsize=12)
        ax4.set_title(f'Current Letter Grade: {letter_grade}', 
                     fontsize=14, fontweight='bold')
        ax4.set_ylim(0, 1.5)
        ax4.text(student_index, 1.1, 'YOU ARE HERE', ha='center', 
                fontsize=12, fontweight='bold', color='darkred')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        else:
            plt.show()
    
    def generate_class_report(self):
        """Generate class-wide statistics"""
        if not self.students:
            print("No students in the course")
            return
        
        grades = [s.calculate_final_grade() for s in self.students.values()]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Class Report: {self.course_name}', fontsize=16, fontweight='bold')
        
        # 1. Grade Distribution Histogram
        ax1.hist(grades, bins=10, color='steelblue', edgecolor='black', alpha=0.7)
        ax1.axvline(np.mean(grades), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(grades):.2f}%')
        ax1.set_xlabel('Grade (%)', fontsize=12)
        ax1.set_ylabel('Number of Students', fontsize=12)
        ax1.set_title('Grade Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Letter Grade Distribution
        letter_grades = [s.get_letter_grade() for s in self.students.values()]
        grade_counts = {}
        for lg in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']:
            grade_counts[lg] = letter_grades.count(lg)
        
        ax2.bar(grade_counts.keys(), grade_counts.values(), 
               color='lightcoral', edgecolor='black')
        ax2.set_ylabel('Number of Students', fontsize=12)
        ax2.set_title('Letter Grade Distribution', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Box Plot
        ax3.boxplot(grades, vert=True)
        ax3.set_ylabel('Grade (%)', fontsize=12)
        ax3.set_title('Grade Statistics (Box Plot)', fontsize=14, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Statistics Summary
        ax4.axis('off')
        stats_text = f"""
        CLASS STATISTICS
        ═══════════════════════════════
        
        Total Students: {len(self.students)}
        
        Mean Grade: {np.mean(grades):.2f}%
        Median Grade: {np.median(grades):.2f}%
        Std Deviation: {np.std(grades):.2f}%
        
        Highest Grade: {np.max(grades):.2f}%
        Lowest Grade: {np.min(grades):.2f}%
        
        Passing Rate: {sum(1 for g in grades if g >= 70)/len(grades)*100:.1f}%
        """
        ax4.text(0.1, 0.5, stats_text, fontsize=12, family='monospace',
                verticalalignment='center')
        
        plt.tight_layout()
        plt.show()
    
    def export_to_pdf(self, student_id: str, filename: str = None):
        """Export student report to PDF"""
        if student_id not in self.students:
            print("Student not found")
            return
        
        if filename is None:
            filename = f"{self.students[student_id].name.replace(' ', '_')}_report.pdf"
        
        with PdfPages(filename) as pdf:
            # Create the plot
            self.plot_student_performance(student_id, save_path=None)
            pdf.savefig()
            plt.close()
            
            # Add metadata
            d = pdf.infodict()
            d['Title'] = f'Grade Report - {self.students[student_id].name}'
            d['Author'] = 'Grade Calculator v13.0.0'
            d['Subject'] = self.course_name
            d['Keywords'] = 'Grades, Report, Education'
            d['CreationDate'] = datetime.now()
        
        print(f"PDF report saved to {filename}")
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            'course_name': self.course_name,
            'students': {}
        }
        
        for student_id, student in self.students.items():
            student_data = {
                'name': student.name,
                'categories': {}
            }
            
            for cat_name, category in student.categories.items():
                student_data['categories'][cat_name] = {
                    'weight': category.weight,
                    'assignments': category.assignments
                }
            
            data['students'][student_id] = student_data
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {self.data_file}")
    
    def load_data(self):
        """Load data from JSON file"""
        if not os.path.exists(self.data_file):
            print("No saved data found")
            return
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        for student_id, student_data in data['students'].items():
            student = Student(student_data['name'], student_id)
            
            for cat_name, cat_data in student_data['categories'].items():
                category = GradeCategory(cat_name, cat_data['weight'])
                for assignment in cat_data['assignments']:
                    category.add_assignment(
                        assignment['name'],
                        assignment['score'],
                        assignment['max_score']
                    )
                student.add_category(category)
            
            self.add_student(student)
        
        print(f"Data loaded from {self.data_file}")

def demo_version_13():
    """Demo of version 13.0.0 features"""
    print("="*60)
    print("GRADE CALCULATOR v13.0.0 - DEMO")
    print("="*60)
    
    # Create course
    calc = GradeCalculator("Introduction to Python Programming")
    
    # Create students
    student1 = Student("Alice Johnson", "S001")
    student2 = Student("Bob Smith", "S002")
    student3 = Student("Carol White", "S003")
    
    # Add categories for each student
    for student in [student1, student2, student3]:
        # Homework (30%)
        homework = GradeCategory("Homework", 30)
        homework.add_assignment("HW1", 95, 100)
        homework.add_assignment("HW2", 88, 100)
        homework.add_assignment("HW3", 92, 100)
        student.add_category(homework)
        
        # Quizzes (20%)
        quizzes = GradeCategory("Quizzes", 20)
        quizzes.add_assignment("Quiz1", 85, 100)
        quizzes.add_assignment("Quiz2", 90, 100)
        student.add_category(quizzes)
        
        # Midterm (25%)
        midterm = GradeCategory("Midterm", 25)
        if student.name == "Alice Johnson":
            midterm.add_assignment("Midterm Exam", 95, 100)
        elif student.name == "Bob Smith":
            midterm.add_assignment("Midterm Exam", 78, 100)
        else:
            midterm.add_assignment("Midterm Exam", 88, 100)
        student.add_category(midterm)
        
        # Final (25%)
        final = GradeCategory("Final", 25)
        if student.name == "Alice Johnson":
            final.add_assignment("Final Exam", 92, 100)
        elif student.name == "Bob Smith":
            final.add_assignment("Final Exam", 82, 100)
        else:
            final.add_assignment("Final Exam", 85, 100)
        student.add_category(final)
        
        calc.add_student(student)
    
    # Generate reports
    print("\n1. Text Report for Alice Johnson:")
    print(calc.generate_student_report("S001"))
    
    print("\n2. Generating visual report for Alice Johnson...")
    calc.plot_student_performance("S001")
    
    print("\n3. Generating class report...")
    calc.generate_class_report()
    
    print("\n4. Exporting PDF report for Alice Johnson...")
    calc.export_to_pdf("S001", "Alice_Johnson_report.pdf")
    
    print("\n5. Saving all data...")
    calc.save_data()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)

if __name__ == "__main__":
    demo_version_13()