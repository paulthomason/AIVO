import json
from config import QUESTIONS_FILE, DISEASES_FILE, DIAGNOSIS_MODEL_FILE

def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_diseases():
    with open(DISEASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_model():
    with open(DIAGNOSIS_MODEL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
