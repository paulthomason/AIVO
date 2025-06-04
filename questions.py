
class Question:
    def __init__(self, qid, text, qtype, choices=None):
        self.qid = qid
        self.text = text
        self.qtype = qtype
        self.choices = choices or []

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["text"],
            data["type"],
            data.get("choices", None)
        )

    def to_dict(self):
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
