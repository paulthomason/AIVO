import os
import sys
import logging
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

import pytest  # noqa: E402
from storage_json import (  # noqa: E402
    load_questions,
    load_diseases,
    load_model,
)
from engine_rule import DiagnosisEngine  # noqa: E402


@pytest.fixture
def engine():
    questions = load_questions()
    q_ids = [q.qid for q in questions]
    return DiagnosisEngine(load_diseases(), q_ids, load_model())


def test_compute_entropy_decreases_after_answer(engine):
    before = engine.compute_entropy()
    engine.answer_question('red_eye', 'Yes')
    after = engine.compute_entropy()
    assert after < before


def test_answer_question_updates_scores(engine):
    engine.answer_question('red_eye', 'Yes')
    assert engine.scores['Conjunctivitis'] == 3
    assert engine.answered['red_eye'] == 'Yes'
    assert 'red_eye' not in engine.remaining_questions


def test_select_best_question_progression(engine):
    first = engine.select_best_question()
    assert first == 'red_eye'
    engine.answer_question(first, 'Yes')
    second = engine.select_best_question()
    assert second == 'vision_loss'


def test_entropy_with_zero_scores():
    eng = DiagnosisEngine(['D1', 'D2'], ['q1'], {'D1': {}, 'D2': {}})
    ent = eng.compute_entropy()
    assert ent == pytest.approx(math.log2(2))


def test_model_missing_weights_logs_warning(caplog):
    caplog.set_level(logging.WARNING)
    DiagnosisEngine(['D1'], ['q1', 'q2'], {'D1': {'q1': {'Yes': 1}}})
    assert any('missing weights' in r.message for r in caplog.records)


def test_undo_reverts_scores_and_history(engine):
    engine.answer_question('red_eye', 'Yes')
    assert engine.history == ['red_eye']
    engine.undo_last_answer()
    assert engine.history == []
    assert 'red_eye' not in engine.answered
    assert 'red_eye' in engine.remaining_questions
    for val in engine.scores.values():
        assert val == 0


def test_undo_returns_previous_question(engine):
    engine.answer_question('red_eye', 'Yes')
    engine.answer_question('pain', 'No')
    assert engine.history == ['red_eye', 'pain']
    qid = engine.undo_last_answer()
    assert qid == 'pain'
    assert engine.history == ['red_eye']
    assert 'pain' not in engine.answered


def test_negative_weight_rules_out_disease(engine):
    engine.answer_question('red_eye', 'No')
    assert engine.scores['Conjunctivitis'] == float('-inf')
    top = [d for d, _ in engine.get_top_diseases()]
    assert 'Conjunctivitis' not in top
    engine.undo_last_answer()
    assert engine.scores['Conjunctivitis'] == 0
