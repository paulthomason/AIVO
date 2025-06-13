import { DiagnosisEngine } from './engine.js';

async function loadData() {
  const [questions, diseases, model] = await Promise.all([
    fetch('../data/questions.json').then(r => r.json()),
    fetch('../data/diseases.json').then(r => r.json()),
    fetch('../data/diagnosis_model.json').then(r => r.json()),
  ]);
  return { questions, diseases, model };
}

function createEngine(data) {
  const questionIds = data.questions.map(q => q.id);
  return new DiagnosisEngine(data.diseases, questionIds, data.model);
}

function displayQuestion(engine, questions, qid) {
  const qdata = questions.find(q => q.id === qid);
  document.getElementById('question').textContent = qdata.text;
  const btns = document.getElementById('answers');
  btns.innerHTML = '';
  const options = engine.getPossibleAnswers(qid);
  options.forEach(ans => {
    const btn = document.createElement('button');
    btn.textContent = ans;
    btn.className = 'answer';
    btn.onclick = () => {
      engine.answerQuestion(qid, ans);
      updateProgress(engine);
      nextStep(engine, questions);
    };
    btns.appendChild(btn);
  });
}

function updateProgress(engine) {
  const scores = engine.getScores();
  const top = engine.getTopDiseases();
  const list = top.map(([d,s]) => `${d}: ${scores[d]}`).join('\n');
  document.getElementById('progress').textContent = `Top Diagnoses:\n${list}`;
  document.getElementById('back').style.display = engine.history.length ? 'inline-block' : 'none';
}

function nextStep(engine, questions) {
  if (engine.isDone()) {
    document.getElementById('answers').innerHTML = '';
    const top = engine.getTopDiseases();
    const text = top.map(([d,s]) => `${d}: ${s.toFixed(2)}`).join('\n');
    document.getElementById('question').textContent = 'Diagnosis complete.';
    document.getElementById('progress').textContent = `Most Likely Diagnoses:\n${text}`;
    document.getElementById('restart').style.display = 'inline-block';
    document.getElementById('back').style.display = engine.history.length ? 'inline-block' : 'none';
    return;
  }
  const qid = engine.selectBestQuestion();
  if (!qid) {
    document.getElementById('question').textContent = 'No more questions.';
    document.getElementById('answers').innerHTML = '';
    return;
  }
  engine.currentQuestion = qid;
  displayQuestion(engine, questions, qid);
}

function goBack(engine, questions) {
  const qid = engine.undoLastAnswer();
  if (qid === null) return;
  document.getElementById('restart').style.display = 'none';
  displayQuestion(engine, questions, qid);
  updateProgress(engine);
}

function restart(engine, questions) {
  engine.reset();
  document.getElementById('progress').textContent = '';
  document.getElementById('restart').style.display = 'none';
  document.getElementById('back').style.display = 'none';
  nextStep(engine, questions);
}

async function init() {
  const data = await loadData();
  const engine = createEngine(data);
  const questions = data.questions;
  document.getElementById('back').onclick = () => goBack(engine, questions);
  document.getElementById('restart').onclick = () => restart(engine, questions);
  nextStep(engine, questions);
}

document.addEventListener('DOMContentLoaded', init);
