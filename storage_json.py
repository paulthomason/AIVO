import json
from typing import Iterable, List

from config import QUESTIONS_FILE, DISEASES_FILE, DIAGNOSIS_MODEL_FILE
from questions import Question


class JSONStorage:
    """Helper class for reading/writing project JSON files."""

    def __init__(self,
                 questions_file: str = QUESTIONS_FILE,
                 diseases_file: str = DISEASES_FILE,
                 diagnosis_model_file: str = DIAGNOSIS_MODEL_FILE) -> None:
        self.questions_file = questions_file
        self.diseases_file = diseases_file
        self.diagnosis_model_file = diagnosis_model_file

    # ------------------------------------------------------------------
    # Questions helpers
    def load_questions(self) -> List[Question]:
        """Load questions and return ``Question`` objects."""
        with open(self.questions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Question.from_dict(q) for q in data]

    def save_questions(self, questions: Iterable[Question]) -> None:
        """Persist questions to disk."""
        data = [q.to_dict() for q in questions]
        with open(self.questions_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------
    # Diseases helpers
    def load_diseases(self) -> List[str]:
        """Return the list of diseases."""
        with open(self.diseases_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_diseases(self, diseases: Iterable[str]) -> None:
        """Write the diseases list back to disk."""
        with open(self.diseases_file, "w", encoding="utf-8") as f:
            json.dump(list(diseases), f, indent=2)

    # ------------------------------------------------------------------
    # Diagnosis model helpers
    def load_diagnosis_model(self) -> dict:
        """Return the diagnosis model mapping."""
        with open(self.diagnosis_model_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_diagnosis_model(self, model: dict) -> None:
        """Persist the diagnosis model mapping."""
        with open(self.diagnosis_model_file, "w", encoding="utf-8") as f:
            json.dump(model, f, indent=2)

# Default storage used by the module level helper functions below
_default_storage = JSONStorage()


def load_questions() -> List[Question]:
    """Load questions using the default storage instance."""
    return _default_storage.load_questions()


def save_questions(questions: Iterable[Question]) -> None:
    """Persist questions using the default storage instance."""
    _default_storage.save_questions(questions)


def load_diseases() -> List[str]:
    """Load diseases using the default storage instance."""
    return _default_storage.load_diseases()


def save_diseases(diseases: Iterable[str]) -> None:
    """Persist diseases using the default storage instance."""
    _default_storage.save_diseases(diseases)


def load_model() -> dict:
    """Backward compatible wrapper for loading the diagnosis model."""
    return _default_storage.load_diagnosis_model()


def save_model(model: dict) -> None:
    """Backward compatible wrapper for saving the diagnosis model."""
    _default_storage.save_diagnosis_model(model)
