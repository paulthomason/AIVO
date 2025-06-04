
from tkinter import *
from tkinter import ttk
from engine_rule import DiagnosisEngine
from storage_json import load_questions, load_diseases, load_model

class DiagnosisUI:
    def __init__(self, master):
        self.master = master
        self.questions = load_questions()
        self.diseases = load_diseases()
        self.model = load_model()
        # ``load_questions`` now returns ``Question`` objects
        self.question_ids = [q.qid for q in self.questions]
        self.engine = DiagnosisEngine(self.diseases, self.question_ids, self.model)
        self.current_question = None
        self.total_questions = len(self.question_ids)
        self.init_ui()
        self.next_question()

    def init_ui(self):
        self.master.title("Vet Ophthalmology Diagnosis")
        self.master.geometry("800x480")
        self.master.resizable(False, False)
        self.question_label = Label(self.master, text="", font=("Arial", 24), wraplength=760)
        self.question_label.pack(pady=40)
        self.button_frame = Frame(self.master)
        self.button_frame.pack(pady=10)
        self.progress_label = Label(self.master, text="", font=("Arial", 16))
        self.progress_label.pack(pady=10)
        self.qprogress_label = Label(self.master, text="", font=("Arial", 14))
        self.qprogress_label.pack()
        self.progress_bar = ttk.Progressbar(self.master, length=760, mode="determinate")
        self.progress_bar.pack(pady=5)
        self.result_label = Label(self.master, text="", font=("Arial", 18, "bold"))
        self.result_label.pack(pady=20)
        self.restart_button = Button(self.master, text="Restart", font=("Arial", 14), command=self.restart)

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
        self.next_question()

    def display_question(self, question_id):
        qdata = next(q for q in self.questions if q.qid == question_id)
        self.question_label.config(text=qdata.text)
        self.clear_buttons()
        options = self.engine.get_possible_answers(question_id)
        for ans in options:
            b = Button(self.button_frame, text=ans, font=("Arial", 20), width=14, height=2,
                       command=lambda a=ans: self.record_answer(a))
            b.pack(side=LEFT, padx=10)

    def record_answer(self, answer):
        qid = self.current_question
        self.engine.answer_question(qid, answer)
        self.update_progress()
        self.next_question()

    def update_progress(self):
        scores = self.engine.get_scores()
        top = self.engine.get_top_diseases()
        prog = "\n".join([f"{d}: {scores[d]}" for d, _ in top])
        self.progress_label.config(text=f"Top Diagnoses:\n{prog}")
        answered = len(self.engine.answered)
        self.qprogress_label.config(text=f"Question {answered + 1} of {self.total_questions}")
        percent = answered / self.total_questions * 100
        self.progress_bar['value'] = percent

    def next_question(self):
        if self.engine.is_done():
            self.question_label.config(text="Diagnosis complete.")
            self.clear_buttons()
            top = self.engine.get_top_diseases()
            text = "\n".join([f"{d}: {score:.2f}" for d, score in top])
            self.result_label.config(text="Most Likely Diagnoses:\n" + text)
            answered = len(self.engine.answered)
            self.qprogress_label.config(text=f"Question {answered} of {self.total_questions}")
            self.progress_bar['value'] = 100
            self.restart_button.pack(pady=10)
            return
        qid = self.engine.select_best_question()
        if not qid:
            self.question_label.config(text="No more questions.")
            self.clear_buttons()
            return
        self.current_question = qid
        self.display_question(qid)
        self.update_progress()
