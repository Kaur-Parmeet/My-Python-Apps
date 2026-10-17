import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime

# ─── Cyber Theme ───
COLORS = {
    'bg':           '#0A0A0F',
    'bg_secondary': '#12121A',
    'bg_tertiary':  '#1A1A24',
    'neon_pink':    '#FF2E97',
    'neon_purple':  '#B537F2',
    'neon_cyan':    '#00F0FF',
    'text':         '#FFFFFF',
    'text_dim':     '#A0A0B0',
    'text_muted':   '#606070',
    'success':      '#00FF88',
    'error':        '#FF3366',
    'warning':      '#FFB800',
    'border':       '#2A2A3A',
    'border_glow':  '#FF2E97',
}


class CognyxApp:
    def __init__(self, root):
        self.root=root
        self.root.title("Cognyx 🧠 - The Learning Companion🤓")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLORS['bg'])
        self.setup_database()
        self.setup_screens()
        self.show_screen("Home")

    def setup_database(self):
        self.conn = sqlite3.connect("cognyx.db")
        self.cursor=self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS decks(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY AUTOINCREMENT, deck_id INTEGER NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL, difficulty TEXT DEFAULT 'Medium', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(deck_id) REFERENCES decks(id) ON DELETE CASCADE)''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY AUTOINCREMENT, deck_id INTEGER NOT NULL, total_cards INTEGER NOT NULL, correct_count INTEGER NOT NULL,  wrong_count INTEGER NOT NULL, skipped_count INTEGER NOT NULL DEFAULT 0, difficulty_filter TEXT, completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE)''')
        self.conn.commit()

    def setup_screens(self):
        self.container=tk.Frame(self.root, bg=COLORS['bg'])
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight = 1)

        self.screens={}
        for ScreenClass in (HomeScreen, DeckScreen, CardScreen, QuizSetupScreen, QuizScreen, ResultsScreen):
            name=ScreenClass.__name__.replace("Screen","")
            screen=ScreenClass(self.container, self)
            screen.grid(row=0, column=0, sticky='nsew')
            self.screens[name]=screen

    def show_screen(self,screen_name):
        if screen_name=='Home':
            self.screens['Home'].update_stats()
        self.screens[screen_name].tkraise()
        

class HomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app=app
        self.build_ui()
        self.update_stats()

    def build_ui(self):
        tk.Label(self, text="COGNYX", font=('Orbitron', 36, 'bold'), bg=COLORS['bg'], fg=COLORS['neon_pink']).pack(pady=(60,5))
        tk.Label(self, text="Master your memory", font=('Orbitron', 18), bg=COLORS['bg'], fg=COLORS['text_dim']).pack(pady=(0,40))

        stats_frame=tk.Frame(self, bg=COLORS['bg'])
        stats_frame.pack(pady=20, padx=20, fill=tk.X)

        def make_stat_box(parent, title, color, col):
            box=tk.Frame(parent, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
            box.grid(row=0, column=col, padx=10, pady=10, sticky='nsew')
            tk.Label(box, text=title, font=('Orbitron', 14, 'bold'), bg=COLORS['bg_secondary'], fg=color).pack(pady=(15,5))
            val_label=tk.Label(box, text='0', font=('Orbitron', 28, 'bold'), bg=COLORS['bg_secondary'], fg=color)
            val_label.pack(pady=(0,15))
            return val_label

        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)

        self.decks_stat=make_stat_box(stats_frame, 'DECKS', COLORS['neon_cyan'], 0)
        self.quizzes_stat=make_stat_box(stats_frame, 'QUIZZES TAKEN', COLORS['neon_purple'], 1)
        self.high_stat=make_stat_box(stats_frame, 'HIGH SCORE', COLORS['success'], 2)
        self.low_stat=make_stat_box(stats_frame, 'LOW SCORE', COLORS['error'], 3)

        btn_frame=tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=60)
        tk.Button(btn_frame, text='Browse Decks ', command=lambda: self.app.show_screen("Deck"), bg=COLORS['neon_pink'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack()

    def update_stats(self):
        self.app.cursor.execute('SELECT COUNT(*) FROM decks')
        deck_count=self.app.cursor.fetchone()[0]
        self.decks_stat.config(text=str(deck_count))

        self.app.cursor.execute('SELECT COUNT(*) FROM sessions')
        quiz_count=self.app.cursor.fetchone()[0]
        self.quizzes_stat.config(text=str(quiz_count))

        self.app.cursor.execute('SELECT MAX(CAST(correct_count AS FLOAT) / total_cards), MIN(CAST(correct_count AS FLOAT) / total_cards) FROM sessions WHERE total_cards>0 ')
        result=self.app.cursor.fetchone()

        if result and result[0] is not None:
            high_pct=round(result[0]*100)
            low_pct=round(result[1] *100)
            self.high_stat.config(text=f"{high_pct}%")
            self.low_stat.config(text=f"{low_pct}%")
        else:
            self.high_stat.config(text='-')
            self.low_stat.config(text='-')


class DeckScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app=app
        self.build_ui()
        self.load_decks()

    def build_ui(self):
        tk.Label(self, text=' YOUR DECKS', font=('Orbitron', 32, 'bold'), bg=COLORS['bg'], fg=COLORS['neon_cyan']).pack(pady=(60,5))
        tk.Label(self, text='Your cards live here', font=('Orbitron', 16), bg=COLORS['bg'], fg=COLORS['text_dim']).pack()
        tk.Button(self, text='Back To Home', command=lambda: self.app.show_screen("Home"), bg=COLORS['neon_purple'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).place(x=20, y=20)
        list_frame=tk.Frame(self, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=60, pady=10)
        scroll=ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.deck_tree=ttk.Treeview(list_frame, columns=('name', 'cards'), show ='headings', yscrollcommand=scroll.set)
        self.deck_tree.heading('name', text='Deck Name')
        self.deck_tree.heading('cards', text='Card Count')
        self.deck_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.config(command=self.deck_tree.yview)
        self.deck_tree.bind('<Double-1>', self.open_deck)

        btn_frame=tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text='New Deck', command=self.add_deck, bg=COLORS['neon_pink'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text='Delete', command=self.delete_deck, bg=COLORS['neon_cyan'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.RIGHT, pady=10)

    def load_decks(self):
        for item in self.deck_tree.get_children():
            self.deck_tree.delete(item)

        self.app.cursor.execute('SELECT d.id, d.name, COUNT(c.id) FROM decks d LEFT JOIN cards c ON c.deck_id=d.id GROUP BY d.id ORDER BY d.name')
        rows=self.app.cursor.fetchall()
        for deck_id, name, count in rows:
            self.deck_tree.insert('', tk.END, iid=deck_id, values=(name, f'{count} cards'))

    def add_deck(self):
        popup=tk.Toplevel(self.app.root)
        popup.title('Add a New Deck')
        popup.geometry('350x200')
        popup.configure(bg=COLORS['bg_secondary'])
        popup.transient(self.app.root)
        popup.grab_set()

        tk.Label(popup, text='Enter Deck Name', font=('Tilt Neon', 12), bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(pady=10)
        name_entry=tk.Entry(popup, font=('Tilt Neon', 12), width=30)
        name_entry.pack(pady=10)
        name_entry.focus()

        def save():
            name=name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a name for the deck!!")
                return

            try:
                self.app.cursor.execute("INSERT INTO decks(name) VALUES(?)", (name,))
                self.app.conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate", f"{name} already exists!!")
                return

            self.load_decks()
            messagebox.showinfo("Success", f"Deck {name} added successfully!!")
            popup.destroy()

        tk.Button(popup, text='Save', font=('Orbitron', 10),command=save, bg=COLORS['success'], fg=COLORS['text'], relief=tk.FLAT, cursor='hand2', padx=5, pady=5).pack(pady=15)
        name_entry.bind('<Return>', lambda e: save())

    def delete_deck(self):
        selection=self.deck_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a deck first!!")
            return
        deck_id=selection[0]
        self.app.cursor.execute('SELECT name FROM decks WHERE id=?', (deck_id,))
        deck_name=self.app.cursor.fetchone()[0]
        self.app.cursor.execute('SELECT COUNT(*) FROM cards WHERE deck_id=?', (deck_id,))
        card_count=self.app.cursor.fetchone()[0]

        msg=f"Delete '{deck_name}' ?"
        if card_count > 0:
            msg+=f"\n\n {card_count} card(s) will also be deleted !"
        if messagebox.askyesno("Confirm Delete", msg):
            self.app.cursor.execute('DELETE FROM decks WHERE id=?', (deck_id,))
            self.app.conn.commit()
            self.load_decks()
            

    def open_deck(self, event):
        selection=self.deck_tree.selection()
        if not selection:
            return
        deck_id=selection[0]
        self.app.screens['Card'].load_deck(deck_id)
        self.app.show_screen('Card')

class CardScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app=app
        self.current_deck_id = None
        self.build_ui()

    def build_ui(self):
        self.header_label=tk.Label(self, text='CARDS', font=('Orbitron', 32, 'bold'), bg=COLORS['bg'], fg=COLORS['neon_cyan'])
        self.header_label.pack(pady=(40,5))
        self.subtitle_label=tk.Label(self, text='Review your cards here', font=('Orbitron', 16), bg=COLORS['bg'], fg=COLORS['text_dim'])
        self.subtitle_label.pack(pady=(0,20))
        tk.Button(self, text='Back To Decks', command=lambda: self.app.show_screen("Deck"), bg=COLORS['neon_purple'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=15, pady=6).place(x=20, y=20)
        list_frame=tk.Frame(self, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=60, pady=10)
        scroll=ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.card_tree=ttk.Treeview(list_frame, columns=('question', 'answer', 'difficulty'), show='headings', yscrollcommand=scroll.set)
        self.card_tree.heading('question', text='Question')
        self.card_tree.heading('answer', text='Answer')
        self.card_tree.heading('difficulty', text="Difficulty")

        self.card_tree.column('question', width=350)
        self.card_tree.column('answer', width=350)
        self.card_tree.column('difficulty', width=100, anchor='center')

        self.card_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.config(command=self.card_tree.yview)

        btn_frame=tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text='Add Card', command=self.add_card, bg=COLORS['neon_pink'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text='Delete Card', command=self.delete_card, bg=COLORS['neon_purple'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text='Start Quiz', command=self.start_quiz, bg=COLORS['neon_cyan'], fg=COLORS['text'], font=('Tilt Neon', 12, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.RIGHT, padx=10)

    def load_deck(self, deck_id):
        self.current_deck_id=deck_id
        self.app.cursor.execute('SELECT name FROM decks WHERE id=?', (deck_id,))
        result=self.app.cursor.fetchone()
        if result:
            deck_name=result[0]
            self.header_label.config(text=f"{deck_name}")
            self.subtitle_label.config(text=f"Cards in '{deck_name}'")
        self.load_cards()

    def load_cards(self):
        for item in self.card_tree.get_children():
            self.card_tree.delete(item)

        self.app.cursor.execute('SELECT id, question, answer, difficulty FROM cards WHERE deck_id=? ORDER BY id DESC', (self.current_deck_id,))
        rows=self.app.cursor.fetchall()
        for card_id, question, answer, difficulty in rows:
            q_preview=question[:40]+"..." if len(question)>40 else question
            a_preview=answer[:40]+"..." if len(answer)>40 else answer
            self.card_tree.insert('', tk.END, iid=card_id, values=(q_preview, a_preview, difficulty))

    def add_card(self):
        popup=tk.Toplevel(self.app.root)
        popup.title("Add Card")
        popup.geometry("500x600")
        popup.configure(bg=COLORS['bg'])
        popup.transient(self.app.root)
        popup.grab_set()

        tk.Label(popup, text='Enter Question', font=('Tilt Neon', 12), bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(pady=10)
        ques_entry=tk.Text(popup, font=('Tilt Neon', 12), width=40, height=4)
        ques_entry.pack(pady=10)
        ques_entry.focus()

        tk.Label(popup, text='Enter Answer', font=('Tilt Neon', 12), bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(pady=10)
        ans_entry=tk.Text(popup,font=('Tilt Neon', 12), width=40, height=4)
        ans_entry.pack(pady=10)
        ans_entry.focus()

        diff_var=tk.StringVar(value='Medium')
        diff_menu=ttk.Combobox(popup, textvariable=diff_var, values=['Easy', 'Medium', 'Hard'], width=10)
        diff_menu.pack(pady=5)

        def save():
            ques=ques_entry.get('1.0', tk.END).strip()
            ans=ans_entry.get('1.0', tk.END).strip()
            diff=diff_var.get()
            if not ques:
                messagebox.showwarning("Warning", "Please enter a Question!!")
                return

            if not ans:
                messagebox.showwarning("Warning", "Please enter an Answer for the Question!!!")
                return
            
            try:
                self.app.cursor.execute("INSERT INTO cards(deck_id, question, answer, difficulty) VALUES(?,?,?,?)", (self.current_deck_id, ques, ans, diff,))
                self.app.conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate", f"{ques} already exists!!")
                return
            
            self.load_cards()
            messagebox.showinfo("Success", f"{ques} added successfully!!")
            popup.destroy()

        tk.Button(popup, text='Save', font=('Orbitron', 10),command=save, bg=COLORS['success'], fg=COLORS['text'], relief=tk.FLAT, cursor='hand2', padx=5, pady=5).pack(pady=15)
        ques_entry.bind('<Return>', lambda e: save())
        ans_entry.bind('<Return>', lambda e: save())

    def delete_card(self):
        selection=self.card_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a card first!!")
            return
        card_id=selection[0]
        self.app.cursor.execute('SELECT question FROM cards WHERE id=?', (card_id,))
        card_name=self.app.cursor.fetchone()[0]
        
        msg=f"Delete '{card_name}' ?"
        if messagebox.askyesno("Confirm Delete", msg):
            self.app.cursor.execute('DELETE FROM cards WHERE id=?', (card_id,))
            self.app.conn.commit()
            self.load_cards()

    def start_quiz(self):
        if not self.current_deck_id:
            messagebox.showwarning("Warning", "No Deck Selected!!")
            return
        self.app.screens['QuizSetup'].load_deck(self.current_deck_id)
        self.app.show_screen('QuizSetup')

class QuizSetupScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app=app
        self.current_deck_id = None
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="QUIZ SETUP", font=('Orbitron', 32, 'bold'), bg=COLORS['bg'], fg=COLORS['neon_purple']).pack(pady=(60,5))
        self.deck_label=tk.Label(self, text='No deck selected', font=('Orbitron', 16), bg=COLORS['bg'], fg=COLORS['text_dim'])
        self.deck_label.pack(pady=(0,30))
        tk.Button(self, text='Back', command=lambda: self.app.show_screen('Card'), bg=COLORS['neon_purple'], fg=COLORS['text'], font=('Tilt Neon', 11, 'bold'), relief=tk.FLAT, cursor='hand2', padx=15, pady=6).place(x=20, y=20)

        config_frame=tk.Frame(self, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        config_frame.pack(padx=100, pady=20, fill=tk.BOTH, expand=True)
        tk.Label(config_frame, text='Difficulty', font=('Orbitron', 14, 'bold'), bg=COLORS['bg_secondary'], fg=COLORS['neon_cyan']).pack(pady=(30,10))

        self.diff_var=tk.StringVar(value='All')
        options_frame=tk.Frame(config_frame, bg=COLORS['bg_secondary'])
        options_frame.pack(pady=10)
        for option in ['All', 'Easy', 'Medium', 'Hard']:
            tk.Radiobutton(options_frame, text=option, variable=self.diff_var, value=option, bg=COLORS['bg_secondary'], fg=COLORS['text'], selectcolor=COLORS['bg_secondary'], activebackground=COLORS['bg_secondary'], activeforeground=COLORS['neon_pink'], font=('Tilt Neon', 12), cursor='hand2').pack(side=tk.LEFT, padx=10)
        
        tk.Label(config_frame, text='NUMBER OF CARDS', font=('Orbitron', 14, 'bold'), bg=COLORS['bg_secondary'], fg=COLORS['neon_cyan']).pack(pady=(30,10))
        self.count_entry=tk.Entry(config_frame, font=('Tilt Neon', 12), width=10, justify='center')
        self.count_entry.pack(pady=10)

        tk.Button(config_frame, text='Start Quiz', command=self.start_quiz, bg=COLORS['neon_pink'], fg=COLORS['text'], font=('Orbitron', 14, 'bold'), relief=tk.FLAT, cursor='hand2', padx=30, pady=12).pack(pady=40)
         
    def load_deck(self, deck_id):
        self.current_deck_id=deck_id
        self.app.cursor.execute('SELECT name FROM  decks WHERE id=?', (deck_id,))
        result=self.app.cursor.fetchone()
        if result:
            deck_name=result[0]
            self.deck_label.config(text=f"Deck:{deck_name}")

    def start_quiz(self):
        if not self.current_deck_id: 
            messagebox.showwarning("Warning", "No deck selected!")
            return
        difficulty=self.diff_var.get()
        if difficulty=='All':
            query='SELECT id, question, answer, difficulty FROM cards WHERE deck_id=?'
            params=(self.current_deck_id,)
        else:
            query='SELECT id, question, answer, difficulty FROM cards WHERE deck_id=? AND difficulty=?'
            params=(self.current_deck_id, difficulty,)

        self.app.cursor.execute(query, params)
        all_cards=self.app.cursor.fetchall()
        if not all_cards:
            messagebox.showwarning("No Cards", "No cards match this difficulty!!")
            return

        cards_list=list(all_cards)
        random.shuffle(cards_list)

        count_text=self.count_entry.get().strip()
        if count_text == '' or count_text.lower()=='all':
            pass
        else:
            try:
                n=int(count_text)
                cards_list=cards_list[:n]
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter a number or 'All' !!")
                return

        self.app.screens['Quiz'].start_quiz(cards_list, self.current_deck_id, difficulty)
        self.app.show_screen('Quiz')

class QuizScreen(tk.Frame):
    def __init__ (self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app=app
        self.cards=[]
        self.current_index=0
        self.correct_count=0
        self.wrong_count=0
        self.skipped_count=0
        self.wrong_cards=[]
        self.skipped_cards=[]
        self.deck_id=None
        self.difficulty=None
        self.answer_revealed=False
        self.build_ui()

    def build_ui(self):
        top_bar=tk.Frame(self, bg=COLORS['bg'])
        top_bar.pack(fill=tk.X, padx=40, pady=(30,10))
        self.progress_label=tk.Label(top_bar, text='Card 0 / 0', font=('Orbitron', 16, 'bold'), bg=COLORS['bg'], fg=COLORS['neon_cyan'])
        self.progress_label.pack(side=tk.BOTTOM)

        tk.Button(top_bar, text='Quit', command=self.confirm_quit, bg=COLORS['error'], fg=COLORS['text'], font=('Tilt Neon', 11, 'bold'), relief=tk.FLAT, cursor='hand2', padx=15, pady=6).pack(side=tk.RIGHT)

        content=tk.Frame(self, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand = True, padx=80, pady=20)

        self.question_box=tk.Frame(content, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        self.question_box.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        tk.Label(self.question_box, text="QUESTION", font=('Orbitron', 11, 'bold'), bg=COLORS['bg_secondary'], fg=COLORS['neon_pink']).pack(pady=(15,5))
        self.question_label=tk.Label(self.question_box, text="", font=('Tilt Neon', 16), bg=COLORS['bg_secondary'], fg=COLORS['text'], wraplength=800, justify='center')
        self.question_label.pack(expand=True, padx=30, pady=20)

        self.answer_box=tk.Frame(content, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        tk.Label(self.answer_box, text='ANSWER',  font=('Orbitron', 11, 'bold'), bg=COLORS['bg_secondary'], fg=COLORS['neon_cyan']).pack(pady=(15,5))
        self.answer_label=tk.Label(self.answer_box, text="", font=('Tilt Neon', 16), bg=COLORS['bg_secondary'], fg=COLORS['text'], wraplength=800, justify='center')
        self.answer_label.pack(expand=True, padx=30, pady=20)

        self.progress_bar=ttk.Progressbar(self, length=600, mode='determinate')
        self.progress_bar.pack(pady=(0,20))

        self.button_area=tk.Frame(self, bg=COLORS['bg'])
        self.button_area.pack(side=tk.BOTTOM, pady=(0,30))

        self.reveal_btn=tk.Button(self.button_area, text='Reveal', command=self.reveal_answer, bg=COLORS['neon_purple'], fg=COLORS['text'], font=('Orbitron', 13, 'bold'), relief=tk.FLAT, cursor='hand2', padx=40, pady=15)
        self.reveal_btn.pack()

        self.correct_btn=tk.Button(self.button_area, text='Correct', command=self.mark_correct, bg=COLORS['success'], fg=COLORS['bg'], font=('Orbitron', 13, 'bold'), relief=tk.FLAT, cursor='hand2', padx=40, pady=15)
        self.wrong_btn=tk.Button(self.button_area, text='Wrong', command=self.mark_wrong, bg=COLORS['error'], fg=COLORS['text'], font=('Orbitron', 13, 'bold'), relief=tk.FLAT, cursor='hand2', padx=40, pady=15)

    def start_quiz(self, cards_list, deck_id, difficulty):
        self.cards=cards_list
        self.deck_id=deck_id
        self.difficulty=difficulty
        self.current_index=0
        self.correct_count=0
        self.wrong_count=0
        self.skipped_count=0
        self.wrong_cards=[]
        self.skipped_cards=[]
        self.answer_revealed=False

        self._bind_quiz_keys()
        self.show_card()

    def _bind_quiz_keys(self):
        self.app.root.bind('<space>', lambda e:self.on_space())
        self.app.root.bind('<Return>', lambda e:self.on_enter())
        self.app.root.bind('<equal>', lambda e: self.on_correct())
        self.app.root.bind('<minus>', lambda e: self.on_wrong())
        self.app.root.bind('<Escape>', lambda e: self.on_escape())

    def _unbind_quiz_keys(self):
        self.app.root.unbind('<space>')
        self.app.root.unbind('<Return>')
        self.app.root.unbind('<equal>')
        self.app.root.unbind('<minus>')
        self.app.root.unbind('<Escape>')

    def show_card(self):
        self.progress_label.config(text=f" Card {self.current_index + 1} / {len(self.cards)}")
        card=self.cards[self.current_index]
        card_id, question, answer, difficulty = card
        self.question_label.config(text=question)
        self.answer_box.pack_forget()
        self.correct_btn.pack_forget()
        self.wrong_btn.pack_forget()
        self.reveal_btn.pack()
        self.answer_revealed=False
        progress_pct=(self.current_index / len(self.cards))*100
        self.progress_bar['value']=progress_pct

    def reveal_answer(self):
        card=self.cards[self.current_index]
        _, _, answer, _ = card
        self.answer_label.config(text=answer)
        self.answer_box.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        self.reveal_btn.pack_forget()
        self.correct_btn.pack(side=tk.LEFT, padx=10)
        self.wrong_btn.pack(side=tk.LEFT, padx=10)
        self.answer_revealed=True

    def mark_correct(self):
        self.correct_count +=1
        self.next_card()

    def mark_wrong(self):
        self.wrong_count +=1
        self.wrong_cards.append(self.cards[self.current_index])
        self.next_card()

    def mark_skipped(self):
        self.skipped_count+=1
        self.skipped_cards.append(self.cards[self.current_index])
        self.next_card()

    def next_card(self):
        self.current_index+=1
        if self.current_index>= len(self.cards):
            self.finish_quiz()
        else:
            self.show_card()

    def finish_quiz(self):
        self._unbind_quiz_keys()
        self.app.cursor.execute('INSERT INTO sessions(deck_id, total_cards, correct_count, wrong_count, skipped_count, difficulty_filter) VALUES(?,?,?,?,?,?)', (self.deck_id, len(self.cards), self.correct_count, self.wrong_count, self.skipped_count, self.difficulty))
        self.app.conn.commit()
        results_data={'correct': self.correct_count, 'wrong' : self.wrong_count, 'skipped':self.skipped_count, 'total':len(self.cards), 'wrong_cards':self.wrong_cards, 'skipped_cards': self.skipped_cards, 'deck_id' : self.deck_id}
        self.app.screens['Results'].show_results(results_data)
        self.app.show_screen('Results')

    def confirm_quit(self):
        if messagebox.askyesno("Quit Quiz?", "Are you sure? Your progress will be lost!!"):
            self._unbind_quiz_keys()
            self.app.show_screen('Deck')


    def on_space(self):
        if not self.answer_revealed:
            self.reveal_answer()

    def on_enter(self):
        if not self.answer_revealed:
            self.mark_skipped()

    def on_correct(self):
        if self.answer_revealed:
            self.mark_correct()

    def on_wrong(self):
        if self.answer_revealed:
            self.mark_wrong()

    def on_escape(self):
        self.confirm_quit()

class ResultsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg'])
        self.app=app
        self.data=None
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text='QUIZ COMPLETE', font=('Orbitron', 32, 'bold'), bg=COLORS['bg'], fg=COLORS['success']).pack(pady=(30,5))
        score_frame=tk.Frame(self, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        score_frame.pack(pady=15, padx=100, fill=tk.X)
        self.score_label=tk.Label(score_frame, text='0 / 0', font=('Orbitron', 32, 'bold'), bg=COLORS['bg_secondary'], fg=COLORS['neon_pink'])
        self.score_label.pack(pady=(20,5))
        self.stats_label=tk.Label(score_frame, text='', font=('Tilt Neon', 14), bg=COLORS['bg_secondary'], fg=COLORS['text'])
        self.stats_label.pack(pady=(0,20))

        tk.Label(self, text='REVIEW NEEDED', font=('Orbitron', 14, 'bold'), bg=COLORS['bg'], fg=COLORS['neon_cyan']).pack(pady=(20,5))
        review_frame=tk.Frame(self, bg=COLORS['bg_secondary'], highlightbackground=COLORS['border'], highlightthickness=1)
        review_frame.pack(fill=tk.BOTH, expand=True, padx=80, pady=10)
        scroll=ttk.Scrollbar(review_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.review_tree=ttk.Treeview(review_frame, columns=('category', 'question', 'answer'), show='headings', yscrollcommand=scroll.set)
        self.review_tree.heading('category', text='Category')
        self.review_tree.heading('question', text='Question')
        self.review_tree.heading('answer', text='Answer')
        self.review_tree.column('category', width=140, anchor='center')
        self.review_tree.column('question', width=350)
        self.review_tree.column('answer', width=350)

        self.review_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.config(command=self.review_tree.yview)

        btn_frame=tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text='Retry Missed', command=self.retry_missed, bg=COLORS['neon_purple'], fg=COLORS['text'], font=('Orbitron', 11, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text='Retake Quiz', command=self.retake_quiz, bg=COLORS['neon_pink'], fg=COLORS['text'], font=('Orbitron', 11, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text='Back to Decks', command=lambda: self.app.show_screen('Deck'), bg=COLORS['success'], fg=COLORS['bg'], font=('Orbitron', 11, 'bold'), relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

        
    def show_results(self, data):
        self.data=data
        correct=data['correct']
        total=data['total']
        percent=round((correct/total)*100) if total>0 else 0
        self.score_label.config(text=f"{correct} / {total}  ({percent}%)")
        self.stats_label.config(text=f"{correct} Correct | {data['skipped']} Needs Review | {data['wrong']} Wrong")

        for item in self.review_tree.get_children():
            self.review_tree.delete(item)

        for card in data['skipped_cards']:
            card_id, question, answer, difficulty = card
            self.review_tree.insert('', tk.END, values=('Review', question, answer))

        for card in data['wrong_cards']:
            card_id, question, answer, difficulty = card
            self.review_tree.insert('', tk.END, values=('Wrong', question, answer))

    def retry_missed(self):
        if not self.data:
            return
        missed_cards=self.data['wrong_cards']+self.data['skipped_cards']
        if not missed_cards:
            messagebox.showinfo("Perfect!!", "You didn't miss any cards !!!")
            return
        random.shuffle(missed_cards)
        self.app.screens['Quiz'].start_quiz(missed_cards, self.data['deck_id'], 'Review')
        self.app.show_screen('Quiz')        

    def retake_quiz(self):
        if not self.data:
            return
        self.app.screens['QuizSetup'].load_deck(self.data['deck_id'])
        self.app.show_screen('QuizSetup')

if __name__=='__main__':
    root=tk.Tk()
    app=CognyxApp(root)
    root.mainloop()