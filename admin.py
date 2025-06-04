import tkinter as tk
"""Administrative interface for managing questions and diseases.

This module provides a Tkinter-based GUI that allows subject matter
experts to maintain the data files used by the diagnostic tool. No
programming knowledge is required. Launch the application from the
command line with ``python admin.py`` and use the tabs to edit
questions, diseases and diagnosis weights. All changes are stored in
JSON files under the ``data/`` directory.
"""

from tkinter import simpledialog, messagebox, ttk, TclError
import os
import sys
import config
from questions import YesNoQuestion, MultiChoiceQuestion


class AdminUI(tk.Tk):
    """Tkinter window used to edit the application's data files."""

    def __init__(self, storage):
        super().__init__()
        self.title("Admin Panel - Veterinary Ophthalmology")
        self.geometry(f"{config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=config.THEME_BG)
        self.storage = storage
        # ``storage`` is expected to provide load/save helpers.  It previously
        # returned raw dictionaries which caused numerous attribute errors
        # throughout the UI.  ``load_questions`` now yields ``Question``
        # objects so we can work with them directly.
        self.questions = storage.load_questions()
        self.diseases = storage.load_diseases()
        self.diagnosis_model = storage.load_model()
        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Save All", command=self.save_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def create_widgets(self):
        """Build the tabbed interface and main controls."""
        self.nb = ttk.Notebook(self)
        self.nb.pack(expand=1, fill=tk.BOTH)

        self.create_questions_tab()
        self.create_diseases_tab()
        self.create_weights_tab()
        self.create_training_tab()
        tk.Button(self, text="Save All", command=self.save_all, font=config.FONT_SMALL).pack(pady=5)

    def create_questions_tab(self):
        """Set up the Questions tab used to manage survey questions."""
        frm_q = tk.Frame(self.nb, bg=config.THEME_BG)
        self.nb.add(frm_q, text="Questions")

        search_frame = tk.Frame(frm_q, bg=config.THEME_BG)
        search_frame.pack(fill=tk.X, padx=6, pady=(6, 0))
        tk.Label(search_frame, text="Search:", bg=config.THEME_BG, font=config.FONT_SMALL).pack(side=tk.LEFT)
        self.q_search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.q_search_var, font=config.FONT_SMALL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.q_search_var.trace_add("write", lambda *a: self.refresh_q_list())

        self.q_listbox = tk.Listbox(frm_q, font=config.FONT_MEDIUM, width=55)
        self.q_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)
        q_scroll = tk.Scrollbar(frm_q, orient=tk.VERTICAL, command=self.q_listbox.yview)
        q_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.q_listbox.config(yscrollcommand=q_scroll.set)
        self.refresh_q_list()

        btns_q = tk.Frame(frm_q, bg=config.THEME_BG)
        btns_q.pack(side=tk.LEFT, padx=6)
        for txt, cmd in [
            ("Add", self.add_q),
            ("Edit", self.edit_q),
            ("Move Up", self.move_q_up),
            ("Move Down", self.move_q_down),
            ("Delete", self.del_q),
        ]:
            tk.Button(btns_q, text=txt, command=cmd, font=config.FONT_MEDIUM).pack(fill=tk.X)
        tk.Button(btns_q, text="Tips", command=self.show_q_tips, font=config.FONT_MEDIUM).pack(fill=tk.X, pady=(10, 0))

    def create_diseases_tab(self):
        """Set up the Diseases tab for editing the disease list."""
        frm_d = tk.Frame(self.nb, bg=config.THEME_BG)
        self.nb.add(frm_d, text="Diseases")

        self.d_listbox = tk.Listbox(frm_d, font=config.FONT_MEDIUM, width=35)
        self.d_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)
        d_scroll = tk.Scrollbar(frm_d, orient=tk.VERTICAL, command=self.d_listbox.yview)
        d_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.d_listbox.config(yscrollcommand=d_scroll.set)
        self.refresh_d_list()

        btns_d = tk.Frame(frm_d, bg=config.THEME_BG)
        btns_d.pack(side=tk.LEFT, padx=6)
        for txt, cmd in [
            ("Add", self.add_d),
            ("Edit", self.edit_d),
            ("Move Up", self.move_d_up),
            ("Move Down", self.move_d_down),
            ("Delete", self.del_d),
        ]:
            tk.Button(btns_d, text=txt, command=cmd, font=config.FONT_MEDIUM).pack(fill=tk.X)
        tk.Button(btns_d, text="Tips", command=self.show_d_tips, font=config.FONT_MEDIUM).pack(fill=tk.X, pady=(10, 0))

    def create_weights_tab(self):
        """Create the Weights tab for assigning scoring weights."""
        frm_w = tk.Frame(self.nb, bg=config.THEME_BG)
        self.nb.add(frm_w, text="Weights")

        tk.Label(
            frm_w,
            text="Select disease, question, and assign weights per answer.",
            font=config.FONT_MEDIUM,
            bg=config.THEME_BG,
        ).pack()
        tk.Label(
            frm_w,
            text=(
                "Weights express how strongly an answer suggests a disease. "
                "Positive values increase the score while negative values "
                "decrease it. The diagnosis totals the weights for all "
                "answers and selects the disease with the highest score."
            ),
            font=config.FONT_SMALL,
            bg=config.THEME_BG,
            wraplength=900,
            justify=tk.LEFT,
        ).pack(padx=6, pady=(0, 10))
        frm_top = tk.Frame(frm_w, bg=config.THEME_BG)
        frm_top.pack()
        self.disease_combo = ttk.Combobox(frm_top, values=self.diseases, font=config.FONT_SMALL)
        self.disease_combo.pack(side=tk.LEFT, padx=7)
        self.disease_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_weight_q())
        self.q_combo = ttk.Combobox(frm_top, values=[q.qid for q in self.questions], font=config.FONT_SMALL)
        self.q_combo.pack(side=tk.LEFT, padx=7)
        self.q_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_weight_q())
        self.ans_frame = tk.Frame(frm_w, bg=config.THEME_BG)
        self.ans_frame.pack(pady=10)
        tk.Button(frm_w, text="Set Weight", command=self.set_weight, font=config.FONT_SMALL).pack()
        tk.Button(frm_w, text="Tips", command=self.show_w_tips, font=config.FONT_SMALL).pack(pady=(10, 0))

    def create_training_tab(self):
        """Create a Training tab for rating question associations."""
        frm_t = tk.Frame(self.nb, bg=config.THEME_BG)
        self.nb.add(frm_t, text="Training")

        tk.Label(
            frm_t,
            text="Rate how strongly a question indicates a disease (0 = none, 5 = strong).",
            font=config.FONT_SMALL,
            bg=config.THEME_BG,
            wraplength=900,
            justify=tk.LEFT,
        ).pack(padx=6, pady=(6, 10))

        top = tk.Frame(frm_t, bg=config.THEME_BG)
        top.pack(pady=5)
        tk.Label(top, text="Disease:", bg=config.THEME_BG, font=config.FONT_SMALL).pack(side=tk.LEFT)
        self.train_disease = ttk.Combobox(top, values=self.diseases, font=config.FONT_SMALL, width=35)
        self.train_disease.pack(side=tk.LEFT, padx=5)
        self.train_disease.bind("<<ComboboxSelected>>", lambda e: self.update_training_prompt())
        tk.Label(top, text="Question:", bg=config.THEME_BG, font=config.FONT_SMALL).pack(side=tk.LEFT)
        self.train_question = ttk.Combobox(top, values=[q.qid for q in self.questions], font=config.FONT_SMALL, width=20)
        self.train_question.pack(side=tk.LEFT, padx=5)
        self.train_question.bind("<<ComboboxSelected>>", lambda e: self.update_training_prompt())

        self.training_prompt_lbl = tk.Label(frm_t, text="", font=config.FONT_MEDIUM, bg=config.THEME_BG, wraplength=900, justify=tk.LEFT)
        self.training_prompt_lbl.pack(pady=10)

        self.rating_var = tk.IntVar(value=0)
        self.rating_scale = tk.Scale(frm_t, from_=0, to=5, orient=tk.HORIZONTAL, variable=self.rating_var, length=400)
        self.rating_scale.pack()

        tk.Button(frm_t, text="Record Rating", command=self.save_training_rating, font=config.FONT_SMALL).pack(pady=(5, 0))
        tk.Button(frm_t, text="Tips", command=self.show_training_tips, font=config.FONT_SMALL).pack(pady=(10, 0))

    def update_training_prompt(self):
        """Update the text prompt based on combobox selection."""
        d = self.train_disease.get()
        qid = self.train_question.get()
        if not d or not qid:
            self.training_prompt_lbl.config(text="")
            return
        q = next((x for x in self.questions if x.qid == qid), None)
        if not q:
            self.training_prompt_lbl.config(text="")
            return
        self.training_prompt_lbl.config(text=f"Is {d} characterized by {q.text}?")

    def save_training_rating(self):
        """Persist the training rating back into the model."""
        d = self.train_disease.get()
        qid = self.train_question.get()
        if not d or not qid:
            return
        rating = self.rating_var.get()
        if d not in self.diagnosis_model:
            self.diagnosis_model[d] = {}
        if qid not in self.diagnosis_model[d]:
            self.diagnosis_model[d][qid] = {}
        q = next((x for x in self.questions if x.qid == qid), None)
        if q and q.qtype == "yesno":
            key = "Yes"
        elif q and q.choices:
            key = q.choices[0]
        else:
            key = "Yes"
        self.diagnosis_model[d][qid][key] = rating
        messagebox.showinfo("Saved", "Rating recorded.")

    def show_training_tips(self):
        """Show help for the Training tab."""
        messagebox.showinfo(
            "Training Tips",
            "Select a disease and question then drag the slider to set how strongly the question suggests the disease."
            " Click Record Rating to store the value and Save All when finished.",
        )

    def refresh_q_list(self):
        """Refresh the list of questions, applying any search filter."""
        self.q_listbox.delete(0, tk.END)
        search = self.q_search_var.get().lower() if hasattr(self, "q_search_var") else ""
        for q in self.questions:
            if search and search not in q.qid.lower() and search not in q.text.lower():
                continue
            txt = f"{q.qid}: {q.text} ({q.qtype})"
            self.q_listbox.insert(tk.END, txt)

    def refresh_d_list(self):
        """Populate the diseases list box."""
        self.d_listbox.delete(0, tk.END)
        for d in self.diseases:
            self.d_listbox.insert(tk.END, d)

    def add_q(self):
        """Prompt the user to create a new question."""
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
        """Edit the currently selected question."""
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
        """Remove the selected question after confirmation."""
        idx = self.q_listbox.curselection()
        if not idx:
            return
        if not messagebox.askyesno("Confirm", "Delete selected question?"):
            return
        del self.questions[idx[0]]
        self.refresh_q_list()

    def move_q_up(self):
        """Move the selected question up in the list."""
        idx = self.q_listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        self.questions[i - 1], self.questions[i] = self.questions[i], self.questions[i - 1]
        self.refresh_q_list()
        self.q_listbox.select_set(i - 1)

    def move_q_down(self):
        """Move the selected question down in the list."""
        idx = self.q_listbox.curselection()
        if not idx or idx[0] >= len(self.questions) - 1:
            return
        i = idx[0]
        self.questions[i + 1], self.questions[i] = self.questions[i], self.questions[i + 1]
        self.refresh_q_list()
        self.q_listbox.select_set(i + 1)

    def add_d(self):
        """Add a new disease entry."""
        d = simpledialog.askstring("Add Disease", "Disease name:")
        if d and d not in self.diseases:
            self.diseases.append(d)
            self.refresh_d_list()

    def edit_d(self):
        """Rename the selected disease."""
        idx = self.d_listbox.curselection()
        if not idx:
            return
        d = self.diseases[idx[0]]
        d2 = simpledialog.askstring("Edit Disease", "Disease name:", initialvalue=d)
        if d2:
            self.diseases[idx[0]] = d2
            self.refresh_d_list()

    def del_d(self):
        """Delete the chosen disease after confirmation."""
        idx = self.d_listbox.curselection()
        if not idx:
            return
        if not messagebox.askyesno("Confirm", "Delete selected disease?"):
            return
        del self.diseases[idx[0]]
        self.refresh_d_list()

    def move_d_up(self):
        """Move the selected disease up."""
        idx = self.d_listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        self.diseases[i - 1], self.diseases[i] = self.diseases[i], self.diseases[i - 1]
        self.refresh_d_list()
        self.d_listbox.select_set(i - 1)

    def move_d_down(self):
        """Move the selected disease down."""
        idx = self.d_listbox.curselection()
        if not idx or idx[0] >= len(self.diseases) - 1:
            return
        i = idx[0]
        self.diseases[i + 1], self.diseases[i] = self.diseases[i], self.diseases[i + 1]
        self.refresh_d_list()
        self.d_listbox.select_set(i + 1)

    def refresh_weight_q(self):
        """Display weight entry boxes for the selected disease/question."""
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
            tk.Label(self.ans_frame, text=c, font=config.FONT_SMALL, bg=config.THEME_BG).pack()
            tk.Entry(self.ans_frame, textvariable=var, font=config.FONT_SMALL, width=8).pack()
            self.weight_vars[c] = var

    def set_weight(self):
        """Save the weights entered in the Weights tab."""
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
        """Persist all modifications back to disk."""
        # Persist all modifications back to disk using the storage helpers.
        self.storage.save_questions(self.questions)
        self.storage.save_diseases(self.diseases)
        self.storage.save_model(self.diagnosis_model)
        messagebox.showinfo("Saved", "All data saved!")

    def show_about(self):
        """Display basic help and usage instructions."""
        messagebox.showinfo(
            "About",
            """This admin panel lets you maintain the questions, diseases \
and weighting model used by the diagnostic tool. Use the tabs above \
to add or edit data and click \"Save All\" when finished.""",
        )

    def show_q_tips(self):
        """Show usage tips for the Questions tab."""
        messagebox.showinfo(
            "Questions Tips",
            "Use the Add button to create new questions. Move Up/Down reorders "
            "the list. Remember to Save All when finished.",
        )

    def show_d_tips(self):
        """Show usage tips for the Diseases tab."""
        messagebox.showinfo(
            "Diseases Tips",
            "Add diseases with unique names. Use Edit to rename and Delete to remove.",
        )

    def show_w_tips(self):
        """Show usage tips for the Weights tab."""
        messagebox.showinfo(
            "Weights Tips",
            "Select a disease and question, enter numeric weights for each answer. "
            "Higher numbers mean a stronger link to the disease while negative "
            "weights reduce the likelihood. Click Set Weight to record your "
            "values and Save All when finished.",
        )


if __name__ == "__main__":
    import storage_json

    if os.name != "nt" and not os.getenv("DISPLAY"):
        sys.exit("Error: no DISPLAY environment variable set")
    try:
        app = AdminUI(storage_json)
    except TclError as exc:
        sys.exit(f"Error initializing Tkinter: {exc}")

    app.mainloop()
