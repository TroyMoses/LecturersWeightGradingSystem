import tkinter as tk
from tkinter import ttk, messagebox
import openpyxl
import os
import sqlite3


assignees_window = None  # Declare globally


def insert_assignee(name, subject):
    with sqlite3.connect("lecturers.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO assignees VALUES (?, ?)", (name, subject))
        conn.commit()


def insert_subjects():
    subjects = [
        # Major subjects
        ("Software Engineering Ethics", "Major"),
        ("Programming Concepts Using C", "Major"),
        ("Software Engineering", "Major"),
        ("Programming Using VB.Net", "Major"),
        ("Python Programming", "Major"),
        ("OOP Using Java", "Major"),
        ("Data Structures and Algorithms", "Major"),
        ("Linux Basics", "Major"),
        ("User Interface Design", "Major"),
        ("Android Programming", "Major"),
        ("Open Source Software", "Major"),
        ("Software Architecture & Design", "Major"),
        ("Artificial Intelligence Concepts", "Major"),
        ("Application Development Frameworks", "Major"),
        ("Computer Science Mathematics I", "Major"),
        ("Discrete Mathematics", "Major"),
        ("Computer Science Mathematics II", "Major"),

        # Cognate subjects
        ("Funds of Relational Database System", "Cognate"),
        ("Fundamentals of Web Development", "Cognate"),
        ("Information System", "Cognate"),
        ("System Analysis & Design", "Cognate"),
        ("Relational Database Systems II", "Cognate"),
        ("Internets and Web Programming", "Cognate"),
        ("Simulation & Modeling", "Cognate"),
        ("Business Intelligence System", "Cognate"),
        ("Basic Entrepreneurship", "Cognate"),
        ("Windows Client Server Admin", "Cognate"),
        ("Parallel and Distributed Systems", "Cognate"),
        ("Linux Client Server Administration", "Cognate"),
        ("Operating Systems", "Cognate")
    ]

    with sqlite3.connect("lecturers.db") as conn:
        c = conn.cursor()
        c.executemany("INSERT INTO subjects VALUES (?, ?)", subjects)
        conn.commit()


insert_subjects()


def fetch_subjects():
    with sqlite3.connect("lecturers.db") as conn:
        c = conn.cursor()
        c.execute("SELECT subject FROM subjects")
        subjects = [row[0] for row in c.fetchall()]
    return subjects


def view_assignees():
    global assignees_window  # Make sure assignees_window is accessible

    if not assignees_window:  # Only create the window if it doesn't exist
        assignees_window = tk.Toplevel()
        assignees_window.title("Assigned Lecturers")
        assignees_window.geometry("500x600")

        # Create the assigned_treeFrame in the new window
        assigned_treeFrame = ttk.Frame(assignees_window)
        assigned_treeFrame.grid(row=1, column=1, columnspan=2, pady=10, padx=10)
        treeScroll2 = ttk.Scrollbar(assigned_treeFrame)
        treeScroll2.pack(side="right", fill="y")
        assigned_treeview_header = ttk.Label(assigned_treeFrame, text="Assigned Subjects")
        assigned_treeview_header.pack()

        cols = ("Name", "Assigned Subject")
        assigned_treeview = ttk.Treeview(assigned_treeFrame, show="headings", columns=cols, height=13)
        for col in cols:
            assigned_treeview.column(col, width=200)
            assigned_treeview.heading(col, text=col)
        assigned_treeview.pack()
        treeScroll2.config(command=treeview.yview)

        assigned_treeview.delete(*assigned_treeview.get_children())

        with sqlite3.connect("lecturers.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM assignees")
            assignees_data = c.fetchall()

        for assignee_values in assignees_data:
            assigned_treeview.insert('', tk.END, values=assignee_values)

    assignees_window.lift()  # Bring the window to the front


def load_data():
    path = "lecturers.db"

    # Create the database if it doesn't exist
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS lecturers (
                name TEXT,
                qualification TEXT,
                experience TEXT,
                publications TEXT,
                weight REAL,
                subject TEXT
            )
        """)

    # Connect to the database and fetch lecturers
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM lecturers ORDER BY weight DESC")
        lecturers_data = c.fetchall()

    # Populate Treeview with sorted data
    for lecturer_values in lecturers_data:
        treeview.insert('', tk.END, values=lecturer_values)


def on_entry_click(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.insert(0, "")
        entry.config(foreground="grey")


def on_entry_leave(event, entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        entry.config(foreground="grey")


def calculate_weight(qualification, experience, publications):
    new_qualification = {
        "Certificate": 5 * 2,
        "Degree": 5 * 3,
        "Masters": 5 * 4,
        "PhD": 5 * 5
    }[qualification]

    new_experience = {
        "0-5 years": 4 * 3,
        "6-10 years": 4 * 4,
        "Above 10 years": 4 * 5
    }[experience]

    new_publications = {
        "1-3": 3 * 3,
        "4-6": 3 * 4,
        "Above 7": 3 * 5
    }[publications]

    # Calculate weight
    total = new_qualification + new_experience + new_publications
    weight = "{:.4f}".format(total / 12)
    return weight


def insert_lecturer():
    name = lecturer_name_entry.get()
    qualification = qualification_combobox.get()
    experience = experience_combobox.get()
    publications = publications_combobox.get()
    subject = subject_combobox.get()

    # Calculate weight
    weight = calculate_weight(qualification, experience, publications)

    # Insert lecturer into SQLite database
    with sqlite3.connect("lecturers.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO lecturers VALUES (?, ?, ?, ?, ?, ?)",
                  (name, qualification, experience, publications, weight, subject))
        conn.commit()

    # Insert lecturer into treeview
    treeview.insert('', tk.END, values=(name, qualification, experience, publications, weight, subject))

    # Clear the values
    clear_entries()


# def load_assignees():
#     assigned_treeview.delete(*assigned_treeview.get_children())
#
#     with sqlite3.connect("lecturers.db") as conn:
#         c = conn.cursor()
#         c.execute("SELECT * FROM assignees")
#         assignees_data = c.fetchall()
#
#     for assignee_values in assignees_data:
#         assigned_treeview.insert('', tk.END, values=assignee_values)


def search_lecturers():
    search_term = search_entry.get().lower()

    # Connect to the database and search for lecturers
    with sqlite3.connect("lecturers.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM lecturers WHERE name LIKE ? OR subject LIKE ?",
                  ('%' + search_term + '%', '%' + search_term + '%'))
        lecturers_data = c.fetchall()

    # Clear treeview and populate with filtered data
    treeview.delete(*treeview.get_children())
    for lecturer_values in lecturers_data:
        treeview.insert('', tk.END, values=lecturer_values)

    # Display message if no results found
    if not lecturers_data:
        tk.messagebox.showinfo("Search Results", "No lecturers found matching the search term.")


def clear_entries():
    lecturer_name_entry.delete(0, "end")
    lecturer_name_entry.insert(0, "Name")
    lecturer_name_entry.config(foreground="grey")

    qualification_combobox.set(qualification_options[0])
    experience_combobox.set(experience_options[0])
    publications_combobox.set(publications_options[0])
    subject_combobox.set(subject_options[0])


def toggle_mode():
    if mode_switch.instate(["selected"]):
        style.theme_use("forest-light")
    else:
        style.theme_use("forest-dark")


def filter_and_assign_lecturer():
    selected_subject = subject_filter_combobox.get()

    with sqlite3.connect("lecturers.db") as conn:
        c = conn.cursor()

        # Check if the subject is already assigned
        c.execute("SELECT * FROM assignees WHERE assigned_subject = ?", (selected_subject,))
        assigned_lecturer = c.fetchone()

        if assigned_lecturer:
            messagebox.showinfo("Subject Already Assigned", f"{selected_subject} is already assigned to {assigned_lecturer[0]}.")
            return  # Exit the function if already assigned

        # Find the best lecturer for the subject
        c.execute("""
            SELECT *
            FROM lecturers
            WHERE subject = ?
            ORDER BY weight DESC
            LIMIT 1
        """, (selected_subject,))
        best_lecturer = c.fetchone()

        if best_lecturer:
            message = f"The most suitable lecturer for {selected_subject} is: {best_lecturer[0]}"
            messagebox.showinfo("Best Lecturer", message)
            name = best_lecturer[0]
            subject = best_lecturer[5]  # Assuming subject is the 6th column
            insert_assignee(name, subject)
        else:
            messagebox.showinfo("No Lecturer Found", "No lecturer found with the selected subject.")

        # Create a new window for assignees
        assignees_window = tk.Toplevel()
        assignees_window.title("Assigned Lecturers")
        assignees_window.geometry("800x600")

        # Create the assigned_treeFrame in the new window
        assigned_treeFrame = ttk.Frame(assignees_window)
        assigned_treeFrame.grid(row=1, column=1, columnspan=2, pady=10, padx=10)
        treeScroll2 = ttk.Scrollbar(assigned_treeFrame)
        treeScroll2.pack(side="right", fill="y")
        assigned_treeview_header = ttk.Label(assigned_treeFrame, text="Assigned Subjects")
        assigned_treeview_header.pack()

        cols = ("Name", "Assigned Subject")
        assigned_treeview = ttk.Treeview(assigned_treeFrame, show="headings", columns=cols, height=13)
        for col in cols:
            assigned_treeview.column(col, width=200)
            assigned_treeview.heading(col, text=col)
        assigned_treeview.pack()
        treeScroll2.config(command=treeview.yview)

        assigned_treeview.delete(*assigned_treeview.get_children())

        with sqlite3.connect("lecturers.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM assignees")
            assignees_data = c.fetchall()

        for assignee_values in assignees_data:
            assigned_treeview.insert('', tk.END, values=assignee_values)


root = tk.Tk()
window_width = 1000
window_height = 650
root.geometry(f"{window_width}x{window_height}")

style = ttk.Style(root)
root.tk.call("source", "forest-light.tcl")
root.tk.call("source", "forest-dark.tcl")
style.theme_use("forest-dark")
style.configure('TButton', font=('Helvetica', 12))  # Example font size, adjust as needed
style.configure('TLabel', font=('Helvetica', 18))
style.configure('TEntry', font=('Helvetica', 18))
style.configure('TCombobox', font=('Helvetica', 18))
style.configure('TCheckbutton', font=('Helvetica', 14))

qualification_options = ["Certificate", "Degree", "Masters", "PhD"]
experience_options = ["0-5 years", "6-10 years", "Above 10 years"]
publications_options = ["1-3", "4-6", "Above 7"]

subject_options = fetch_subjects()

frame = ttk.Frame(root)
frame.pack()

widgets_frame = ttk.LabelFrame(frame, text="Insert Lecturer")
widgets_frame.grid(row=0, column=0, padx=20, pady=10)

lecturer_name_entry = ttk.Entry(widgets_frame, foreground="grey")
lecturer_name_entry.insert(0, "Name")
lecturer_name_entry.bind("<FocusIn>", lambda e: on_entry_click(e, lecturer_name_entry, "Name"))
lecturer_name_entry.bind("<FocusOut>", lambda e: on_entry_leave(e, lecturer_name_entry, "Name"))
lecturer_name_entry.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="ew")

qualification_combobox = ttk.Combobox(widgets_frame, values=qualification_options)
qualification_combobox.current(0)
qualification_combobox.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

experience_combobox = ttk.Combobox(widgets_frame, values=experience_options)
experience_combobox.current(0)
experience_combobox.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

publications_combobox = ttk.Combobox(widgets_frame, values=publications_options)
publications_combobox.current(0)
publications_combobox.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

subject_combobox = ttk.Combobox(widgets_frame, values=subject_options)
subject_combobox.current(0)
subject_combobox.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

button = ttk.Button(widgets_frame, text="Insert Lecturer", command=insert_lecturer)
button.grid(row=7, column=0, padx=5, pady=5, sticky="nsew")

search_entry = ttk.Entry(widgets_frame)
search_entry.insert(0, "Search")
search_entry.bind("<FocusIn>", lambda e: on_entry_click(e, search_entry, "Search"))
search_entry.bind("<FocusOut>", lambda e: on_entry_leave(e, search_entry, "Search"))
search_entry.grid(row=14, column=0, padx=5, pady=5, sticky="ew")

search_button = ttk.Button(widgets_frame, text="Search", command=search_lecturers)
search_button.grid(row=15, column=0, padx=5, pady=5, sticky="nsew")

clear_button = ttk.Button(widgets_frame, text="Clear Entries", command=clear_entries)
clear_button.grid(row=9, column=0, padx=5, pady=5, sticky="nsew")

separator = ttk.Separator(widgets_frame)
separator.grid(row=10, column=0, padx=(20, 10), pady=10, sticky="ew")

# New UI elements for the filtering algorithm
subject_filter_combobox = ttk.Combobox(widgets_frame, values=subject_options)
subject_filter_combobox.current(0)
subject_filter_combobox.grid(row=11, column=0, padx=5, pady=5, sticky="ew")

assign_button = ttk.Button(widgets_frame, text="Assign", command=filter_and_assign_lecturer)
assign_button.grid(row=12, column=0, padx=5, pady=5, sticky="nsew")

# Create the "View Assignees" button
view_assignees_button = tk.Button(widgets_frame, text="View Assignees", command=view_assignees)
view_assignees_button.grid(row=13, column=0, padx=5, pady=5, sticky="nsew")  # Place it below the assign button

add_priorities_button = tk.Button(widgets_frame, text="Add Lec. Priorities")
add_priorities_button.grid(row=8, column=0, padx=5, pady=5, sticky="nsew")

mode_switch = ttk.Checkbutton(
    widgets_frame, text="Mode", style="Switch", command=toggle_mode)
mode_switch.grid(row=16, column=0, padx=5, pady=10, sticky="nsew")

treeFrame = ttk.Frame(frame)
treeFrame.grid(row=0, column=1, columnspan=2, pady=10)
treeScroll = ttk.Scrollbar(treeFrame)
treeScroll.pack(side="right", fill="y")

cols = ("Name", "Qualification", "Experience", "Publications", "Weight", "Subject")
treeview = ttk.Treeview(treeFrame, show="headings",
                        yscrollcommand=treeScroll.set, columns=cols, height=27)
for col in cols:
    treeview.column(col, width=100)
    treeview.heading(col, text=col)
treeview_header = ttk.Label(treeFrame, text="Lecturers' Weight")
treeview_header.pack()
treeview.pack()
treeScroll.config(command=treeview.yview)


root.after(0, load_data)
root.mainloop()

