#First try app 
import tkinter as tk
from tkinter import messagebox
import json
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime 

class NotesApp:
    def __init__(self,root):
        self.root=root
        self.root.title("Brain Dump")
        self.root.geometry("1400x1200")
        self.root.configure(bg='#ffe791')
        self.notes={}
        self.current_note_id=None
        self.setup_database()
        self.create_widgets()
        self.load_notes()
        

    def setup_database(self):
        self.conn=sqlite3.connect('notes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title TEXT NOT NULL,
                                    content TEXT,
                                    priority TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    )''')
        self.conn.commit()

    def create_widgets(self):
        #-----header-------
        header=tk.Frame(self.root, bg='#ffcb97', height=85)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Notes App", font=('Helvetica', 25, 'bold'), bg="#eef5bc", fg='white').pack(pady=15)

        #main container
        main_container=tk.Frame(self.root, bg="#b891ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #--------left panel--------
        left_panel=tk.Frame(main_container, bg='#ffcb97', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="Saved Notes", font=('Helvcetica', 16, 'bold'), bg='#ffcb97', fg='#333').pack(pady=10)

        #tree view for notes list
        columns=('ID', 'Title', 'Priority', 'Created')
        self.notes_tree=ttk.Treeview(left_panel, columns=columns, show='headings', height=18)
        self.notes_tree.heading('ID', text='ID')
        self.notes_tree.heading('Title', text='Note')
        self.notes_tree.heading('Priority', text='Priority')
        self.notes_tree.heading('Created', text='Created')
        self.notes_tree.column('ID', width=40)
        self.notes_tree.column('Title', width=250)
        self.notes_tree.column('Priority', width=100)
        self.notes_tree.column('Created', width=150)

        #Button
        tk.Button(left_panel, text="Add New Note", command=self.add_note, bg="#76ece2", fg='white', font=('Helvetica', 10, 'bold'), padx=15, pady=5).pack(side=tk.LEFT, padx=10)

        #scrollbar
        scrollbar=ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=scrollbar.set)
        self.notes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        #bind selection event to load note content 
        self.notes_tree.bind('<<TreeviewSelect>>', self.on_note_select)

        #-------Right panel-------
        right_panel=tk.Frame(main_container, bg='#ffe791')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10,0))

        #title entry
        tk.Label(right_panel, text='Title', font=('Helvetica', 12, 'bold'), bg="#a1d3fc").pack(anchor=tk.W, pady=(0,10))
        self.title_entry=tk.Entry(right_panel, font=('Comic Sans MS', 14), width=50)
        self.title_entry.pack(fill=tk.X, pady=(0,10))

        #priority dropdown
        priority_frame=tk.Frame(right_panel, bg="#bf97d8")
        priority_frame.pack(anchor=tk.W, pady=(0,10))
        tk.Label(priority_frame, text="Priority :", font=('Helvetica', 10, 'bold'), bg='white').pack(side=tk.LEFT, padx=10)
        self.priority_var=tk.StringVar(value="Medium")
        priority_menu=ttk.Combobox(priority_frame, textvariable=self.priority_var, values=['High', 'Medium', 'Low'], width=10)
        priority_menu.pack(side=tk.LEFT)

        #text area
        tk.Label(right_panel, text='Content :', font=('Helvetica', 12, 'bold'), bg='#f0f0f0').pack(anchor=tk.W, pady=5)
        self.text_area=tk.Text(right_panel, font=('Helvetica', 12), wrap=tk.WORD, height=20, width=60)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=10)

        #Buttons
        button_frame = tk.Frame(right_panel, bg='#ffe791')
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="💾 Save Note", command=self.save_note, bg='#3498db', fg='white', font=('Helvetica', 11, 'bold'), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🗑️ Delete Note", command=self.delete_note, bg='#db5534', fg='white', font=('Helvetica', 11, 'bold'), padx=20, pady=5).pack(side=tk.LEFT, padx=5)

        #I WORKED TILL HERE 
        #6 SEPTEMBER -> I HAVE WORKED TILL HERE ONLY ...... YOU NEED TO EDIT YOUR CODE FURTHER


    def add_note(self):
        self.current_note_id=None
        self.title_entry.delete(0,tk.END)
        self.text_area.delete(1.0, tk.END)
        self.priority_var.set("Medium")
        self.notes_tree.selection_remove(self.notes_tree.selection())
        messagebox.showinfo("New Note", "Write your new note and click Save.")

    def load_notes(self):
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)

        self.cursor.execute('''SELECT id, title, priority, strftime('%Y-%m-%d %H:%M', created_at)FROM notes ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, created_at DESC''')

        for note in self.cursor.fetchall():
            tags=()
            if note[2]=='High':
                tags=('high',)
            elif note[2] == 'Medium':
                tags =('medium',)
            else:
                 tags=('low',)
            self.notes_tree.insert('', tk.END, values=note, tags=tags)

        self.notes_tree.tag_configure('high', background='#ffcccc')
        self.notes_tree.tag_configure('medium', background='#ffffcc')
        self.notes_tree.tag_configure('low', background='#ccffcc')

    def on_note_select(self, event):
        selected=self.notes_tree.selection()
        if not selected:
             return
        note_id=self.notes_tree.item(selected[0])['values'][0]
        self.cursor.execute('SELECT title, content, priority FROM notes WHERE id=?', (note_id,))
        result=self.cursor.fetchone()
        if result:
             self.current_note_id=note_id
             self.title_entry.delete(0,tk.END)
             self.title_entry.insert(0, result[0])
             self.text_area.delete(1.0, tk.END)
             self.text_area.insert(1.0, result[1] if result[1] else"")
             self.priority_var.set(result[2])
                

    def save_note(self):
        title=self.title_entry.get().strip()
        if not title:
              messagebox.showwarning("Warning", "Please enter a title!")
              return
        content=self.text_area.get(1.0, tk.END).strip()
        priority=self.priority_var.get()

        if self.current_note_id is None:
            self.cursor.execute('''INSERT INTO notes (title, content, priority) VALUES(?,?,?)''', (title, content, priority))
            messagebox.showinfo("Success", "Note added successfully!")
        else:
            self.cursor.execute('''UPDATE notes SET title=?, content=?, priority=? WHERE id=?''', (title, content, priority, self.current_note_id))
            messagebox.showinfo("Success", "Note updated successfully!")

        self.conn.commit()
        self.load_notes()

        self.current_note_id=None
        self.title_entry.delete(0, tk.END)
        self.text_area.delete(1.0, tk.END)
        self.priority_var.set("Medium")
        self.notes_tree.selection_remove(self.notes_tree.selection())


    def delete_note(self):
        selected = self.notes_tree.selection()
        if not selected:
                    messagebox.showwarning("Warning", "Please select a Note!")
                    return
        if messagebox.askyesno("Confirm Delete", "Delete this note?"):
                    note_id=self.notes_tree.item(selected[0])['values'][0]
                    self.cursor.execute('DELETE FROM notes WHERE id =?', (note_id,))
                    self.conn.commit()
                    self.load_notes()

                    if self.current_note_id==note_id:
                        self.current_note_id=None
                        self.title_entry.delete(0, tk.END)
                        self.text_area.delete(1.0, tk.END)
                        self.priority_var.set("Medium")
                    messagebox.showinfo("Deleted", "Note removed.")

    def __del__(self):
            if hasattr(self,'conn'):
                self.conn.close()


if __name__=='__main__':
    root=tk.Tk()
    app=NotesApp(root)
    root.mainloop()