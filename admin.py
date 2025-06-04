import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from config import SCREEN_WIDTH, SCREEN_HEIGHT, THEME_BG
from questions import Question, YesNoQuestion, MultiChoiceQuestion

class AdminUI(tk.Tk):
    def __init__(self, storage):
        super().__init__()
        self.title("Admin Panel - Veterinary Ophthalmology")
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=THEME_BG)
        self.storage = storage
        # ``storage`` is expected to provide load/save helpers.  It previously
        # returned raw dictionaries which caused numerous attribute errors
        # throughout the UI.  ``load_questions`` now yields ``Question``
        # objects so we can work with them directly.
        self.questions = storage.load_questions()
        self.diseases = storage.load_diseases()
        self.diagnosis_model = storage.load_model()
        self.create_widgets()

    def create_widgets(self):
        nb = ttk.Notebook(self)
        nb.pack(expand=1, fill=tk.BOTH)
        # Questions tab
        frm_q = tk.Frame(nb, bg=THEME_BG)
        nb.add(frm_q, text="Questions")
        self.q_listbox = tk.Listbox(frm_q, font=("Arial", 16), width=55)
        self.q_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.refresh_q_list()
        btns_q = tk.Frame(frm_q, bg=THEME_BG)
        btns_q.pack(side=tk.LEFT, padx=6)
        tk.Button(btns_q, text="Add", command=self.add_q, font=("Arial", 16)).pack(fill=tk.X)
        tk.Button(btns_q, text="Edit", command=self.edit_q, font=("Arial", 16)).pack(fill=tk.X)
        tk.Button(btns_q, text="Delete", command=self.del_q, font=("Arial", 16)).pack(fill=tk.X)
        # Diseases tab
        frm_d = tk.Frame(nb, bg=THEME_BG)
        nb.add(frm_d, text="Diseases")
        self.d_listbox = tk.Listbox(frm_d, font=("Arial", 16), width=35)
        self.d_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.refresh_d_list()
        btns_d = tk.Frame(frm_d, bg=THEME_BG)
        btns_d.pack(side=tk.LEFT, padx=6)
        tk.Button(btns_d, text="Add", command=self.add_d, font=("Arial", 16)).pack(fill=tk.X)
        tk.Button(btns_d, text="Edit", command=self.edit_d, font=("Arial", 16)).pack(fill=tk.X)
        tk.Button(btns_d, text="Delete", command=self.del_d, font=("Arial", 16)).pack(fill=tk.X)
        # Weights tab
        frm_w = tk.Frame(nb, bg=THEME_BG)
        nb.add(frm_w, text="Weights")
        tk.Label(frm_w, text="Select disease, question, and assign weights per answer.", font=("Arial", 16), bg=THEME_BG).pack()
        frm_top = tk.Frame(frm_w, bg=THEME_BG)
        frm_top.pack()
        self.disease_combo = ttk.Combobox(frm_top, values=self.diseases, font=("Arial", 14))
        self.disease_combo.pack(side=tk.LEFT, padx=7)
        self.disease_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_weight_q())
        self.q_combo = ttk.Combobox(frm_top, values=[q.qid for q in self.questions], font=("Arial", 14))
        self.q_combo.pack(side=tk.LEFT, padx=7)
        self.q_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_weight_q())
        self.ans_frame = tk.Frame(frm_w, bg=THEME_BG)
        self.ans_frame.pack(pady=10)
        tk.Button(frm_w, text="Set Weight", command=self.set_weight, font=("Arial", 14)).pack()
        tk.Button(self, text="Save All", command=self.save_all, font=("Arial", 14)).pack(pady=5)

    def refresh_q_list(self):
        self.q_listbox.delete(0, tk.END)
        for q in self.questions:
            txt = f"{q.qid}: {q.text} ({q.qtype})"
            self.q_listbox.insert(tk.END, txt)

    def refresh_d_list(self):
        self.d_listbox.delete(0, tk.END)
        for d in self.diseases:
            self.d_listbox.insert(tk.END, d)

    def add_q(self):
        qid = simpledialog.askstring("Question ID", "ID (no spaces):")
        if not qid:
            return
        qtext = simpledialog.askstring("Question Text", "Enter question:")
        if not qtext:
            return
        qtype = simpledialog.askstring("Type", "Type (yesno/multichoice):")
        if qtype == "yesno":
            q = YesNoQuestion(qid, qtext)
        else:
            choices = simpledialog.askstring("Choices", "Choices (comma separated):")
            q = MultiChoiceQuestion(qid, qtext, [c.strip() for c in choices.split(",")])
        self.questions.append(q)
        self.refresh_q_list()

    def edit_q(self):
        idx = self.q_listbox.curselection()
        if not idx:
            return
        q = self.questions[idx[0]]
        qtext = simpledialog.askstring("Edit Text", "Question text:", initialvalue=q.text)
        if q.qtype == "yesno":
            q2 = YesNoQuestion(q.qid, qtext)
        else:
            choices = simpledialog.askstring("Choices", "Choices (comma separated):", initialvalue=",".join(q.choices))
            q2 = MultiChoiceQuestion(q.qid, qtext, [c.strip() for c in choices.split(",")])
        self.questions[idx[0]] = q2
        self.refresh_q_list()

    def del_q(self):
        idx = self.q_listbox.curselection()
        if not idx:
            return
        del self.questions[idx[0]]
        self.refresh_q_list()

    def add_d(self):
        d = simpledialog.askstring("Add Disease", "Disease name:")
        if d and d not in self.diseases:
            self.diseases.append(d)
            self.refresh_d_list()

    def edit_d(self):
        idx = self.d_listbox.curselection()
        if not idx:
            return
        d = self.diseases[idx[0]]
        d2 = simpledialog.askstring("Edit Disease", "Disease name:", initialvalue=d)
        if d2:
            self.diseases[idx[0]] = d2
            self.refresh_d_list()

    def del_d(self):
        idx = self.d_listbox.curselection()
        if not idx:
            return
        del self.diseases[idx[0]]
        self.refresh_d_list()

    def refresh_weight_q(self):
        for widget in self.ans_frame.winfo_children():
            widget.destroy()
        d = self.disease_combo.get()
        qid = self.q_combo.get()
        if not d or not qid:
            return
        q = next((x for x in self.questions if x.qid == qid), None)
        if not q:
            return
        wdict = self.diagnosis_model.get(d, {}).get(qid, {})
        if q.qtype == "yesno":
            choices = ["Yes", "No"]
        else:
            choices = q.choices
        self.weight_vars = {}
        for c in choices:
            var = tk.IntVar(value=wdict.get(c, 0))
            tk.Label(self.ans_frame, text=c, font=("Arial", 14), bg=THEME_BG).pack()
            tk.Entry(self.ans_frame, textvariable=var, font=("Arial", 14), width=8).pack()
            self.weight_vars[c] = var

    def set_weight(self):
        d = self.disease_combo.get()
        qid = self.q_combo.get()
        if not d or not qid:
            return
        if d not in self.diagnosis_model:
            self.diagnosis_model[d] = {}
        if qid not in self.diagnosis_model[d]:
            self.diagnosis_model[d][qid] = {}
        for c, var in self.weight_vars.items():
            self.diagnosis_model[d][qid][c] = var.get()
        messagebox.showinfo("Saved", "Weight updated.")

    def save_all(self):
        # Persist all modifications back to disk using the storage helpers.
        self.storage.save_questions(self.questions)
        self.storage.save_diseases(self.diseases)
        self.storage.save_model(self.diagnosis_model)
        messagebox.showinfo("Saved", "All data saved!")
