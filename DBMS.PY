import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# --- Database Setup ---
conn = sqlite3.connect('student_mgmt.db')
c = conn.cursor()

# Reset all tables
c.execute("DROP TABLE IF EXISTS marks")
c.execute("DROP TABLE IF EXISTS student_courses")
c.execute("DROP TABLE IF EXISTS courses")
c.execute("DROP TABLE IF EXISTS students")

# Create Students table (with 'semester' instead of 'class')
c.execute('''
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_no TEXT UNIQUE,
        name TEXT,
        age INTEGER,
        semester TEXT,
        address TEXT
    )
''')

# Create Courses table (generic names)
c.execute('''
    CREATE TABLE courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT UNIQUE
    )
''')
# Insert subjects dynamically as "Subject 1", "Subject 2", etc.
for i in range(1, 6):
    c.execute("INSERT INTO courses (course_name) VALUES (?)", (f"Subject {i}",))

# Create linking and marks tables
c.execute('''
    CREATE TABLE student_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(course_id) REFERENCES courses(course_id)
    )
''')

c.execute('''
    CREATE TABLE marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        mark INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        FOREIGN KEY(course_id) REFERENCES courses(course_id)
    )
''')

conn.commit()

# --- UI Setup ---
root = tk.Tk()
root.title("Student Management System")

# Input Fields
tk.Label(root, text="Enrollment No").grid(row=0, column=0)
enroll_entry = tk.Entry(root)
enroll_entry.grid(row=0, column=1)

tk.Label(root, text="Name").grid(row=1, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=1)

tk.Label(root, text="Age").grid(row=2, column=0)
age_entry = tk.Entry(root)
age_entry.grid(row=2, column=1)

tk.Label(root, text="Semester").grid(row=3, column=0)
semester_entry = tk.Entry(root)
semester_entry.grid(row=3, column=1)

tk.Label(root, text="Address").grid(row=4, column=0)
address_entry = tk.Entry(root)
address_entry.grid(row=4, column=1)

# Subject Name and Marks Fields (dynamic)
subject_entries = {}
for i in range(1, 6):
    tk.Label(root, text=f"Subject {i} Name").grid(row=5 + i, column=0)
    subject_name_entry = tk.Entry(root)
    subject_name_entry.grid(row=5 + i, column=1)
    
    tk.Label(root, text=f"Subject {i} Marks").grid(row=5 + i, column=2)
    subject_marks_entry = tk.Entry(root)
    subject_marks_entry.grid(row=5 + i, column=3)
    
    subject_entries[f"Subject {i}"] = (subject_name_entry, subject_marks_entry)

# Output box
output_text = tk.Text(root, width=100, height=15)
output_text.grid(row=12, column=0, columnspan=4, pady=10)

# --- Functions ---
def refresh_output():
    output_text.delete('1.0', tk.END)
    c.execute('''
        SELECT s.enrollment_no, s.name, s.age, s.semester, s.address,
               c.course_name, m.mark
        FROM students s
        LEFT JOIN student_courses sc ON s.student_id = sc.student_id
        LEFT JOIN courses c ON sc.course_id = c.course_id
        LEFT JOIN marks m ON m.student_id = s.student_id AND m.course_id = c.course_id
        ORDER BY s.enrollment_no, c.course_name
    ''')
    records = c.fetchall()

    current_enroll = None
    for r in records:
        if r[0] != current_enroll:
            output_text.insert(tk.END, f"\nEnrollment No: {r[0]} | Name: {r[1]} | Age: {r[2]} | Semester: {r[3]} | Address: {r[4]}\n")
            current_enroll = r[0]
        output_text.insert(tk.END, f"   - {r[5]}: {r[6]}\n")

def clear_inputs():
    enroll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    semester_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    for subject, (subject_name_entry, subject_marks_entry) in subject_entries.items():
        subject_name_entry.delete(0, tk.END)
        subject_marks_entry.delete(0, tk.END)

def submit_data():
    enrollment_no = enroll_entry.get()
    name = name_entry.get()
    age = age_entry.get()
    semester = semester_entry.get()
    address = address_entry.get()

    if not enrollment_no or not name:
        messagebox.showerror("Error", "Enrollment No and Name are required.")
        return

    try:
        c.execute("INSERT INTO students (enrollment_no, name, age, semester, address) VALUES (?, ?, ?, ?, ?)",
                  (enrollment_no, name, age, semester, address))
        student_id = c.lastrowid

        for subject, (subject_name_entry, subject_marks_entry) in subject_entries.items():
            subject_name = subject_name_entry.get()
            mark = subject_marks_entry.get()
            c.execute("SELECT course_id FROM courses WHERE course_name = ?", (subject,))
            course_id = c.fetchone()[0]
            c.execute("INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
            c.execute("INSERT INTO marks (student_id, course_id, mark) VALUES (?, ?, ?)",
                      (student_id, course_id, mark))
        conn.commit()
        refresh_output()
        clear_inputs()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Enrollment No must be unique.")

def delete_student():
    enrollment_no = simpledialog.askstring("Delete Student", "Enter Enrollment No to delete:")
    if not enrollment_no:
        return

    c.execute("SELECT student_id FROM students WHERE enrollment_no = ?", (enrollment_no,))
    result = c.fetchone()
    if result:
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete student {enrollment_no}?")
        if confirm:
            student_id = result[0]
            c.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
            c.execute("DELETE FROM student_courses WHERE student_id = ?", (student_id,))
            c.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            refresh_output()
            clear_inputs()
    else:
        messagebox.showerror("Error", "Student not found.")

def update_student():
    enrollment_no = simpledialog.askstring("Update Student", "Enter Enrollment No to update:")
    if not enrollment_no:
        return

    c.execute("SELECT * FROM students WHERE enrollment_no = ?", (enrollment_no,))
    student = c.fetchone()
    if student:
        # Pre-fill data into the fields
        enroll_entry.delete(0, tk.END)
        enroll_entry.insert(0, student[1])
        name_entry.delete(0, tk.END)
        name_entry.insert(0, student[2])
        age_entry.delete(0, tk.END)
        age_entry.insert(0, student[3])
        semester_entry.delete(0, tk.END)
        semester_entry.insert(0, student[4])
        address_entry.delete(0, tk.END)
        address_entry.insert(0, student[5])

        # After filling student data, allow the user to modify it
        def save_update():
            name = name_entry.get()
            age = age_entry.get()
            semester = semester_entry.get()
            address = address_entry.get()

            c.execute("UPDATE students SET name=?, age=?, semester=?, address=? WHERE enrollment_no=?",
                      (name, age, semester, address, enrollment_no))

            for i, (subject_name_entry, subject_marks_entry) in enumerate(subject_entries.values(), 1):
                mark = subject_marks_entry.get()
                c.execute("SELECT course_id FROM courses WHERE course_name = ?", (f"Subject {i}",))
                course_id = c.fetchone()[0]
                c.execute("UPDATE marks SET mark=? WHERE student_id = (SELECT student_id FROM students WHERE enrollment_no=?) AND course_id=?",
                          (mark, enrollment_no, course_id))

            conn.commit()
            refresh_output()
            clear_inputs()

        update_btn = tk.Button(root, text="Save Update", command=save_update)
        update_btn.grid(row=15, column=0, columnspan=2)

    else:
        messagebox.showerror("Error", "Student not found.")

# --- Buttons ---
tk.Button(root, text="Add Student", command=submit_data).grid(row=11, column=0, sticky='ew')
tk.Button(root, text="View Students", command=refresh_output).grid(row=11, column=1, sticky='ew')
tk.Button(root, text="Update Student", command=update_student).grid(row=13, column=0, sticky='ew')
tk.Button(root, text="Delete Student", command=delete_student).grid(row=13, column=1, sticky='ew')
tk.Button(root, text="Clear Fields", command=clear_inputs).grid(row=14, column=0, columnspan=2, sticky='ew')

# --- Run App ---
refresh_output()
root.mainloop()
