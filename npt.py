import sqlite3
import tkinter as tk
from tkinter import messagebox

# Database Setup
conn = sqlite3.connect('student_management.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
                        student_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        dob TEXT,
                        gender TEXT,
                        department TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Courses (
                        course_id INTEGER PRIMARY KEY,
                        course_name TEXT,
                        department TEXT,
                        credits INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Enrollments (
                        student_id INTEGER,
                        course_id INTEGER,
                        semester TEXT,
                        PRIMARY KEY (student_id, course_id),
                        FOREIGN KEY (student_id) REFERENCES Students(student_id),
                        FOREIGN KEY (course_id) REFERENCES Courses(course_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Marks (
                        student_id INTEGER,
                        course_id INTEGER,
                        marks_obtained INTEGER,
                        grade TEXT,
                        FOREIGN KEY (student_id) REFERENCES Students(student_id),
                        FOREIGN KEY (course_id) REFERENCES Courses(course_id))''')
    conn.commit()

create_tables()

# GUI Setup
root = tk.Tk()
root.title("Student Management System")
root.geometry("700x600")

# Frame for dynamic content
content_frame = tk.Frame(root)
content_frame.pack(pady=10)

# Clear Frame function to clear previous widgets
def clear_frame():
    for widget in content_frame.winfo_children():
        widget.destroy()

# Add Student Form
def add_student_form():
    clear_frame()
    tk.Label(content_frame, text="Add Student", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)
    
    student_labels = ["Student ID", "First Name", "Last Name", "DOB (YYYY-MM-DD)", "Gender", "Department"]
    student_entries = []
    
    for idx, label in enumerate(student_labels):
        tk.Label(content_frame, text=label).grid(row=idx+1, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(content_frame, width=30)
        entry.grid(row=idx+1, column=1, padx=10, pady=5)
        student_entries.append(entry)
    
    def add_student():
        data = [e.get().strip() for e in student_entries]
        try:
            cursor.execute("INSERT INTO Students VALUES (?, ?, ?, ?, ?, ?)", data)
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    tk.Button(content_frame, text="Add Student", command=add_student).grid(row=len(student_labels)+1, columnspan=2, pady=10)

# Add Course Form
def add_course_form():
    clear_frame()
    tk.Label(content_frame, text="Add Course", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)

    course_labels = ["Course ID", "Course Name", "Department", "Credits"]
    course_entries = []

    for idx, label in enumerate(course_labels):
        tk.Label(content_frame, text=label).grid(row=idx+1, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(content_frame, width=30)
        entry.grid(row=idx+1, column=1, padx=10, pady=5)
        course_entries.append(entry)

    def add_course():
        data = [e.get().strip() for e in course_entries]
        try:
            cursor.execute("INSERT INTO Courses VALUES (?, ?, ?, ?)", data)
            conn.commit()
            messagebox.showinfo("Success", "Course added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Course ID already exists.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(content_frame, text="Add Course", command=add_course).grid(row=len(course_labels)+1, columnspan=2, pady=10)

# Enroll Student Form
def enroll_student_form():
    clear_frame()
    tk.Label(content_frame, text="Enroll Student", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)

    tk.Label(content_frame, text="Student ID").grid(row=1, column=0, padx=10, pady=5)
    enroll_student_id = tk.Entry(content_frame, width=30)
    enroll_student_id.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Course ID").grid(row=2, column=0, padx=10, pady=5)
    enroll_course_id = tk.Entry(content_frame, width=30)
    enroll_course_id.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Semester").grid(row=3, column=0, padx=10, pady=5)
    enroll_semester = tk.Entry(content_frame, width=30)
    enroll_semester.grid(row=3, column=1, padx=10, pady=5)

    def enroll_student():
        try:
            cursor.execute("INSERT INTO Enrollments VALUES (?, ?, ?)", (
                enroll_student_id.get().strip(),
                enroll_course_id.get().strip(),
                enroll_semester.get().strip()
            ))
            conn.commit()
            messagebox.showinfo("Success", "Student enrolled successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Enrollment already exists.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(content_frame, text="Enroll Student", command=enroll_student).grid(row=4, columnspan=2, pady=10)

# Add Marks Form
def add_marks_form():
    clear_frame()
    tk.Label(content_frame, text="Add Marks", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)

    tk.Label(content_frame, text="Student ID").grid(row=1, column=0, padx=10, pady=5)
    marks_student_id = tk.Entry(content_frame, width=30)
    marks_student_id.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Course ID").grid(row=2, column=0, padx=10, pady=5)
    marks_course_id = tk.Entry(content_frame, width=30)
    marks_course_id.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Marks Obtained").grid(row=3, column=0, padx=10, pady=5)
    marks_obtained = tk.Entry(content_frame, width=30)
    marks_obtained.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(content_frame, text="Grade").grid(row=4, column=0, padx=10, pady=5)
    marks_grade = tk.Entry(content_frame, width=30)
    marks_grade.grid(row=4, column=1, padx=10, pady=5)

    def add_marks():
        try:
            cursor.execute("INSERT INTO Marks VALUES (?, ?, ?, ?)", (
                marks_student_id.get().strip(),
                marks_course_id.get().strip(),
                marks_obtained.get().strip(),
                marks_grade.get().strip()
            ))
            conn.commit()
            messagebox.showinfo("Success", "Marks added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(content_frame, text="Add Marks", command=add_marks).grid(row=5, columnspan=2, pady=10)

# View Marks Function
def view_marks():
    clear_frame()
    tk.Label(content_frame, text="View Marks", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)

    rows = cursor.execute("SELECT * FROM Marks").fetchall()
    for idx, row in enumerate(rows):
        tk.Label(content_frame, text=str(row)).grid(row=idx+1, column=0, padx=10, pady=2)

# Main Menu with Buttons
def main_menu():
    tk.Button(root, text="Add Student", command=add_student_form).pack(pady=5)
    tk.Button(root, text="Add Course", command=add_course_form).pack(pady=5)
    tk.Button(root, text="Enroll Student", command=enroll_student_form).pack(pady=5)
    tk.Button(root, text="Add Marks", command=add_marks_form).pack(pady=5)
    tk.Button(root, text="View Marks", command=view_marks).pack(pady=5)

# Initial Menu
main_menu()

root.mainloop()
conn.close()
