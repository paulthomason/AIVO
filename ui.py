
"""Graphical user interface for the diagnostic questionnaire."""

import tkinter as tk
from tkinter import ttk, messagebox

import config
from engine_rule import DiagnosisEngine
from storage_json import load_questions, load_diseases, load_model


class DiagnosisUI:
    """Interactive Tkinter UI driving ``DiagnosisEngine``."""

    def __init__(self, master, *, debug: bool | None = None):
        self.master = master
        self.questions = load_questions()
        self.diseases = load_diseases()
        self.model = load_model()
        # ``load_questions`` now returns ``Question`` objects
        self.question_ids = [q.qid for q in self.questions]
        if debug is None:
            debug = config.get_env_bool("AIVO_DEBUG")
        self.engine = DiagnosisEngine(
            self.diseases,
            self.question_ids,
            self.model,
            debug=debug,
        )
        self.current_question = None
        self.total_questions = len(self.question_ids)
        self.init_ui()
        self.next_question()

    def init_ui(self):
        self.master.title("Vet Ophthalmology Diagnosis")
        self.master.geometry(
            f"{config.DIAG_SCREEN_WIDTH}x{config.DIAG_SCREEN_HEIGHT}"
        )
        self.master.resizable(False, False)
        self.master.configure(bg=config.THEME_BG, padx=20, pady=20)

        menubar = tk.Menu(self.master)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(
            label="About",
            command=lambda: messagebox.showinfo(
                "About", "Brief instructions and project info"
            ),
        )
        menubar.add_cascade(label="Help", menu=help_menu)
        self.master.config(menu=menubar)

        self.style = ttk.Style(self.master)
        self.style.configure(
            "Question.TLabel",
            font=config.FONT_LARGE,
            background=config.THEME_BG,
        )
        self.style.configure("Answer.TButton", font=config.FONT_MEDIUM)
        self.style.configure(
            "Result.TLabel",
            font=config.FONT_MEDIUM,
            background=config.THEME_BG,
        )
        self.style.configure(
            "Small.TLabel",
            font=config.FONT_SMALL,
            background=config.THEME_BG,
        )

        self.question_label = ttk.Label(
            self.master, text="", style="Question.TLabel", wraplength=760
        )
        self.question_label.pack(pady=(10, 20))
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.pack(pady=(0, 10))
        self.progress_label = ttk.Label(
            self.master,
            text="",
            style="Result.TLabel",
        )
        self.progress_label.pack(pady=(0, 10))
        self.qprogress_label = ttk.Label(
            self.master,
            text="",
            style="Small.TLabel",
        )
        self.qprogress_label.pack()
        self.progress_bar = ttk.Progressbar(
            self.master, length=760, mode="determinate"
        )
        self.progress_bar.pack(pady=5)
        self.result_label = ttk.Label(
            self.master,
            text="",
            style="Result.TLabel",
        )
        self.result_label.pack(pady=20)
        self.nav_frame = ttk.Frame(self.master)
        self.nav_frame.pack(pady=10)
        self.back_button = ttk.Button(
            self.nav_frame,
            text="Back",
            command=self.go_back,
            style="Answer.TButton",
        )
        self.back_button.pack(side=tk.LEFT, padx=5)
        self.restart_button = ttk.Button(
            self.nav_frame,
            text="Restart",
            command=self.restart,
            style="Answer.TButton",
        )
        self.restart_button.pack(side=tk.LEFT, padx=5)
        self.back_button.pack_forget()
        self.restart_button.pack_forget()

    def clear_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def restart(self):
        """Reset the engine and UI so the user can start over."""
        self.engine.reset()
        self.current_question = None
        self.result_label.config(text="")
        self.progress_label.config(text="")
        self.qprogress_label.config(text="")
        self.progress_bar['value'] = 0
        self.restart_button.pack_forget()
        self.back_button.pack_forget()
        self.next_question()

    def display_question(self, question_id):
        qdata = next(q for q in self.questions if q.qid == question_id)
        self.question_label.config(text=qdata.text)
        self.clear_buttons()
        options = self.engine.get_possible_answers(question_id)
        for ans in options:
            button = ttk.Button(
                self.button_frame,
                text=ans,
                command=lambda a=ans: self.record_answer(a),
                style="Answer.TButton",
            )
            button.pack(side=tk.LEFT, padx=5, pady=5)

    def record_answer(self, answer):
        qid = self.current_question
        self.engine.answer_question(qid, answer)
        self.update_progress()
        self.next_question()

    def go_back(self):
        """Undo the last answer and show the previous question."""
        qid = self.engine.undo_last_answer()
        if qid is None:
            return
        self.result_label.config(text="")
        self.restart_button.pack_forget()
        self.current_question = qid
        self.display_question(qid)
        self.update_progress()

    def update_progress(self):
        scores = self.engine.get_scores()
        top = self.engine.get_top_diseases()
        prog = "\n".join([f"{d}: {scores[d]}" for d, _ in top])
        self.progress_label.config(text=f"Top Diagnoses:\n{prog}")
        answered = len(self.engine.answered)
        self.qprogress_label.config(
            text=f"Question {answered + 1} of {self.total_questions}"
        )
        percent = answered / self.total_questions * 100
        self.progress_bar['value'] = percent
        if self.engine.history:
            self.back_button.pack(side=tk.LEFT, padx=5)
        else:
            self.back_button.pack_forget()

    def next_question(self):
        if self.engine.is_done():
            self.question_label.config(text="Diagnosis complete.")
            self.clear_buttons()
            top = self.engine.get_top_diseases()
            text = "\n".join(
                [f"{d}: {score:.2f}" for d, score in top]
            )
            self.result_label.config(text="Most Likely Diagnoses:\n" + text)
            answered = len(self.engine.answered)
            self.qprogress_label.config(
                text=f"Question {answered} of {self.total_questions}"
            )
            self.progress_bar['value'] = 100
            self.restart_button.pack(side=tk.LEFT, padx=5)
            if self.engine.history:
                self.back_button.pack(side=tk.LEFT, padx=5)
            return
        qid = self.engine.select_best_question()
        if not qid:
            self.question_label.config(text="No more questions.")
            self.clear_buttons()
            return
        self.current_question = qid
        self.display_question(qid)
        self.update_progress()
