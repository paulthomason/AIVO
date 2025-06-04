# AIVO: Veterinary Ophthalmology Diagnostic Tool

This project provides a simple rule-based system to assist in diagnosing canine eye diseases.
It asks the user a series of questions via a Tkinter GUI and ranks possible diagnoses
based on pre-defined weights stored in the `data/` folder. An administrative interface
is included for editing questions, diseases and diagnosis weights.

## Running the Diagnosis UI

Execute `main.py` with Python. A window will guide you through a set of
questions and display the most likely diseases at the end.

```bash
python main.py
```

## Launching the Admin Interface

The admin panel allows you to add or remove questions, manage diseases and
adjust the weight mapping used by the diagnostic engine. A search box makes it
easy to locate questions. Items can be reordered with **Move Up/Down** buttons
and all changes are saved using the **File** menu.
Launch it with:

```bash
python admin.py
```

## Debugging

The diagnostic engine supports debug logging. Set the environment variable
`AIVO_DEBUG=1` before running the UI or tests to see detailed log output.

## Dependencies

- Python 3.9 or later
- Tkinter must be available in your Python installation
  (it is included with most standard Python distributions)

No third‑party packages are required.
