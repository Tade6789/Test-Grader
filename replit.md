# Test Grader System

## Overview
This is a comprehensive Test Grading application with multiple versions. The project currently runs **Test Grader v10.0.0** which features:
- Interactive menu system for grading multiple tests
- Automatic grade history saved to `grade_history.txt`
- Color-coded terminal output with ANSI colors
- GPA calculator (4.0 scale)
- 13-tier grading system (A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F)
- Session statistics and detailed feedback
- 50-character progress bar visualization

## Project Structure
- **test grader v10.0.0.py** - Main grader (currently active with menu & txt history)
- **test grader v11.0.0.py** - Database edition with SQLite storage
- **test grader v12.0.0.py** - Professional edition with CSV export
- **test grader v13.0.0.py** - Ultimate edition with graphical charts (requires matplotlib)
- **test.html** - Download page for all versions
- **wed_view.py** - Simple HTTP server to serve the download page
- **grade_history.txt** - Automatically generated file storing all graded tests
- **requirements.txt** - Python dependencies (matplotlib, numpy)

## Recent Changes
- **2025-11-12**: Initial Replit setup
  - Installed Python 3.11 and dependencies
  - Fixed matplotlib imports in v13.0.0
  - Updated wed_view.py to use port 5000 and 0.0.0.0 binding
  - Configured workflow to run Test Grader v10.0.0 with interactive menu
  - Created documentation and .gitignore

## How to Use

### Running the Test Grader (Current Default)
The workflow automatically runs v10.0.0 when you start the project. You'll see a menu with options:
1. Grade a new test
2. View grading scale
3. View grade history (from grade_history.txt)
4. Exit

### Running Different Versions
To run a different version manually:
```bash
python "test grader v11.0.0.py"  # Database edition
python "test grader v12.0.0.py"  # CSV export edition
python "test grader v13.0.0.py"  # Graphical charts edition
```

### Serving the Download Page
To start the web server for the HTML download page:
```bash
python wed_view.py
```
This will serve the download page on port 5000.

## Features by Version

### v10.0.0 (Current) - Ultimate Edition
- ✅ Interactive menu system
- ✅ grade_history.txt file storage
- ✅ Color-coded output
- ✅ GPA calculator
- ✅ Session statistics
- ✅ Detailed feedback

### v11.0.0 - Database Edition
- SQLite database storage
- Advanced queries and statistics
- Student name and subject tracking

### v12.0.0 - Professional Plus
- CSV export functionality
- Advanced analytics
- Student information tracking

### v13.0.0 - Graphical Edition
- Matplotlib charts and graphs
- PDF export capability
- Multiple student tracking
- Weighted grade categories

## User Preferences
- Preferred version: **v10.0.0** (with menu and .txt file)
- Output format: grade_history.txt for persistent storage
- Interface: Command-line menu system
