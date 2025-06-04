import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import math
import pytest
from storage_json import load_questions, load_diseases, load_model
from engine_rule import DiagnosisEngine

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
    assert second == 'pain'
