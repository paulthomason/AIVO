"""Question model classes."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    """Represent a single question."""

    qid: str
    text: str
    qtype: str
    choices: Optional[List[str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        """Instantiate from a dictionary produced by ``to_dict``."""

        return cls(
            data["id"],
            data["text"],
            data["type"],
            data.get("choices", None)
        )

    def to_dict(self):
        """Return ``dict`` representation for JSON serialization."""

        d = {
            "id": self.qid,
            "text": self.text,
            "type": self.qtype,
        }
        if self.choices:
            d["choices"] = self.choices
        return d


class YesNoQuestion(Question):
    def __init__(self, qid, text):
        super().__init__(qid, text, "yesno", ["Yes", "No"])


class MultiChoiceQuestion(Question):
    def __init__(self, qid, text, choices):
        super().__init__(qid, text, "multichoice", choices)
