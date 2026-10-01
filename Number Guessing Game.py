import tkinter as tk
from tkinter import ttk, messagebox 
import random 
import sqlite3
import os

class CuteGuessingGame:
    def __init__(self,root):
        self.root=root
        self.root.title("🎯Cute Number Guesser")
        self.root.geometry('800x700')

        #setting color schemes
        self.colors= { 'bg':'#fff0f5', 'header':'#ffb6c1', 'button':'#ff69b4', 'button_hover':'#ff1493', 'text':'#4a4a4a', 'success':'#98fb98', 'warning':'#ffd700', 'card':'#ffffff'}
        self.root.configure(bg=self.colors['bg'])

        #game state
        self.secret_number=0
        self.attempts=0
        self.difficulty='Medium'
        self.max_attempts=10
        self.is_game_over=False

        #setting up database
        self.setup_database()

        #create UI
        self.create_widgets()

        #start new game
        self.new_game()

    def setup_database(self):
        self.conn=sqlite3.connect('game_scores.db')
        self.cursor=self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, attempts INTEGER, difficulty TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''' )
        self.conn.commit()

    def new_game(self):
        #Update difficulty first 
        self.difficulty=self.diff_var.get()

        #reset game state
        self.is_game_over=False
        self.attempts=0
                            
        #set range based on difficulty 
        ranges={'Easy':(1,50), 'Medium':(1,100), "Hard":(1,250)}
        low,high=ranges[self.difficulty]
        self.secret_number=random.randint(low,high)
                            
        #update UI
        self.progress['value']=0
        self.attempt_label.config(text=f"🎯Attempts:0")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.config(state='normal')
        self.guess_button.config(state='normal')
                            
        #cute messages
        self.hint_label.config(text=f"🔮 I'm thinking of a number between {low} and {high}!", fg=self.colors['text'])
        self.feedback.config(text='✨Make a guess! You can do this!💪', fg='#6c6c6c')
                            
        #get best score for this difficulty
        self.cursor.execute('SELECT MIN(attempts) FROM scores WHERE difficulty = ?', (self.difficulty,))
        best=self.cursor.fetchone()[0]
        if best:
            self.best_label.config(text=f"🌟Best : {best} guesses")
        else:
            self.best_label.config(text="🫡No record yet!!")
                            
        #enable entries
        self.guess_entry.focus()
                     
       

       

    def create_widgets(self):
        #Header
        header=tk.Frame(self.root, bg=self.colors['header'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        #Title
        tk.Label(header, text="The Ultimate Number Guessing Game✨🌟", font=('Comic Sans MS', 20, 'bold'), bg="#f5e8bc", fg='white').pack(pady=10)
        
        #Subtitle
        tk.Label(header, text="Guess the Number and Beat your best Score!!!", font=('Comic Sans MS', 10), bg="#f5e8bc", fg='white').pack()

        #Main Container
        main_container=tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #Score and difficulty section 
        info_frame=tk.Frame(main_container, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=(0,10))

        #Best Score
        self.best_label=tk.Label(info_frame, text="🗽Best 💪: ", font=('Comic Sans MS', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text'])
        self.best_label.pack(pady=5)

        #Difficulty Selector 
        diff_frame=tk.Frame(info_frame, bg=self.colors['card'])
        diff_frame.pack(pady=5)
        tk.Label(diff_frame, text="Difficulty :", font=('Comic Sans MS', 12, 'bold'), bg=self.colors['card']).pack(side=tk.LEFT, padx=5)
        self.diff_var=tk.StringVar(value="Medium")
        diff_menu=ttk.Combobox(diff_frame, textvariable=self.diff_var, values=['Easy', 'Medium', 'Hard'], width=12, state='readonly')
        diff_menu.pack(side=tk.LEFT, padx=5)
        diff_menu.bind('<<ComboboxSelected>>', lambda e: self.new_game())
        tk.Button(diff_frame, text="🆕New Game", command=self.new_game, bg=self.colors['button'], fg='white', font=('Comic Sans MS', 12, 'bold'), padx=15, pady=3).pack(side=tk.LEFT, padx=5)

        #Game Area
        game_frame=tk.Frame(main_container, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        game_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        #Hint
        self.hint_label=tk.Label(game_frame, text="🤔I'm thinking of a number", font=('Comic Sans MS', 14, 'bold'), bg=self.colors['card'], fg=self.colors['text'])
        self.hint_label.pack(pady=15)

        #Input Area
        input_frame=tk.Frame(game_frame, bg=self.colors['card'])
        input_frame.pack(pady=10)
        self.guess_entry=tk.Entry(input_frame, width=15, font=('Comic Sans MS', 16), justify='center')
        self.guess_entry.pack(side=tk.LEFT, padx=5)
        self.guess_entry.bind('<Return>', lambda e: self.check_guess())
        self.guess_button=tk.Button(input_frame, text="Guess", command=self.check_guess, bg=self.colors['button'], fg='white', font=('Comic Sans MS', 12, 'bold'), padx=15, pady=5)
        self.guess_button.pack(side=tk.LEFT, padx=5)

        #Feedback
        self.feedback=tk.Label(game_frame, text=" 🌟Make Your First Guess!!", font=('Comic Sans MS', 13), bg=self.colors['card'], fg='#6c6c6c')
        self.feedback.pack(pady=10)

        #Progress Bar
        self.progress=ttk.Progressbar(game_frame, length=400, mode='determinate', style='Cute.Horizontal.TProgressbar')
        self.progress.pack(pady=10)

        #Attempts
        self.attempt_label=tk.Label(game_frame, text="🎯Attempts : 0", font=('Comic Sans MS', 12), bg=self.colors['card'], fg=self.colors['text'])
        self.attempt_label.pack(pady=5)

        #Create Buttons for Stats, High Score, Hint etc. 
        button_frame=tk.Frame(main_container, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=10)
        tk.Button(button_frame, text="📊My Stats", command=self.show_stats, bg='#87ceeb', fg='white', font=('Comic Sans MS', 10, 'bold'), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text= "🎯High Scores", command=self.show_high_scores, bg='#ffd700', fg='white', font=('Comic Sans Ms', 10, 'bold'), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="💡Hint", command=self.give_hint, bg='#dda0dd', fg='white', font=('Comic Sans MS', 10, 'bold'), padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def check_guess(self):
        if self.is_game_over:
            messagebox.showinfo("Game Over", "The game is over! Click 'New Game' to try again🎮")
            return

        try:
            guess=int(self.guess_entry.get())
        except ValueError:
            messagebox.showwarning("Oops!", "Please enter a number !🤔")
            self.guess_entry.delete(0, tk.END)
            return

        self.attempts +=1 
        self.attempt_label.config(text=f"🚩Attempts : {self.attempts}")

        #update progress
        progress_value=min(100,(self.attempts/30)*100)
        self.progress['value'] = progress_value

        #check guess 
        diff=abs(guess-self.secret_number)
        if guess < self.secret_number:
            if diff <= 5:
                msg = "📈 So close! Go a bit higher! 🤗"
                color = '#FF6B6B'
            elif diff <= 15:
                msg = "📈 Higher! You're getting warm! 🌟"
                color = '#FFA94D'
            else:
                msg = "📈 Higher! Keep going! 💪"
                color = '#4DABF7'
            self.feedback.config(text=msg, fg=color)
            self.guess_entry.delete(0, tk.END)

        elif guess > self.secret_number:
            if diff <=5:
                msg = "📉 So close! Go a bit lower! 🤗"
                color = '#FF6B6B'
            elif diff <= 15:
                msg = "📉 Lower! You're getting warm! 🌟"
                color = '#FFA94D'
            else:
                msg = "📉 Lower! Keep going! 💪"
                color = '#4DABF7'
            self.feedback.config(text=msg, fg=color)
            self.guess_entry.delete(0, tk.END)

        else:
            self.is_game_over = True
            self.progress['value'] = 100
            self.guess_entry.config(state='disabled')
            self.guess_button.config(state='disabled')

            win_messages = [
                f"🎉 YOU WON in {self.attempts} attempts! You're amazing! 🌟",
                f"✨ Perfect! {self.attempts} attempts! You're a genius! 🧠",
                f"🏆 {self.attempts} attempts! You're the champion! 👑",
                f"💖 {self.attempts} attempts! I'm so proud of you! 🥰"]

            self.feedback.config(text=random.choice(win_messages), fg='#2e8b57')
            self.hint_label.config(text=f"🎯 The number was {self.secret_number}!")

            #save high score
            self.cursor.execute('INSERT INTO scores (difficulty, attempts) VALUES (?,?)', (self.difficulty, self.attempts))
            self.conn.commit()

            #uppdate best score
            self.cursor.execute('SELECT MIN(attempts) FROM scores WHERE difficulty =?', (self.difficulty,))
            best=self.cursor.fetchone()[0]
            if best:
                self.best_label.config(text=f"✨ Best: {best} guesses")

            messagebox.showinfo("🎉 Congratulations!", f"You guessed it in {self.attempts} attempts!\n\nYou're a number wizard! 🧙‍♂️")

    def give_hint(self):
        if self.is_game_over:
            messagebox.showinfo("Game Over", "Start a new game first !🔄")
            return

        low=max(1, self.secret_number - 10)
        high=min(100, self.secret_number +10)

        hints = [
            f"💡 It's between {low} and {high}!",
            f"💡 The number {'is even' if self.secret_number % 2 == 0 else 'is odd'}!",
            f"💡 It's {'greater' if self.secret_number > 50 else 'less'} than 50!",
            f"💡 You're {'getting closer!' if self.attempts > 0 else 'just starting!'}"]

        messagebox.showinfo("💡Hint", random.choice(hints))

    def show_stats(self):
        self.cursor.execute('''SELECT COUNT(*) as total_games, AVG(attempts) as avg_attempts, MIN(attempts) as best_score, difficulty FROM scores GROUP BY difficulty ''')
        stats=self.cursor.fetchall()

        if not stats:
            messagebox.showinfo("📊 Your Stats", "You haven't played any games yet! Start playing! 🎮")
            return

        stat_text= "📊 Your Statistics\n" + "="*30 + "\n\n"

        for row in stats:
            total, avg, best, diff = row
            stat_text += f"🎯 {diff}:\n"
            stat_text += f"   Games: {total}\n"
            stat_text += f"   Best: {int(best)} guesses\n"
            stat_text += f"   Average: {avg:.1f} guesses\n\n"

        messagebox.showinfo("📊 Your Stats", stat_text)

    def show_high_scores(self):
        self.cursor.execute('''SELECT difficulty, attempts, date FROM scores ORDER BY attempts ASC LIMIT 10''')
        scores=self.cursor.fetchall()

        if not scores:
            messagebox.showinfo("🏆 High Scores", "No scores yet! Be the first! 🌟")
            return

        leaderboard="🏆 High Scores\n"+"="*30 +"\n\n"

        for i, (diff, attempts, date) in enumerate(scores, 1):
            medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f"{i}."
            date_str = date[:10]  # Just the date part
            leaderboard += f"{medal} {diff:8}  {attempts:3} guesses  ({date_str})\n"

        messagebox.showinfo("🏆 High Scores", leaderboard)

if __name__ == "__main__":
    root=tk.Tk()
    app=CuteGuessingGame(root)
    root.mainloop()


        

