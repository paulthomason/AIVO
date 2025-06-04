"""Rule based diagnostic engine."""

import logging
import math
from copy import deepcopy


class DiagnosisEngine:
    """Perform simple rule based disease ranking."""

    def __init__(self, diseases, questions, model, *, debug: bool = False):
        self.diseases = diseases
        self.questions = questions
        self.model = model
        self.debug = debug
        self.logger = logging.getLogger(self.__class__.__name__)
        if self.debug and not logging.getLogger().handlers:
            logging.basicConfig(level=logging.DEBUG)
        self.logger.debug("Engine initialised")
        self.history = []
        self._validate_model()
        self.reset()

    def _validate_model(self) -> None:
        """Log a warning if ``model`` lacks weights for known questions."""

        for d in self.diseases:
            for q in self.questions:
                if q not in self.model.get(d, {}):
                    self.logger.warning("Model missing weights for %s/%s", d, q)

    def reset(self):
        self.scores = {d: 0 for d in self.diseases}
        self.answered = {}
        self.remaining_questions = set(self.questions)
        self.history = []
        self.eliminated = {d: 0 for d in self.diseases}
        self._prev_scores = {}
        self.logger.debug("State reset")

    def answer_question(self, question, answer):
        self.answered[question] = answer
        self.remaining_questions.discard(question)
        self.history.append(question)
        for disease in self.diseases:
            if question not in self.model[disease]:
                continue
            weight = self.model[disease][question].get(answer, 0)
            if weight == -1:
                if self.eliminated[disease] == 0:
                    self._prev_scores[disease] = self.scores[disease]
                    self.scores[disease] = float('-inf')
                self.eliminated[disease] += 1
            elif self.eliminated[disease] == 0:
                self.scores[disease] += weight
        self.logger.debug("Answered %s=%s", question, answer)

    def compute_entropy(self, scores=None):
        """Return the Shannon entropy of ``scores``.

        Parameters
        ----------
        scores: dict or None
            Mapping of disease name to numeric score. If ``None`` the current
            engine scores are used.
        """

        scores = scores if scores is not None else self.scores
        active = [s for s in scores.values() if not math.isinf(s)]
        values = [max(0, s) for s in active]
        total = sum(values)
        if total == 0 or not active:
            return math.log2(len(active)) if len(active) else 0
        probs = [v / total for v in values]
        ent = -sum(p * math.log2(p) for p in probs if p > 0)
        self.logger.debug("Entropy computed: %.4f", ent)
        return ent

    def get_possible_answers(self, question):
        for d in self.diseases:
            if question in self.model[d]:
                return list(self.model[d][question].keys())
        return ["Yes", "No"]

    def simulate_answer(self, scores, question, answer):
        sim_scores = deepcopy(scores)
        for disease in self.diseases:
            if question not in self.model[disease]:
                continue
            weight = self.model[disease][question].get(answer, 0)
            if weight == -1:
                sim_scores[disease] = float('-inf')
            elif not math.isinf(sim_scores[disease]):
                sim_scores[disease] += weight
        return sim_scores

    def information_gain_for_question(self, question):
        """Calculate expected information gain for ``question``."""

        answers = self.get_possible_answers(question)
        entropies = []
        num_answers = len(answers)
        for answer in answers:
            sim_scores = self.simulate_answer(self.scores, question, answer)
            ent = self.compute_entropy(sim_scores)
            entropies.append(ent)
        expected_entropy = sum(entropies) / num_answers if num_answers else 0
        current_entropy = self.compute_entropy()
        info_gain = current_entropy - expected_entropy
        self.logger.debug("Info gain for %s: %.4f", question, info_gain)
        return info_gain

    def select_best_question(self):
        best_q = None
        best_ig = -float('inf')
        for q in self.remaining_questions:
            ig = self.information_gain_for_question(q)
            if ig > best_ig:
                best_q = q
                best_ig = ig
        self.logger.debug("Best next question: %s (IG=%.4f)", best_q, best_ig)
        return best_q

    def get_top_diseases(self, n=3):
        active = {d: s for d, s in self.scores.items() if not math.isinf(s)}
        top = sorted(active.items(), key=lambda x: x[1], reverse=True)[:n]
        self.logger.debug("Top diseases: %s", top)
        return top

    def get_scores(self):
        return {d: s for d, s in self.scores.items() if not math.isinf(s)}

    def get_progress(self):
        active = {d: s for d, s in self.scores.items() if not math.isinf(s)}
        max_score = max(active.values()) if active else 1
        return {d: (s / max_score if max_score else 0) for d, s in active.items()}

    def is_done(self, max_questions=25):
        done = len(self.answered) >= max_questions or not self.remaining_questions
        self.logger.debug("Is done? %s", done)
        return done

    def get_state(self):
        state = {
            "scores": deepcopy(self.scores),
            "answered": deepcopy(self.answered),
            "remaining_questions": list(self.remaining_questions),
            "history": list(self.history),
        }
        self.logger.debug("Current state: %s", state)
        return state

    def undo_last_answer(self):
        """Revert the most recently answered question."""

        if not self.history:
            self.logger.debug("Undo called with empty history")
            return None
        question = self.history.pop()
        answer = self.answered.pop(question, None)
        if answer is None:
            return None
        for disease in self.diseases:
            if question not in self.model[disease]:
                continue
            weight = self.model[disease][question].get(answer, 0)
            if weight == -1:
                if self.eliminated[disease] > 0:
                    self.eliminated[disease] -= 1
                    if self.eliminated[disease] == 0:
                        self.scores[disease] = self._prev_scores.pop(disease, 0)
                        # Score restored to value prior to elimination
                    else:
                        self.scores[disease] = float('-inf')
            elif self.eliminated[disease] == 0:
                self.scores[disease] -= weight
        self.remaining_questions.add(question)
        self.logger.debug("Undid %s=%s", question, answer)
        return question
