# Contributing to ToneSoul

Thank you for considering contributing to ToneSoul! 🌌

## 💭 Our Philosophy

Before diving into code, please understand what makes ToneSoul different:

> **We optimize for honesty, not just helpfulness.**

Every contribution should ask: *"Does this make the system more accountable, or just more capable?"*

---

## 🚀 Quick Start for Contributors

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/tonesoul52.git
cd tonesoul52
```

### 2. Set Up Development Environment

```bash
# Windows
.\setup_env.ps1

# Or manually
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
pip install -e ".[dev]"
```

### 3. Run Tests

```bash
pytest tests/
```

### 4. Run 7D Audit

```bash
python scripts/verify_7d.py
```

---

## 📋 Types of Contributions

### 🐛 Bug Reports

Found a bug? Please include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior

### ✨ Feature Requests

Have an idea? Please describe:
- The problem you're trying to solve
- Your proposed solution
- How it aligns with ToneSoul's philosophy

### 🔧 Code Contributions

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest tests/`
4. Run 7D audit: `python scripts/verify_7d.py`
5. Submit a Pull Request

---

## 📝 Code Style

- **Python**: Follow Black formatting (line length 100)
- **Docstrings**: Google style
- **Tests**: Use pytest, aim for high coverage
- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)

### Linting

```bash
black --check --line-length 100 tonesoul tests
ruff check tonesoul tests
```

### Multi-Agent Commit Attribution

When multiple agents share the same Git author identity, add trailers to every
commit message for traceability:

```text
Agent: codex-gpt5 | antigravity | human
Trace-Topic: short-topic-id
```

Example:

```text
feat(council): integrate VTP runtime guard

Agent: codex-gpt5
Trace-Topic: phase32-vtp-runtime-integration
```

You can verify the latest commit message with:

```bash
python scripts/verify_commit_attribution.py --rev HEAD
```

CI policy (incremental blocking):
- `pull_request`: check only commits in `base..head`
- `push`: check only newly pushed commits in `before..after`
- legacy history is not blocked retroactively

If any incremental commit misses `Agent` or `Trace-Topic`, CI fails.

---

## 🛡️ 7D Audit Compliance

All contributions must pass the 7D audit:

| Dimension | Requirement |
|-----------|-------------|
| TDD | New features must have tests |
| RDD | Security-sensitive code needs red-team review |
| DDD | No data leakage, clean memory hygiene |
| XDD | Logic must be explainable |
| GDD | Respect governance boundaries |
| CDD | Maintain narrative consistency |
| SDH | No performance regressions |

---

## 💬 Community

- **Issues**: For bug reports and feature requests
- **Discussions**: For broader conversations
- **Pull Requests**: For code contributions

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

---

## 🙏 Thank You

> *"If you've ever felt that AI should be more than a clever autocomplete — if you believe machines can be built to say 'I don't know' with dignity — you belong here."*

Every contribution, no matter how small, helps build a future where AI is honest, accountable, and genuinely helpful.

⭐ **Star this repo** to help others discover this work!
