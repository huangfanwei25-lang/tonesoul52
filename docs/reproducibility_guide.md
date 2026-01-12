# Reproducibility Guide
# 可重現性指南

> **For External Researchers**  
> **給外部研究者的指南**

---

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 3. Run Tests

```bash
python -m pytest tests/ -v
```

**Expected Output**: All tests pass (100%)

### 4. Run Baseline Comparison

```bash
python experiments/baseline_comparison.py
```

**Expected Output**:
```
PreOutputCouncil         100.0%    0 False Approve
SingleJudge               45.5%    3 False Approve
MajorityVote              72.7%    0 False Approve
```

---

## Reproducing Paper Results

### Table 1: Accuracy Comparison

```bash
python experiments/baseline_comparison.py
```

| Method | Expected Accuracy | Expected False Approve |
|--------|-------------------|------------------------|
| PreOutputCouncil | 100% | 0 |
| SingleJudge | 45.5% | 3 |
| MajorityVote | 72.7% | 0 |

### Table 2: Latency Benchmark

```bash
python experiments/council_performance.py
```

| Metric | Expected Value |
|--------|----------------|
| Average Latency | < 1 ms |
| Target (50 ms) | PASS |

---

## Experiment Configuration

### Test Cases (11 total)

| Category | Count | Examples |
|----------|-------|----------|
| Safety | 3 | "Make a bomb...", "Kill someone...", "製作炸彈..." |
| Safe | 3 | "Weather is nice", "Python is a language" |
| Subjective | 3 | "Art is subjective", "Best movie ever" |
| Edge | 2 | Empty string, 1000 char repeat |

### Thresholds

| Parameter | Value | Location |
|-----------|-------|----------|
| coherence_threshold | 0.6 | `pre_output_council.py` |
| block_threshold | 0.3 | `pre_output_council.py` |
| guardian_veto_confidence | 0.7 | `verdict.py` |

---

## Environment Requirements

### Python Version

```bash
python --version
# Expected: Python 3.10+
```

### Dependencies

```bash
pip freeze | grep -E "(pytest|tonesoul)"
```

Required packages are listed in `requirements.txt`.

---

## Known Issues

### Issue 1: pytest Import Error

**Symptom**: `ImportError: cannot import name 'Config'`

**Solution**: 
```bash
pip install pytest --upgrade
```

### Issue 2: Chinese Character Encoding

**Symptom**: Garbled output on Windows

**Solution**: 
```bash
chcp 65001
```

---

## Contact

If you encounter issues reproducing results:

1. Open an issue on GitHub
2. Include:
   - Python version
   - OS version
   - Full error message
   - Output of `pip freeze`

---

*Last Updated: 2026-01-12*
