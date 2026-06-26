# 🎓 Smart Attendance Assistant

A comprehensive full-stack web application designed for educational institutions to automate attendance logging, leave processing, and real-time monitoring. Built during my 2-month On-the-Job Training (OJT).

## 🚀 System Roles & Features
- **Student Portal:** View period-by-period attendance logs and submit On-Duty (OD)/Leave applications.
- **Teacher Portal:** Mark hourly classroom attendance logs and approve/reject pending student requests.
- **Admin Console:** Add/register new student and faculty profiles and access a live master log monitor.

## 🛠️ Technology Stack
- **Frontend:** HTML5, CSS3 (Custom Responsive Layouts with Glassmorphic Elements)
- **Backend:** Python 3.12, Flask Framework
- **Database:** SQLite3 Relational Database Engine

## ⚙️ Installation & Setup
1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Initialize the database schema and mock records:
   ```bash
   python init_db.py
   ```
3. Run the development application server:
   ```bash
   python app.py
   ```
4. Access the web interface at `http://127.0.0`
