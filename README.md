# AIVO: Veterinary Ophthalmology Diagnostic Tool

This project provides a simple rule-based system to assist in diagnosing canine eye diseases.
It asks the user a series of questions via a Tkinter GUI and ranks possible diagnoses
based on pre-defined weights stored in the `data/` folder. An administrative interface
is included for editing questions, diseases and diagnosis weights.

## Running the Diagnosis UI

Execute `main.py` with Python. A window will guide you through a set of
questions and display the most likely diseases at the end.
The window includes a **Help** menu with an About dialog summarizing
how to use the tool.

```bash
python main.py
```

## Launching the Admin Interface

The admin panel allows you to add or remove questions, manage diseases and
adjust the weight mapping used by the diagnostic engine. A search box makes it
easy to locate questions. Items can be reordered with **Move Up/Down** buttons
and all changes are saved using the **File** menu. A **Training** tab lets you
quickly rate how strongly each question is associated with a disease using a
slider from -1 to 5. A rating of -1 means the answer rules out the disease.
Use **Random Pair** to pick a disease/question combination, then
click **Record Rating** and **Save All** to persist the new weights.
Launch it with:

```bash
python admin.py
```

## Data Format

All application data lives in the `data/` directory. It contains three JSON
files:

- `questions.json` – list of questions with optional multiple choice options.
- `diseases.json` – array of disease names.
- `diagnosis_model.json` – nested mapping of disease -> question -> answer -> weight.

You can modify these files directly or use the admin interface which ensures the
structure remains valid.

## Debugging

The diagnostic engine supports debug logging. Set the environment variable
`AIVO_DEBUG=1` before running the UI or tests to see detailed log output.

The size of the diagnosis window can also be adjusted with environment
variables. Set `AIVO_DIAG_SCREEN_WIDTH` and `AIVO_DIAG_SCREEN_HEIGHT`
to override the default 800x480 geometry used by the questionnaire UI.

## Dependencies

- Python 3.9 or later
- Tkinter must be available in your Python installation
  (it is included with most standard Python distributions)

No third‑party packages are required.

## Contributing

Pull requests are welcome! Please ensure that unit tests continue to pass by
running `pytest` before submitting. Feel free to open issues if you encounter
problems or have suggestions for improvement.
