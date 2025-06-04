import os
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
DISEASES_FILE = os.path.join(DATA_DIR, "diseases.json")
DIAGNOSIS_MODEL_FILE = os.path.join(DATA_DIR, "diagnosis_model.json")

# Default UI configuration values.  AdminUI relies on these constants
# when sizing and styling its windows.  They previously did not exist
# which caused attribute errors on start up.
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
THEME_BG = "#f0f0f0"
