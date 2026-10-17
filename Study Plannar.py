#Study Plannar 
import tkinter as tk
from tkinter import ttk, messagebox
import json 
import sqlite3
from datetime import datetime

class StudyPlanner:
    def __init__ (self,root):
        self.root=root
        self.root.title("📚Study Planner📑")
        self.root.geometry("1100x700")
        self.root.configure(bg="#d09bec")
        self.setup_database()
        self.create_widgets()
        self.load_subjects()
        self.update_dashboard()

    def setup_database(self):
        self.conn=sqlite3.connect("Study.db")
        self.cursor=self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS topics(id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id INTEGER NOT NULL, name TEXT NOT NULL, deadline DATE, completed BOOLEAN DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE)''')
        self.conn.commit()

    def create_widgets(self):
        #header
        header=tk.Frame(self.root, bg="#d09bec", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Study Plannar🔖", font=('Helvetica', 20, 'bold'), bg="#d09bec", fg="#7b079f").pack(side=tk.LEFT, padx=20)
        self.refresh_btn=tk.Button(header, text="🔄 Refresh", command=self.refresh, bg="#3996ed", fg='white', font=('Helvetica', 11, 'bold'), padx=15, pady=5, relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=20)

        #main box
        main_container=tk.Frame(self.root, bg="#f3d3fa")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        #left panel : subjects list
        left_panel=tk.Frame(main_container, bg="#cd8af0", width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_panel.pack_propagate(False)
        tk.Label(left_panel, text="Subjects", font=('Helvetica', 15, 'bold'), bg="#ce8feb", fg="#7b079f").pack(pady=10)
        scrollbar=ttk.Scrollbar(left_panel, style="Vertical.TScrollbar")
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        #treeview for subjects : left panel
        self.subjects_tree=ttk.Treeview(left_panel, columns=('name'), show='tree', yscrollcommand=scrollbar.set)
        self.subjects_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.subjects_tree.yview)

        self.subjects_tree.bind('<<TreeviewSelect>>', self.on_subject_select)

        #add subject button in left panel
        self.add_subject_btn=tk.Button(left_panel, text="➕ Add Subject", bg="#f2bad2", fg='white', command=self.add_subject,font=('Helvetica', 11, 'bold'), relief=tk.FLAT,cursor='hand2')
        self.add_subject_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=5)

        #right panel : topics in subjects
        right_panel=tk.Frame(main_container, bg="#cd8af0", width=750)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right_panel, text="Topics and Things To-Do", font=('Helvetica', 15, 'bold'), bg="#ce8feb", fg="#7b079f").pack(pady=10)
        scroll=ttk.Scrollbar(right_panel, style="Vertical.TScrollbar")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        #treeview for topics : right panel
        self.topics_tree=ttk.Treeview(right_panel, columns=('status','topic', 'deadline'), show='headings', yscrollcommand=scroll.set)

        self.topics_tree.heading('status', text='Status')
        self.topics_tree.heading('topic', text='Topic')
        self.topics_tree.heading('deadline', text='Deadline')

        self.topics_tree.column('status', width=80, anchor='center')
        self.topics_tree.column('topic', width=400, anchor='w')
        self.topics_tree.column('deadline', width=150, anchor='center')

        self.topics_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.config(command=self.topics_tree.yview)

        self.topics_tree.bind('<<TreeviewSelect>>', self.on_topic_select)

        #button frame : right panel
        topics_btn_frame=tk.Frame(right_panel, bg="#cd8af0")
        topics_btn_frame.pack(side=tk.BOTTOM, pady=10)

        #buttons : right panel 
        self.add_topics_btn=tk.Button(topics_btn_frame, text="➕ Add Topic", bg="#f285bc", fg="white", font=('Helvetica', 11, 'bold'), padx=15, pady=5, relief=tk.FLAT, cursor='hand2', command=self.add_topic).pack(side=tk.LEFT,expand=True, padx=3)
        self.complete_btn=tk.Button(topics_btn_frame, text="✅ Mark Complete", bg="#7ef582", fg='white', font=('Helvetica', 11, 'bold'), padx=15, pady=5, relief=tk.FLAT, cursor='hand2', command=self.mark_complete).pack(side=tk.LEFT,expand=True, padx=3)
        self.delete_btn=tk.Button(topics_btn_frame, text="🗑️ Delete", bg="#f25d4d", fg='white', font=('Helvetica', 11, 'bold'), padx=15, pady=5, relief=tk.FLAT, cursor='hand2', command=self.delete_topic).pack(side=tk.LEFT,expand=True, padx=3)

        #basically the footer with stats
        dashboard=tk.Frame(self.root, bg="#d09bec", height=80)
        dashboard.pack(side=tk.BOTTOM, fill=tk.X)
        dashboard.pack_propagate(False)
        self.dashboard_label=tk.Label(dashboard, text="📊 Total: 0  |  ✅ Done: 0  |  ⏳ Pending: 0  |  0% Complete", font=('Helvetica', 14, 'bold'), bg="#cd8af0", fg='white')
        self.dashboard_label.pack(pady=20)

        #the treeview styling
        style=ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background="#f3d3fa", foreground='black', rowheight=30, fieldbackground="#f3d3fa", font=('Helvetica', 12))
        style.configure('Treeview.Heading', background="#ce8feb", foreground='white', font=('Helvetica', 12, 'bold'))
        style.map("Treeview", background=[('selected', '#ffb6c1')])
        style.configure("Vertical.TScrollbar", background="#f5f3f7", troughcolor="#efd5f5", bordercolor="#400050", arrowcolor="#ce8feb", darkcolor="#400050", lightcolor="#f4d7fb", relief='flat', arrowsize=14, width=14)
        style.map('Vertical.TScrollbar', background=[('active', '#f5f3f7')], arrowcolor=[('active', '#ffffff')])

    def add_subject(self):
        popup=tk.Toplevel(self.root)
        popup.title("Add New Subject")
        popup.geometry("350x200")
        popup.configure(bg='#f3d3fa')
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text='Subject Name :', font=('Helvetica', 11, 'bold'), bg='#f3d3fa', fg="#7b08ac").pack(pady=20)

        name_entry=tk.Entry(popup, font=('Helvetica', 11, 'bold'), width=50)
        name_entry.pack(padx=10, pady=10)
        name_entry.focus()

        def save():
            name=name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a subject name!")
                return

            try:
                self.cursor.execute("INSERT INTO subjects(name) VALUES(?)", (name,))
                self.conn.commit()
            except sqlite3.IntegrityError: 
                messagebox.showwarning("Duplicate", f"'{name}' already exists!!")
                return

            self.load_subjects()
            messagebox.showinfo("Success", f"Subject '{name}' added Successfully!!")
            popup.destroy()

        tk.Button(popup, text='Save', command=save,font=('Helvetica' , 11, 'bold'), bg="#7ef582", fg='#fcfcfc', relief=tk.FLAT, cursor='hand2', padx=5, pady=5).pack(pady=15)
        name_entry.bind('<Return>', lambda e: save())

    def load_subjects(self):
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)

        self.cursor.execute("SELECT id, name FROM subjects ORDER BY name")
        rows=self.cursor.fetchall()
        for subject_id, name in rows:
            self.subjects_tree.insert('', tk.END, iid=subject_id, text=name)

    def on_subject_select(self, event):
        selected=self.subjects_tree.selection()
        if not selected :
            return
        subject_id = selected[0]
        self.load_topics(subject_id)
        self.update_dashboard()

    def add_topic(self):
        selection=self.subjects_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a subject first!!")
            return
        subject_id=selection[0]

        popup=tk.Toplevel(self.root)
        popup.title("Add Topic")
        popup.geometry("400x280")
        popup.configure(bg='#f3d3fa')
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text='Topic Name :', font=('Helvetica', 11, 'bold'), bg='#f3f3f3', fg='#7b08ac').pack(pady=10)
        name_entry=tk.Entry(popup, font=('Helvetica', 11, 'bold'), width=50)
        name_entry.pack(padx=30, pady=10)
        name_entry.focus()

        tk.Label(popup, text='Deadline (YYYY-MM-DD) :', font=('Helvetica', 11, 'bold'), bg='#f3f3f3', fg='#7b08ac').pack(pady=(15,5), padx=20)
        deadline_entry=tk.Entry(popup, font=('Helvetica' , 11, 'bold'), width=50)
        deadline_entry.pack(pady=10, padx=40)

        def save():
            name = name_entry.get().strip()
            deadline = deadline_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a topic name!!")
                return

            if not deadline :
                deadline = None

            try:
                self.cursor.execute("INSERT INTO topics(id, subject_id, name, deadline) VALUES(NULL, ?, ?, ?)", (subject_id, name, deadline))
                self.conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate", f"'{name}' already exists!!!")
                return
 
            self.load_topics(subject_id)
            self.update_dashboard()
            messagebox.showinfo("Success", f"'{name}' topic added successfully!!!")
            popup.destroy()

        tk.Button(popup, text='Save', command=save, font=('Helvetica', 11, 'bold'), bg='#7ef582', fg='white', relief=tk.FLAT, cursor='hand2', padx=5, pady=5).pack(pady=15)
        name_entry.bind('<Return>', lambda e: save())
        deadline_entry.bind('<Return>', lambda e: save())


    def load_topics(self, subject_id):
        for item in self.topics_tree.get_children():
            self.topics_tree.delete(item)

        self.cursor.execute("SELECT id, name, deadline, completed FROM topics WHERE subject_id=? ORDER BY completed, deadline", (subject_id,))
        rows=self.cursor.fetchall()
        for topic_id, name, deadline, completed in rows:
            status='✅' if completed else '⏳'
            display_deadline=deadline if deadline else "No Deadline"
            self.topics_tree.insert('', tk.END, iid=topic_id, values=(status, name, display_deadline))

    def on_topic_select(self):
        pass

    def mark_complete(self):
        selected=self.topics_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a topic first!!!")
            return
        topic_id=selected[0]
        self.cursor.execute("UPDATE topics SET completed = NOT completed WHERE id=?", (topic_id,))
        self.conn.commit()

        subject_selection=self.subjects_tree.selection()
        if subject_selection:
            self.load_topics(subject_selection[0])

        self.update_dashboard()

    def delete_topic(self):
        selection=self.topics_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a topic first!!!")
            return
        topic_id=selection[0]
        self.cursor.execute("SELECT name FROM topics WHERE id=?", (topic_id,))
        topic_name = self.cursor.fetchone()[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{topic_name}' ?"):
            self.cursor.execute("DELETE FROM topics WHERE id=?", (topic_id,))
            self.conn.commit()

            subject_selection=self.subjects_tree.selection()
            if subject_selection:
                self.load_topics(subject_selection[0])
            self.update_dashboard()


    def update_dashboard(self):
        selection=self.subjects_tree.selection()
        if not selection:
            self.dashboard_label.config(text="📊 Select a subject to see its progress")
            return

        subject_id=selection[0]
        self.cursor.execute("SELECT COUNT(*) FROM topics WHERE subject_id=?", (subject_id,))
        total=self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM topics WHERE subject_id=? AND completed = 1", (subject_id,))
        done= self.cursor.fetchone()[0]

        pending=total-done
        if total>0:
            percent=round((done/total)*100)
        else:
            percent=0

        self.dashboard_label.config(text=f"📊Total:{total}  |  ✅Done : {done}  |  ⏳Pending : {pending}  |  {percent}% Complete")

    def refresh(self):
        self.load_subjects()
        for item in self.topics_tree.get_children():
            self.topics_tree.delete(item)

        self.update_dashboard()

if __name__=='__main__':
    root=tk.Tk()
    app=StudyPlanner(root)
    root.mainloop()
    


        #i need to create : 
        #widgets: 
        #1. main container DONE 
        #2. two panels DONE
        #3. header DONE
        #4. Dashboard bar (stats) DONE
        #5. Button to add subject DONE
        #6. Button to add topic in subject DONE
        #7. Button to delete a task DONE
        #8. Button to mark the task complete DONE
        #9. Refresh Button DONE
        #10. Messageboxes for delete confirmation and added succesfully messages DONE

