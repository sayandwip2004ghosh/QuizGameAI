# quiz_app_full.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, random, csv
from datetime import datetime
import os



# Optional libs
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

# Optional for sound
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False

# ----------------- Configurable Settings -----------------
QUESTIONS_JSON = "questions.json"
LEADERBOARD_CSV = "leaderboard.csv"
TIME_PER_QUESTION = 15  # seconds default
IMAGE_MAX_SIZE = (320, 220)
SOUNDS = {
    "correct": "correct.wav",
    "wrong": "wrong.wav",
    "timeout": "timeout.wav"
}
# ---------------------------------------------------------

def load_questions_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def play_sound(name):
    if not SOUND_AVAILABLE:
        return
    fname = SOUNDS.get(name)
    if not fname or not os.path.isfile(fname):
        return
    try:
        pygame.mixer.Sound(fname).play()
    except Exception:
        pass

# ----------------- Main App -----------------
class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz App — Full Edition")
        self.master.geometry("820x560")
        self.style = ttk.Style()
        self.theme = "light"  # or "dark"
        self.setup_styles()

        # state
        self.categories = []
        self.questions = []       # flattened questions of chosen category (list of dicts)
        self.q_index = 0
        self.user_answers = []    # user's chosen option strings per question
        self.time_per_question = TIME_PER_QUESTION
        self.time_left = self.time_per_question
        self.timer_running = False
        self.current_image = None

        # GUI frames
        self.header = ttk.Frame(master, padding=10)
        self.header.pack(fill="x")
        self.content = ttk.Frame(master, padding=12)
        self.content.pack(fill="both", expand=True)
        self.footer = ttk.Frame(master, padding=10)
        self.footer.pack(fill="x")

        # Header content
        self.title_label = ttk.Label(self.header, text="Quiz App", font=("Helvetica", 20, "bold"))
        self.title_label.pack(side="left")
        self.progress_var = tk.StringVar(value="No quiz loaded")
        self.progress_label = ttk.Label(self.header, textvariable=self.progress_var)
        self.progress_label.pack(side="left", padx=12)
        self.timer_var = tk.StringVar(value="")
        self.timer_label = ttk.Label(self.header, textvariable=self.timer_var, font=("Helvetica", 12))
        self.timer_label.pack(side="right")
        self.theme_btn = ttk.Button(self.header, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.pack(side="right", padx=(6,0))
        self.leaderboard_btn = ttk.Button(self.header, text="Leaderboard", command=self.show_leaderboard)
        self.leaderboard_btn.pack(side="right", padx=(6,0))

        # Content: left question area, right controls
        self.left = ttk.Frame(self.content)
        self.left.pack(side="left", fill="both", expand=True)
        self.right = ttk.Frame(self.content, width=260)
        self.right.pack(side="right", fill="y")

        # Left area: question, image, options, feedback
        self.question_text = tk.StringVar()
        self.question_label = ttk.Label(self.left, textvariable=self.question_text, wraplength=460, font=("Helvetica", 14))
        self.question_label.pack(anchor="w", pady=(6,8))
        self.image_label = ttk.Label(self.left)
        self.image_label.pack(pady=(0,8))
        self.option_var = tk.StringVar(value="")
        self.radio_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(self.left, text="", variable=self.option_var, value="", takefocus=False)
            rb.pack(anchor="w", pady=6)
            self.radio_buttons.append(rb)
        self.feedback_var = tk.StringVar(value="")
        self.feedback_label = ttk.Label(self.left, textvariable=self.feedback_var, font=("Helvetica", 11))
        self.feedback_label.pack(anchor="w", pady=(6,6))

        # Right area: controls
        ttk.Label(self.right, text="Controls", font=("Helvetica", 12, "bold")).pack(pady=(6,8))
        self.prev_btn = ttk.Button(self.right, text="Previous", command=self.prev_pressed)
        self.prev_btn.pack(fill="x", pady=6)
        self.next_btn = ttk.Button(self.right, text="Next", command=self.next_pressed)
        self.next_btn.pack(fill="x", pady=6)
        self.review_btn = ttk.Button(self.right, text="Review & Submit", command=self.open_review)
        self.review_btn.pack(fill="x", pady=6)
        ttk.Separator(self.right).pack(fill="x", pady=8)
        ttk.Label(self.right, text="Quiz Settings", font=("Helvetica", 12, "bold")).pack(pady=(6,8))
        ttk.Label(self.right, text="Time per Q (s):").pack(anchor="w")
        self.time_spin = ttk.Spinbox(self.right, from_=5, to=120, increment=5, width=8, command=self.update_time)
        self.time_spin.set(str(self.time_per_question))
        self.time_spin.pack(anchor="w", pady=(0,8))
        self.shuffle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.right, text="Shuffle Questions & Options", variable=self.shuffle_var).pack(anchor="w", pady=(0,8))

        ttk.Separator(self.right).pack(fill="x", pady=8)
        ttk.Button(self.right, text="Export Result (CSV)", command=self.export_result).pack(fill="x", pady=6)
        ttk.Button(self.right, text="Restart Quiz", command=self.restart_quiz).pack(fill="x", pady=6)

        # Footer: progressbar for timer
        self.footer_left = ttk.Frame(self.footer)
        self.footer_left.pack(side="left", fill="x", expand=True)
        self.progressbar = ttk.Progressbar(self.footer_left, orient="horizontal", mode="determinate")
        self.progressbar.pack(fill="x", expand=True, padx=6, pady=6)

        # Load JSON and open category selector
        try:
            self.categories = load_questions_from_json(QUESTIONS_JSON)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load {QUESTIONS_JSON}: {e}")
            self.categories = []

        self.open_category_selector()

    # ---------- Styling ----------
    def setup_styles(self):
        # Basic light/dark styles using ttk.Style
        self.style.theme_use('default')
        # Light defaults
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0")
        self.style.configure("TButton", padding=6)
        self.style.configure("TRadiobutton", background="#f0f0f0")
        # Dark mode overrides will be applied in toggle_theme
        self.apply_light_theme()

    def apply_light_theme(self):
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", foreground="#000000")
        self.style.configure("TButton", background="#e0e0e0", foreground="#000000")
        self.master.configure(background="#f0f0f0")
        self.theme = "light"

    def apply_dark_theme(self):
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
        self.style.configure("TButton", background="#3a3a3a", foreground="#ffffff")
        self.style.configure("TRadiobutton", background="#2b2b2b", foreground="#ffffff")
        self.master.configure(background="#2b2b2b")
        self.theme = "dark"

    def toggle_theme(self):
        if self.theme == "light":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    # ---------- Category selection ----------
    def open_category_selector(self):
        # Build a simple popup to choose category
        if not self.categories:
            messagebox.showerror("No Data", "No categories/questions available in JSON.")
            return
        top = tk.Toplevel(self.master)
        top.title("Select Category")
        top.geometry("420x320")
        ttk.Label(top, text="Choose category to start", font=("Helvetica", 14, "bold")).pack(pady=12)
        listbox = tk.Listbox(top, height=8)
        listbox.pack(fill="both", expand=True, padx=12)
        for i, cat in enumerate(self.categories):
            listbox.insert("end", cat.get("category", f"Category {i+1}"))
        listbox.selection_set(0)

        def start_for_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Select", "Please select a category.")
                return
            idx = sel[0]
            cat_obj = self.categories[idx]
            # Flatten and prepare questions
            qs = cat_obj.get("questions", [])
            # validate
            qlist = []
            for q in qs:
                # ensure options exist and answer in them
                options = q.get("options", [])
                if q.get("answer") not in options:
                    # place correct answer first then extend unique options
                    if q.get("answer"):
                        options = [q["answer"]] + [o for o in options if o != q["answer"]]
                # pad options to at least 2 (UI expects up to 4)
                while len(options) < 2:
                    options.append("")
                # truncate/pad to 4
                options = options[:4] + ([""] * max(0, 4 - len(options)))
                qlist.append({
                    "question": q.get("question", ""),
                    "options": options,
                    "answer": q.get("answer", ""),
                    "image": q.get("image", "")
                })
            # shuffle questions if needed (do at start)
            if self.shuffle_var.get():
                random.shuffle(qlist)
                # shuffle options but keep correct mapping
                for q in qlist:
                    opts = q["options"].copy()
                    random.shuffle(opts)
                    q["options"] = opts
            self.questions = qlist
            self.user_answers = [""] * len(self.questions)
            self.q_index = 0
            top.destroy()
            self.load_question()

        ttk.Button(top, text="Start", command=start_for_selected).pack(pady=8)

    # ---------- Time settings ----------
    def update_time(self):
        try:
            v = int(self.time_spin.get())
            if v < 1:
                v = 1
        except Exception:
            v = TIME_PER_QUESTION
        self.time_per_question = v

    # ---------- Load & display a question ----------
    def load_question(self):
        if not self.questions:
            self.question_text.set("No questions loaded.")
            return
        if self.q_index < 0:
            self.q_index = 0
        if self.q_index >= len(self.questions):
            self.open_review()
            return
        q = self.questions[self.q_index]
        self.question_text.set(f"Q{self.q_index+1}. {q.get('question','')}")
        # options
        opts = q.get("options", [])
        for i, rb in enumerate(self.radio_buttons):
            if i < len(opts):
                rb.config(text=opts[i], value=opts[i])
                rb.pack(anchor="w", pady=6)
            else:
                rb.pack_forget()
        # restore previous selection
        prev = self.user_answers[self.q_index] if self.q_index < len(self.user_answers) else ""
        self.option_var.set(prev)
        # image
        self.show_image(q.get("image",""))
        # progress text
        self.progress_var.set(f"Question {self.q_index+1} / {len(self.questions)}")
        # prev/next button state
        if self.q_index == 0:
            self.prev_btn.state(["disabled"])
        else:
            self.prev_btn.state(["!disabled"])

        if self.q_index == len(self.questions)-1:
            self.next_btn.config(text="Finish")
        else:
            self.next_btn.config(text="Next")
        # reset feedback
        self.feedback_var.set("")
        # start timer
        self.timer_running = False
        self.time_left = self.time_per_question
        self.progressbar['maximum'] = self.time_per_question
        self.progressbar['value'] = self.time_per_question
        self.start_timer()

    def show_image(self, path):
        if not path:
            self.image_label.config(image="", text="")
            self.current_image = None
            return
        if not Image or not ImageTk:
            self.image_label.config(text=f"(Pillow not installed) Image: {path}", image="")
            return
        if not os.path.isfile(path):
            self.image_label.config(text=f"(missing) {path}", image="")
            return
        try:
            img = Image.open(path)
            img.thumbnail(IMAGE_MAX_SIZE)
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.current_image, text="")
        except Exception as e:
            self.image_label.config(text=f"Error loading image: {e}", image="")

    # ---------- Timer ----------
    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.timer_running = False

    def update_timer(self):
        if not self.timer_running:
            return
        # update text and progressbar
        self.timer_var.set(f"Time Left: {self.time_left}s")
        self.progressbar['value'] = self.time_left
        if self.time_left <= 0:
            self.timer_running = False
            self.feedback_var.set("⏳ Time Up!")
            play_sound("timeout")
            self.handle_timeout()
            return
        self.time_left -= 1
        # schedule next tick
        self.master.after(1000, self.update_timer)

    def handle_timeout(self):
        # save current selected (may be empty)
        sel = self.option_var.get()
        self.user_answers[self.q_index] = sel
        # auto move
        if self.q_index < len(self.questions)-1:
            self.q_index += 1
            self.load_question()
        else:
            self.open_review()

    # ---------- Navigation ----------
    def next_pressed(self):
        self.stop_timer()
        sel = self.option_var.get()
        self.user_answers[self.q_index] = sel
        # immediate feedback
        q = self.questions[self.q_index]
        if sel:
            if sel == q.get("answer"):
                self.feedback_var.set("✅ Correct!")
                play_sound("correct")
            else:
                self.feedback_var.set(f"❌ Incorrect. (Correct: {q.get('answer')})")
                play_sound("wrong")
        else:
            self.feedback_var.set("No answer selected.")
        # move forward or finish
        if self.q_index < len(self.questions)-1:
            self.q_index += 1
            self.load_question()
        else:
            self.open_review()

    def prev_pressed(self):
        self.stop_timer()
        if self.q_index > 0:
            self.q_index -= 1
            self.load_question()

    # ---------- Review & Submit ----------
    def open_review(self):
        # Stop timer
        self.stop_timer()
        # Review window where user can navigate and edit answers
        top = tk.Toplevel(self.master)
        top.title("Review Answers")
        top.geometry("760x480")
        ttk.Label(top, text="Review your answers. Click a question to jump and edit.", font=("Helvetica", 12, "bold")).pack(pady=8)
        frame = ttk.Frame(top, padding=8)
        frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # list question summaries
        for i, q in enumerate(self.questions):
            your = self.user_answers[i] if i < len(self.user_answers) else ""
            text = f"Q{i+1}. {q.get('question')}\n   Your: {your}\n   Correct: {q.get('answer')}\n"
            lbl = ttk.Label(scrollable, text=text, wraplength=700, justify="left")
            lbl.pack(anchor="w", pady=6)
            def make_jump(idx):
                def jump(_=None):
                    top.destroy()
                    self.q_index = idx
                    self.load_question()
                return jump
            lbl.bind("<Button-1>", make_jump(i))

        btn_frame = ttk.Frame(top, padding=8)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Submit Quiz", command=lambda: [top.destroy(), self.submit_quiz()]).pack(side="right", padx=6)
        ttk.Button(btn_frame, text="Close", command=top.destroy).pack(side="right")

    def submit_quiz(self):
        # finalize answers, compute score and save to leaderboard
        score = 0
        total = len(self.questions)
        for i, q in enumerate(self.questions):
            ans = self.user_answers[i] if i < len(self.user_answers) else ""
            if ans == q.get("answer"):
                score += 1
        pct = (score/total)*100 if total>0 else 0
        msg = f"Your Score: {score} / {total}  ({pct:.1f}%)"
        # ask for name
        name = simpledialog.askstring("Finished", f"{msg}\n\nEnter your name for leaderboard (or Cancel to skip):")
        if name:
            self.save_leaderboard(name, score, total)
        # show detailed results
        self.show_result_window(score, total)

    def show_result_window(self, score, total):
        pct = (score/total)*100 if total>0 else 0
        win = tk.Toplevel(self.master)
        win.title("Result")
        win.geometry("640x400")
        ttk.Label(win, text="Quiz Result", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(win, text=f"Score: {score} / {total} ({pct:.1f}%)", font=("Helvetica", 12)).pack(pady=6)
        frame = ttk.Frame(win, padding=8)
        frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, q in enumerate(self.questions):
            your = self.user_answers[i] if i < len(self.user_answers) else "(no answer)"
            correct = q.get("answer")
            text = f"Q{i+1}. {q.get('question')}\n   Your: {your}\n   Correct: {correct}\n"
            ttk.Label(scrollable, text=text, wraplength=580, justify="left").pack(anchor="w", pady=6)

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)

    # ---------- Leaderboard ----------
    def save_leaderboard(self, name, score, total):
        try:
            with open(LEADERBOARD_CSV, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([name, score, total, datetime.now().isoformat()])
            messagebox.showinfo("Saved", "Score saved to leaderboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save leaderboard: {e}")

    def show_leaderboard(self):
        top = tk.Toplevel(self.master)
        top.title("Leaderboard")
        top.geometry("420x420")
        ttk.Label(top, text="Leaderboard (Top entries)", font=("Helvetica", 14, "bold")).pack(pady=8)
        frame = ttk.Frame(top, padding=8)
        frame.pack(fill="both", expand=True)
        # read leaderboard
        rows = []
        if os.path.isfile(LEADERBOARD_CSV):
            try:
                with open(LEADERBOARD_CSV, "r", encoding="utf-8") as f:
                    r = csv.reader(f)
                    for row in r:
                        if len(row) >= 4:
                            name, score, total, ts = row[0], int(row[1]), int(row[2]), row[3]
                            pct = (int(score)/int(total))*100 if int(total)>0 else 0
                            rows.append((name, score, total, pct, ts))
                # sort by score pct desc
                rows.sort(key=lambda x: (x[3], x[1]), reverse=True)
            except Exception as e:
                ttk.Label(frame, text=f"Error reading leaderboard: {e}").pack()
        if not rows:
            ttk.Label(frame, text="No leaderboard entries yet.").pack()
        else:
            for i, r in enumerate(rows[:50]):
                name, score, total, pct, ts = r
                ttk.Label(frame, text=f"{i+1}. {name} — {score}/{total} ({pct:.1f}%) — {ts[:19]}").pack(anchor="w", pady=2)
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=8)

    # ---------- Export results ----------
    def export_result(self):
        if not self.questions:
            messagebox.showinfo("No data", "No quiz data to export.")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"quiz_export_{timestamp}.csv"
        try:
            with open(fname, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Question", "Your Answer", "Correct Answer", "Correct?"])
                for i, q in enumerate(self.questions):
                    your = self.user_answers[i] if i < len(self.user_answers) else ""
                    correct = q.get("answer")
                    w.writerow([q.get("question"), your, correct, "YES" if your == correct else "NO"])
            messagebox.showinfo("Exported", f"Exported to {fname}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    # ---------- Restart ----------
    def restart_quiz(self):
        if not messagebox.askyesno("Restart", "Restart the quiz (lose current progress)?"):
            return
        self.open_category_selector()

# ----------------- Run -----------------
def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()