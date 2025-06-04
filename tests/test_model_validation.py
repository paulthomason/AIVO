import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

from storage_json import load_questions, load_diseases, load_model  # noqa: E402


def test_model_has_mappings_for_all_questions_and_valid_answers():
    questions = load_questions()
    diseases = load_diseases()
    model = load_model()

    choices = {q.qid: (q.choices if q.choices else ["Yes", "No"]) for q in questions}

    for disease in diseases:
        assert disease in model
        for qid, valid_choices in choices.items():
            assert qid in model[disease], f"{disease} missing mapping for {qid}"
            used_choices = set(model[disease][qid].keys())
            assert used_choices.issubset(set(valid_choices)), (
                f"{disease}/{qid} has invalid answers {used_choices - set(valid_choices)}"
            )
