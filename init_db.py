import sqlite3

def initialize_database():
    # 1. Connect to the database file (creates it if it doesn't exist)
    connection = sqlite3.connect('attendance.db')
    cursor = connection.cursor()

    print("Creating database tables...")

    # 2. Create the Users/Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 3. Create the Teachers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 4. Create the Admins Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 5. Create the Attendance Records Table (Period by Period)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            period TEXT NOT NULL,
            status TEXT NOT NULL, -- 'Present' or 'Absent'
            marked_by TEXT NOT NULL, -- Teacher's ID
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 6. Create the Leave & OD (On-Duty) Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            type TEXT NOT NULL, -- 'Leave Letter' or 'OD'
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # 7. Insert Mock Data so we can test logins immediately
    # INSERT OR IGNORE avoids throwing errors if the data already exists
    cursor.execute("INSERT OR IGNORE INTO students VALUES ('STU101', 'Alan Das', 'stu123')")
    cursor.execute("INSERT OR IGNORE INTO teachers VALUES ('TCH501', 'Mr. Robert', 'tch123')")
    cursor.execute("INSERT OR IGNORE INTO admins VALUES ('ADM001', 'System Admin', 'admin123')")

    # Save changes and close the connection
    connection.commit()
    connection.close()
    print("Database initialization completely successful!")

if __name__ == '__main__':
    initialize_database()
