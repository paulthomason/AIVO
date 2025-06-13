class DiagnosisEngine {
  constructor(diseases, questions, model) {
    this.diseases = diseases;
    this.questions = questions;
    this.model = model;
    this.reset();
  }

  reset() {
    this.scores = {};
    this.diseases.forEach(d => { this.scores[d] = 0; });
    this.answered = {};
    this.remaining = new Set(this.questions);
    this.history = [];
    this.eliminated = {};
    this.diseases.forEach(d => { this.eliminated[d] = 0; });
    this._prevScores = {};
  }

  answerQuestion(question, answer) {
    this.answered[question] = answer;
    this.remaining.delete(question);
    this.history.push(question);
    this.diseases.forEach(d => {
      const qmap = this.model[d] || {};
      if (!(question in qmap)) return;
      const weight = qmap[question][answer] || 0;
      if (weight === -1) {
        if (this.eliminated[d] === 0) {
          this._prevScores[d] = this.scores[d];
          this.scores[d] = -Infinity;
        }
        this.eliminated[d] += 1;
      } else if (this.eliminated[d] === 0) {
        this.scores[d] += weight;
      }
    });
  }

  undoLastAnswer() {
    if (!this.history.length) return null;
    const question = this.history.pop();
    const answer = this.answered[question];
    delete this.answered[question];
    this.remaining.add(question);
    this.diseases.forEach(d => {
      const qmap = this.model[d] || {};
      if (!(question in qmap)) return;
      const weight = qmap[question][answer] || 0;
      if (weight === -1) {
        if (this.eliminated[d] > 0) {
          this.eliminated[d] -= 1;
          if (this.eliminated[d] === 0) {
            this.scores[d] = this._prevScores[d] || 0;
          } else {
            this.scores[d] = -Infinity;
          }
        }
      } else if (this.eliminated[d] === 0) {
        this.scores[d] -= weight;
      }
    });
    return question;
  }

  getPossibleAnswers(question) {
    for (const d of this.diseases) {
      const qmap = this.model[d];
      if (qmap && question in qmap) {
        return Object.keys(qmap[question]);
      }
    }
    return ["Yes", "No"];
  }

  computeEntropy(scores = this.scores) {
    const active = Object.values(scores).filter(v => v !== -Infinity);
    const values = active.map(v => Math.max(0, v));
    const total = values.reduce((a, b) => a + b, 0);
    if (total === 0 || active.length === 0) {
      return active.length ? Math.log2(active.length) : 0;
    }
    const probs = values.map(v => v / total);
    return -probs.reduce((sum, p) => p > 0 ? sum + p * Math.log2(p) : sum, 0);
  }

  simulateAnswer(scores, question, answer) {
    const sim = { ...scores };
    this.diseases.forEach(d => {
      const qmap = this.model[d] || {};
      if (!(question in qmap)) return;
      const weight = qmap[question][answer] || 0;
      if (weight === -1) {
        sim[d] = -Infinity;
      } else if (sim[d] !== -Infinity) {
        sim[d] += weight;
      }
    });
    return sim;
  }

  informationGainForQuestion(question) {
    const answers = this.getPossibleAnswers(question);
    const entropies = [];
    for (const ans of answers) {
      const sim = this.simulateAnswer(this.scores, question, ans);
      entropies.push(this.computeEntropy(sim));
    }
    const expected = entropies.reduce((a,b)=>a+b,0) / answers.length;
    const current = this.computeEntropy();
    return current - expected;
  }

  selectBestQuestion() {
    let best = null;
    let bestIg = -Infinity;
    for (const q of this.remaining) {
      const ig = this.informationGainForQuestion(q);
      if (ig > bestIg) {
        bestIg = ig;
        best = q;
      }
    }
    return best;
  }

  getTopDiseases(n=3) {
    const active = Object.entries(this.scores).filter(([,s]) => s !== -Infinity);
    active.sort((a,b)=>b[1]-a[1]);
    return active.slice(0,n);
  }

  getScores() {
    const out = {};
    for (const [d,s] of Object.entries(this.scores)) {
      if (s !== -Infinity) out[d] = s;
    }
    return out;
  }

  isDone(maxQuestions=25) {
    return this.history.length >= maxQuestions || this.remaining.size === 0;
  }
}

export { DiagnosisEngine };
