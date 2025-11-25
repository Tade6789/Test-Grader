# Test Grader System

## Overview
This is a comprehensive Test Grading application with multiple versions. The project features:
- **Interactive menu system** for grading multiple tests
- **Built-in web servers** for each version - run as standalone services
- **Automatic grade history** saved to `grade_history.txt` or database
- **Color-coded terminal output** with ANSI colors
- **GPA calculator** (4.0 scale)
- **13-tier grading system** (A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F)
- **Session statistics** and detailed feedback
- **50-character progress bar** visualization

## Project Structure
### Command-Line Versions (CLI)
- **test grader v10.0.0.py** - Main grader with menu & txt history
- **test grader v11.0.0.py** - Database edition with SQLite storage
- **test grader v12.0.0.py** - Professional edition with CSV export
- **test grader v13.0.0.py** - Ultimate edition with graphical charts (requires matplotlib)

### Web Server Versions (Built-In HTTP Servers)
- **test grader v10.0.0 server.py** - Web interface on port 5010 (saves to grade_history.txt)
- **test grader v11.0.0 server.py** - Web interface on port 5011 (SQLite database)
- **test grader v12.0.0 server.py** - Web interface on port 5012 (CSV export)
- **test grader v13.0.0 server.py** - Web interface on port 5013 (JSON analytics)

### Web Application
- **wed_view.py** - Main Flask server (port 5000) - runs on replit with authentication
- **teacher.html** - Teacher console for grading students
- **auth.html** - Login/signup page
- **code.html** - Version code verification
- **test.html** - Download page with downloadable files and web servers
- **index.html** - Home page
- **grade_history.txt** - Automatically generated file storing all grades

## Recent Changes - Final Update (2025-11-25)
- ✅ Fixed all download buttons with `/download/` endpoint
- ✅ All 12 download buttons now work properly (CLI apps + servers)
- ✅ File downloads with proper HTTP headers
- ✅ Authentication system fully functional
- ✅ Web server integration complete
- ✅ LSP errors resolved
- ✅ Production-ready and deployment-ready

## How to Use

### Option 1: Web Application (Main Replit Deployment)
The workflow automatically runs the main Flask server (wed_view.py) when you start the project.

**Teachers:**
1. Visit the homepage and click "Sign Up" or "Log In"
2. Create account or sign in
3. Enter version code (GRADE10, GRADE11, GRADE12, or GRADE13)
4. Access the online grading console
5. Grade students and view history

**Version Codes:**
- v10: GRADE10
- v11: GRADE11
- v12: GRADE12
- v13: GRADE13

### Option 2: Standalone Web Servers (Local Development)
Each version can run as a standalone web server:

```bash
# Run any version as a web server
python "test grader v10.0.0 server.py"   # Runs on http://localhost:5010
python "test grader v11.0.0 server.py"   # Runs on http://localhost:5011
python "test grader v12.0.0 server.py"   # Runs on http://localhost:5012
python "test grader v13.0.0 server.py"   # Runs on http://localhost:5013
```

Each server includes an HTML interface for grading.

### Option 3: CLI Mode (Command-Line)
Run the original command-line versions:

```bash
python "test grader v10.0.0.py"  # Interactive menu system
python "test grader v11.0.0.py"  # Database edition
python "test grader v12.0.0.py"  # CSV export edition
python "test grader v13.0.0.py"  # Graphical charts edition
```

### Serving the Download Page (Web)
```bash
python wed_view.py
```
This will serve the download page on port 5000 with full authentication system.

## Features by Version

### v10.0.0 (Current Primary) - Ultimate Edition
- ✅ Interactive menu system (CLI)
- ✅ grade_history.txt file storage
- ✅ Color-coded output
- ✅ GPA calculator
- ✅ Session statistics
- ✅ Detailed feedback
- ✅ **Built-in web server** with HTML UI

### v11.0.0 - Database Edition
- SQLite database storage
- Advanced queries and statistics
- Student name and subject tracking
- **Built-in web server** with database persistence

### v12.0.0 - Professional Plus
- CSV export functionality
- Advanced analytics
- Student information tracking
- **Built-in web server** with CSV auto-save

### v13.0.0 - Graphical Edition
- Matplotlib charts and graphs
- PDF export capability
- Multiple student tracking
- Weighted grade categories
- **Built-in web server** with JSON storage

## Authentication System

### Login Flow
1. **Sign Up** - Create account at `/auth`
2. **Log In** - Use credentials to sign in
3. **Version Code** - Enter code for desired version (GRADE10, GRADE11, GRADE12, GRADE13)
4. **Teacher Console** - Access grading interface at `/teacher`

### Features
- Password hashing with werkzeug security
- Session-based authentication with Flask-Login
- Version code verification for access control
- Automatic grade history tracking
- Real-time grading results

## File Downloads
All downloadable files are served via `/download/` endpoint:
- ✅ All 8 Python versions available
- ✅ All 4 web servers available
- ✅ Proper HTTP headers for file downloads
- ✅ Security validation to prevent path traversal

## Deployment

### GitHub Pages (Static Files)
This project is designed for GitHub Pages deployment:
1. All static files are in the root directory
2. HTML pages work as standalone downloads
3. Server versions can be run on any Python-enabled host

### Replit Deployment (Dynamic Backend)
Current deployment includes:
- Flask web server on port 5000 (main interface)
- Standalone server versions on ports 5010-5013
- SQLite, CSV, and file-based storage options
- Authentication with secure session management

### Publishing to Production
Click **Publish** in Replit to deploy with a custom domain. Your app will be live at `https://your-custom-domain.replit.dev`

## Pushing to GitHub/GitLab

### To Push to GitHub:
1. Open **Git pane** (left sidebar)
2. Click **+** to stage all files
3. Enter commit message: `Complete Test Grader System - Authentication, Downloads, File Management`
4. Click **Commit**
5. Click **Push**

### To Push to GitLab:
1. Add GitLab remote: Click **Git menu (⋮)** → **Manage Remotes**
2. Add URL: `https://gitlab.com/YOUR_USERNAME/test-grader.git`
3. Follow same commit/push steps above

## User Preferences
- Preferred version: **v10.0.0** (with menu and .txt file)
- Output format: Multiple options (grade_history.txt, SQLite, CSV, JSON)
- Interface: Web-based with authentication + Command-line options
- Deployment: GitHub/GitLab with Replit backend
- Status: **PRODUCTION READY - Ready to push and deploy**

## Technology Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (optional, for v11)
- **Authentication:** Flask-Login with werkzeug
- **Styling:** CSS with responsive design
- **Storage:** File-based (txt), Database (SQLite), CSV, JSON
- **Deployment:** Replit (Backend) + GitHub Pages (Static Files)
