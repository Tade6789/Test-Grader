# Test Grader System

## Overview
This is a comprehensive Test Grading application with multiple versions and multi-port deployment. The project features:
- **Interactive menu system** for grading multiple tests
- **Built-in web servers** for grading (each version on dedicated ports)
- **Account servers** for user authentication (separate login servers for each version)
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
- **test grader V6.0.0.py** - Full-featured with visual feedback
- **test grader V2.4.12.py** - Input validation version
- **test grader V2.2.0.py** - Updated grading scale version
- **test grader v1.0.7.py** - Original basic version

### Web Server Versions (Built-In HTTP Servers - Grading Only)
- **test grader v10.0.0 server.py** - Web grader on port 5010 (file-based storage)
- **test grader v11.0.0 server.py** - Web grader on port 5011 (SQLite database)
- **test grader v12.0.0 server.py** - Web grader on port 5012 (CSV export)
- **test grader v13.0.0 server.py** - Web grader on port 5013 (JSON analytics)
- **test grader V6.0.0 server.py** - Web grader on port 5014 (visual feedback)
- **test grader V2.4.12 server.py** - Web grader on port 5015 (input validation)
- **test grader V2.2.0 server.py** - Web grader on port 5016 (updated scale)
- **test grader v 1.0.7 server.py** - Web grader on port 5017 (original)

### Account Servers (With User Authentication)
- **test grader v10.0.0 account server.py** - Login + grading on port 6010
- **test grader v11.0.0 account server.py** - Login + grading on port 6011
- **test grader v12.0.0 account server.py** - Login + grading on port 6012
- **test grader v13.0.0 account server.py** - Login + grading on port 6013

### Web Application (Main Replit Deployment)
- **wed_view.py** - Main Flask server (port 5000) - runs on replit with authentication
- **teacher.html** - Teacher console for grading students
- **auth.html** - Login/signup page
- **test.html** - Download page with all downloadable files and web servers
- **index.html** - Home page
- **grade_history.txt** - Automatically generated file storing all grades

## Recent Changes - Complete System Update (2025-11-25)
- ✅ Created 8 web grading servers (4 main versions + 4 earlier versions)
- ✅ Created 4 account servers with authentication (ports 6010-6013)
- ✅ All 20+ download buttons working with `/download/` endpoint
- ✅ File downloads with proper HTTP headers
- ✅ Complete multi-port deployment strategy
- ✅ Authentication system fully functional
- ✅ Production-ready and deployment-ready

## How to Use

### Option 1: Main Web Application (Replit Deployment)
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

### Option 2: Standalone Web Servers - Grading Only
Each version has a simple web grader (no authentication):

```bash
# Latest versions
python "test grader v10.0.0 server.py"   # Runs on http://localhost:5010
python "test grader v11.0.0 server.py"   # Runs on http://localhost:5011
python "test grader v12.0.0 server.py"   # Runs on http://localhost:5012
python "test grader v13.0.0 server.py"   # Runs on http://localhost:5013

# Earlier versions
python "test grader V6.0.0 server.py"    # Runs on http://localhost:5014
python "test grader V2.4.12 server.py"   # Runs on http://localhost:5015
python "test grader V2.2.0 server.py"    # Runs on http://localhost:5016
python "test grader v 1.0.7 server.py"   # Runs on http://localhost:5017
```

### Option 3: Account Servers - Grading With Authentication
Each version has an account server with login/signup:

```bash
# Account servers (user authentication included)
python "test grader v10.0.0 account server.py"   # Runs on http://localhost:6010
python "test grader v11.0.0 account server.py"   # Runs on http://localhost:6011
python "test grader v12.0.0 account server.py"   # Runs on http://localhost:6012
python "test grader v13.0.0 account server.py"   # Runs on http://localhost:6013
```

### Option 4: CLI Mode (Command-Line)
Run the original command-line versions:

```bash
python "test grader v10.0.0.py"  # Interactive menu system
python "test grader v11.0.0.py"  # Database edition
python "test grader v12.0.0.py"  # CSV export edition
python "test grader v13.0.0.py"  # Graphical charts edition
```

## Deployment Strategy

### Multi-Port Architecture
- **Port 5000** - Main Flask app with authentication (Replit)
- **Ports 5010-5017** - Grading-only web servers (8 versions)
- **Ports 6010-6013** - Account servers with login (4 versions)

### Local Development
Run multiple servers simultaneously on your local machine:

```bash
# Terminal 1 - Main app
python wed_view.py

# Terminal 2 - v10 account server
python "test grader v10.0.0 account server.py"

# Terminal 3 - v11 grader
python "test grader v11.0.0 server.py"

# Terminal 4 - CLI grader
python "test grader v10.0.0.py"
```

### GitHub Pages Deployment
All static files (HTML, CSS) are in the root directory and can be deployed to GitHub Pages.

### Replit Deployment
- Main Flask server runs on port 5000
- All web servers can run on separate ports
- Full authentication with secure session management

## Features by Version

### v10.0.0 - Ultimate Edition
- Interactive menu system (CLI)
- grade_history.txt file storage
- Color-coded output
- GPA calculator
- Session statistics
- Detailed feedback
- **Web server** (port 5010)
- **Account server** (port 6010)

### v11.0.0 - Database Edition
- SQLite database storage
- Advanced queries and statistics
- Student name and subject tracking
- **Web server** (port 5011)
- **Account server** (port 6011)

### v12.0.0 - Professional Plus
- CSV export functionality
- Advanced analytics
- Student information tracking
- **Web server** (port 5012)
- **Account server** (port 6012)

### v13.0.0 - Graphical Edition
- Matplotlib charts and graphs
- PDF export capability
- Multiple student tracking
- Weighted grade categories
- **Web server** (port 5013)
- **Account server** (port 6013)

### v6.0.0, v2.4.12, v2.2.0, v1.0.7
Each earlier version includes:
- Full-featured grading system
- **Web server** (grading only)
- **CLI interface**

## Authentication System

### Main Flask App (/auth)
1. **Sign Up** - Create account
2. **Log In** - Use credentials
3. **Version Code** - Enter access code
4. **Teacher Console** - Access grading interface

### Account Servers (Local)
1. **Sign Up** - Create account (email + password)
2. **Log In** - Use credentials
3. **Dashboard** - View user profile
4. **Grader** - Access grading interface

### Features
- Password hashing with werkzeug security
- Session-based authentication
- Email verification ready
- Secure storage

## File Downloads Available

**8 CLI Applications:**
- All versions available for download
- Proper HTTP headers for file downloads
- Security validation to prevent path traversal

**8 Web Servers (Grading Only):**
- v10-v13 on ports 5010-5013
- v6, v2.4.12, v2.2.0, v1.0.7 on ports 5014-5017

**4 Account Servers (With Login):**
- v10-v13 on ports 6010-6013

## Deployment

### Replit (Production)
Click **Publish** in Replit to deploy with a custom domain. Your app will be live at `https://your-custom-domain.replit.dev`

### GitHub/GitLab
1. Open **Git pane** (left sidebar)
2. Click **+** to stage all files
3. Enter commit message: `Complete Test Grader System - Multi-port Deployment`
4. Click **Commit**
5. Click **Push** to GitHub or GitLab

## Technology Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (optional)
- **Authentication:** Flask-Login, werkzeug security
- **Styling:** CSS with responsive design
- **Storage:** File-based, Database, CSV, JSON
- **Deployment:** Replit (Backend) + GitHub Pages (Static Files)

## Status: PRODUCTION READY ✅
- All servers configured and tested
- Multiple deployment options available
- Complete file download system
- User authentication working
- Ready for GitHub/GitLab push
- Ready for Replit publish
