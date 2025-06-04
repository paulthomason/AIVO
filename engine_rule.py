import math
from copy import deepcopy

class DiagnosisEngine:
    def __init__(self, diseases, questions, model):
        self.diseases = diseases
        self.questions = questions
        self.model = model
        self.reset()

    def reset(self):
        self.scores = {d: 0 for d in self.diseases}
        self.answered = {}
        self.remaining_questions = set(self.questions)

    def answer_question(self, question, answer):
        self.answered[question] = answer
        self.remaining_questions.discard(question)
        for disease in self.diseases:
            if question in self.model[disease]:
                self.scores[disease] += self.model[disease][question].get(answer, 0)

    def compute_entropy(self, scores=None):
        scores = scores if scores is not None else self.scores
        values = [max(0, s) for s in scores.values()]
        total = sum(values)
        if total == 0 or not values:
            return math.log2(len(scores)) if len(scores) else 0
        probs = [v / total for v in values]
        return -sum(p * math.log2(p) for p in probs if p > 0)

    def get_possible_answers(self, question):
        for d in self.diseases:
            if question in self.model[d]:
                return list(self.model[d][question].keys())
        return ["Yes", "No"]

    def simulate_answer(self, scores, question, answer):
        sim_scores = deepcopy(scores)
        for disease in self.diseases:
            if question in self.model[disease]:
                sim_scores[disease] += self.model[disease][question].get(answer, 0)
        return sim_scores

    def information_gain_for_question(self, question):
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
        return info_gain

    def select_best_question(self):
        best_q = None
        best_ig = -float('inf')
        for q in self.remaining_questions:
            ig = self.information_gain_for_question(q)
            if ig > best_ig:
                best_q = q
                best_ig = ig
        return best_q

    def get_top_diseases(self, n=3):
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)[:n]

    def get_scores(self):
        return dict(self.scores)

    def get_progress(self):
        max_score = max(self.scores.values()) if self.scores else 1
        return {d: (s / max_score if max_score else 0) for d, s in self.scores.items()}

    def is_done(self, max_questions=25):
        return len(self.answered) >= max_questions or not self.remaining_questions

    def get_state(self):
        return {
            "scores": deepcopy(self.scores),
            "answered": deepcopy(self.answered),
            "remaining_questions": list(self.remaining_questions)
        }
