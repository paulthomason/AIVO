import json
from typing import Iterable, List

from config import QUESTIONS_FILE, DISEASES_FILE, DIAGNOSIS_MODEL_FILE
from questions import Question


def load_questions() -> List[Question]:
    """Load questions from disk and return ``Question`` objects."""

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load questions: {exc}") from exc
    return [Question.from_dict(q) for q in data]


def load_diseases() -> List[str]:
    """Return the list of diseases from disk."""

    try:
        with open(DISEASES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load diseases: {exc}") from exc


def load_model() -> dict:
    """Return the diagnosis model mapping."""

    try:
        with open(DIAGNOSIS_MODEL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load model: {exc}") from exc


def save_questions(questions: Iterable[Question]) -> None:
    """Persist questions to ``QUESTIONS_FILE``."""

    data = [q.to_dict() for q in questions]
    try:
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        raise RuntimeError(f"Failed to save questions: {exc}") from exc


def save_diseases(diseases: Iterable[str]) -> None:
    """Write the diseases list back to disk."""

    try:
        with open(DISEASES_FILE, "w", encoding="utf-8") as f:
            json.dump(list(diseases), f, indent=2)
    except OSError as exc:
        raise RuntimeError(f"Failed to save diseases: {exc}") from exc


def save_model(model: dict) -> None:
    """Persist the diagnosis model mapping."""

    try:
        with open(DIAGNOSIS_MODEL_FILE, "w", encoding="utf-8") as f:
            json.dump(model, f, indent=2)
    except OSError as exc:
        raise RuntimeError(f"Failed to save model: {exc}") from exc
