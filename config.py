"""Configuration helpers and defaults for the application."""

import os


def _get_env_or_default(name: str, default: str) -> str:
    """Return ``name`` from the environment or ``default`` if unset."""

    return os.getenv(name, default)


def get_env_int(name: str, default: int) -> int:
    """Return ``name`` converted to ``int`` or ``default`` on error."""

    val = os.getenv(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def get_env_bool(name: str, default: bool = False) -> bool:
    """Return ``name`` interpreted as a boolean."""

    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = _get_env_or_default("AIVO_DATA_DIR", os.path.join(BASE_DIR, "data"))
QUESTIONS_FILE = _get_env_or_default(
    "AIVO_QUESTIONS_FILE", os.path.join(DATA_DIR, "questions.json")
)
DISEASES_FILE = _get_env_or_default(
    "AIVO_DISEASES_FILE", os.path.join(DATA_DIR, "diseases.json")
)
DIAGNOSIS_MODEL_FILE = _get_env_or_default(
    "AIVO_DIAGNOSIS_MODEL_FILE", os.path.join(DATA_DIR, "diagnosis_model.json")
)

# Default UI configuration values.  AdminUI relies on these constants
# when sizing and styling its windows.  They previously did not exist
# which caused attribute errors on start up.
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
# Size of the diagnosis questionnaire window.  Can be overridden with
# ``AIVO_DIAG_SCREEN_WIDTH`` and ``AIVO_DIAG_SCREEN_HEIGHT`` environment
# variables which is helpful when running on small displays.
DIAG_SCREEN_WIDTH = get_env_int("AIVO_DIAG_SCREEN_WIDTH", 800)
DIAG_SCREEN_HEIGHT = get_env_int("AIVO_DIAG_SCREEN_HEIGHT", 480)
THEME_BG = "#f0f0f0"

# Font configuration used across the Tkinter interfaces. These
# consolidate the various hard-coded font tuples previously scattered
# throughout the UI modules which made the look and feel inconsistent.
FONT_LARGE = ("Helvetica", 24)
FONT_MEDIUM = ("Helvetica", 16)
FONT_SMALL = ("Helvetica", 14)
