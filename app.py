from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

# Required for using sessions to securely track who is logged into the application
app.secret_key = 'ojt_secret_key_attendance_assistant'

# Helper function to quickly establish a connection to your local database file
def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row  # Enables column fetching by row names
    return conn

# ==============================================================================
# 1. GLOBAL ROOT ROUTE
# ==============================================================================
@app.route('/')
def home():
    # Renders the clean 3-button block portal selection home screen
    return render_template('portal_selection.html')


# ==============================================================================
# 2. STUDENT SYSTEM MODULE
# ==============================================================================
@app.route('/login/student')
def login_student_page():
    return render_template('login_student.html')

@app.route('/auth/student', methods=['POST'])
def auth_student():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ? AND password = ?', 
                           (username, password)).fetchone()
    conn.close()
    
    if student:
        session['user_id'] = student['id']
        session['user_name'] = student['name']
        session['role'] = 'student'
        return redirect(url_for('student_dashboard'))
    else:
        return "<h3>Invalid Student ID or Password. <a href='/login/student'>Go Back</a></h3>", 401

@app.route('/dashboard/student')
def student_dashboard():
    # Security checkpoint check
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('home'))
        
    student_id = session['user_id']
    conn = get_db_connection()
    
    student_data = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    attendance_records = conn.execute('SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC, period ASC', (student_id,)).fetchall()
    leave_records = conn.execute('SELECT * FROM leave_requests WHERE student_id = ? ORDER BY id DESC', (student_id,)).fetchall()
    conn.close()
    
    return render_template('student_dashboard.html', student=student_data, attendance=attendance_records, leaves=leave_records)

@app.route('/request/submit', methods=['POST'])
def submit_request():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('home'))
        
    student_id = session['user_id']
    request_type = request.form.get('request_type') # 'Leave Letter' or 'OD'
    reason = request.form.get('reason')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO leave_requests (student_id, type, reason, status) VALUES (?, ?, ?, ?)',
                 (student_id, request_type, reason, 'Pending'))
    conn.commit()
    conn.close()
    return redirect(url_for('student_dashboard'))


# ==============================================================================
# 3. TEACHER SYSTEM MODULE
# ==============================================================================
@app.route('/login/teacher')
def login_teacher_page():
    return render_template('login_teacher.html')

@app.route('/auth/teacher', methods=['POST'])
def auth_teacher():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    teacher = conn.execute('SELECT * FROM teachers WHERE id = ? AND password = ?', 
                           (username, password)).fetchone()
    conn.close()
    
    if teacher:
        session['user_id'] = teacher['id']
        session['user_name'] = teacher['name']
        session['role'] = 'teacher'
        return redirect(url_for('teacher_dashboard'))
    else:
        return "<h3>Invalid Teacher ID or Password. <a href='/login/teacher'>Go Back</a></h3>", 401

@app.route('/dashboard/teacher')
def teacher_dashboard():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    all_students = conn.execute('SELECT * FROM students').fetchall()
    pending_requests = conn.execute('''
        SELECT leave_requests.*, students.name 
        FROM leave_requests 
        JOIN students ON leave_requests.student_id = students.id
        WHERE leave_requests.status = 'Pending'
    ''').fetchall()
    conn.close()
    
    return render_template('teacher_dashboard.html', teacher_name=session['user_name'], students=all_students, requests=pending_requests)

@app.route('/attendance/submit', methods=['POST'])
def submit_attendance():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('home'))
        
    date = request.form.get('date')
    period = request.form.get('period')
    teacher_id = session['user_id']
    
    conn = get_db_connection()
    all_students = conn.execute('SELECT id FROM students').fetchall()
    
    for student in all_students:
        # Dynamically pulls status matching the unique radio group name for each student ID
        status = request.form.get(f'status_{student["id"]}')
        if status:
            conn.execute('''
                INSERT INTO attendance (student_id, date, period, status, marked_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (student['id'], date, period, status, teacher_id))
            
    conn.commit()
    conn.close()
    return "<h3>Attendance Logged Successfully! <a href='/dashboard/teacher'>Return to Control Panel</a></h3>"

@app.route('/request/action/<int:request_id>/<string:action_status>')
def process_request(request_id, action_status):
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    conn.execute('UPDATE leave_requests SET status = ? WHERE id = ?', (action_status, request_id))
    conn.commit()
    conn.close()
    return redirect(url_for('teacher_dashboard'))


# ==============================================================================
# 4. ADMIN SYSTEM MODULE
# ==============================================================================
@app.route('/login/admin')
def login_admin_page():
    return render_template('login_admin.html')

@app.route('/auth/admin', methods=['POST'])
def auth_admin():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM admins WHERE id = ? AND password = ?', 
                           (username, password)).fetchone()
    conn.close()
    
    if admin:
        session['user_id'] = admin['id']
        session['user_name'] = admin['username']
        session['role'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    else:
        return "<h3>Invalid Admin Credentials. <a href='/login/admin'>Go Back</a></h3>", 401

@app.route('/dashboard/admin')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    all_students = conn.execute('SELECT * FROM students').fetchall()
    all_teachers = conn.execute('SELECT * FROM teachers').fetchall()
    
    # Master System monitor join log query
    attendance_logs = conn.execute('''
        SELECT attendance.*, students.name AS student_name, teachers.name AS teacher_name
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        JOIN teachers ON attendance.marked_by = teachers.id
        ORDER BY attendance.date DESC, attendance.period ASC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                           admin_name=session['user_name'],
                           students=all_students, 
                           teachers=all_teachers,
                           logs=attendance_logs)

@app.route('/admin/add_user', methods=['POST'])
def admin_add_user():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
        
    user_type = request.form.get('user_type') # 'student' or 'teacher'
    user_id = request.form.get('user_id')
    user_name = request.form.get('user_name')
    user_password = request.form.get('user_password')
    
    conn = get_db_connection()
    if user_type == 'student':
        conn.execute('INSERT INTO students (id, name, password) VALUES (?, ?, ?)', (user_id, user_name, user_password))
    elif user_type == 'teacher':
        conn.execute('INSERT INTO teachers (id, name, password) VALUES (?, ?, ?)', (user_id, user_name, user_password))
        
    conn.commit()
    conn.close()
    return "<h3>User Profile Added Successfully! <a href='/dashboard/admin'>Return to Admin Panel</a></h3>"


# ==============================================================================
# 5. GLOBAL LOGOUT UTILITY
# ==============================================================================
@app.route('/logout')
def logout():
    session.clear() # Destroys current session cookies completely
    return redirect(url_for('home'))


if __name__ == '__main__':
    # Launches your local development server with live reload tracking enabled
    app.run(debug=True)
