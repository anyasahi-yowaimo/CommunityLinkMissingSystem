# Evaluation

Run from the project root with the virtual environment active:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m evaluation.benchmark.run_benchmark
```

The included smoke benchmark measures the current local database's candidate generation and score distribution. It intentionally does **not** report Precision@5 or Recall@5 because this MVP does not yet contain a separately frozen, complete ground-truth candidate-label set. Reporting these without a defined relevant set would be misleading. A full benchmark should define positive/negative candidate labels and rationales before evaluating either this engine or a keyword baseline, and then calculate Precision@5, Recall@5, novelty, redundancy, explanation grounding, candidate coverage, abstention quality, deterministic order, eligibility pass rate and duplicate suppression using the same eligibility controls.

All seed records are synthetic. Results cannot establish real-campus performance.
