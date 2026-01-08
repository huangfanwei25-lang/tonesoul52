# ToneSoul 5.2 Test Cases Specification
# 測試案例規格
# 2025-12-27

---

## Overview

Based on multi-perspective audit, these test cases address edge scenarios.

---

## 1. Gate Edge Cases

### poav_gate

```python
def test_poav_gate_empty_string():
    """Empty string should return skipped, not crash."""
    result = poav_gate("", threshold=0.7, enforce=False)
    assert result.passed is True
    assert "poav_text_empty" in result.issues

def test_poav_gate_whitespace_only():
    """Whitespace-only should be treated as empty."""
    result = poav_gate("   \n\t  ", threshold=0.7, enforce=False)
    assert result.passed is True
    assert "poav_text_empty" in result.issues

def test_poav_gate_enforce_empty():
    """Empty text with enforce should block."""
    result = poav_gate("", threshold=0.7, enforce=True)
    assert result.passed is False
```

### escalation_gate

```python
def test_escalation_gate_missing_poav():
    """No POAV result should not crash."""
    result = escalation_gate(
        context={"decision_mode": "normal"},
        poav_result=None,
        drift_metrics={},
    )
    assert result.gate == "escalation_gate"

def test_escalation_gate_missing_drift():
    """Empty drift metrics should handle gracefully."""
    result = escalation_gate(
        context={},
        poav_result=None,
        drift_metrics=None,
    )
    assert result.passed is True  # no escalation without data
```

### tech_trace_gate

```python
def test_tech_trace_gate_invalid_json():
    """Invalid JSON file should return load_failed."""
    # Create temp file with invalid JSON
    result = tech_trace_gate("/path/to/invalid.json", require=False)
    assert result.passed is True
    assert "tech_trace_load_failed" in str(result.issues)

def test_tech_trace_gate_missing_file():
    """Missing file should return missing."""
    result = tech_trace_gate("/nonexistent/path.json", require=False)
    assert result.passed is True
    assert "tech_trace_missing" in result.issues
```

---

## 2. Memory Manager Edge Cases

```python
def test_memory_manager_empty_run_dir():
    """Empty run directory should return empty pointers."""
    pointers = build_pointers("/empty/dir")
    assert pointers.context is None

def test_memory_manager_concurrent_writes():
    """Concurrent writes should not corrupt ledger."""
    # Use threading to test concurrent access
    import threading
    errors = []
    def write_seed(run_id):
        try:
            write_seed(memory_root, run_id, {"test": True})
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=write_seed, args=(f"run_{i}",)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0
```

---

## 3. Pipeline Edge Cases

```python
def test_pipeline_missing_task():
    """Pipeline without task should use default."""
    config = PipelineConfig(objective="Test")
    # Should not crash
    run_pipeline(config)

def test_pipeline_all_gates_skip():
    """Pipeline with skip-gates should still produce artifacts."""
    config = PipelineConfig(
        task="Test",
        skip_gates=True,
    )
    run_pipeline(config)
    # Check artifacts exist
```

---

## 4. YSTM Edge Cases

```python
def test_ystm_diff_empty_nodes():
    """Diff with empty node sets should return empty changes."""
    diff = compute_batch_diff({}, {}, rationale="empty test")
    assert len(diff.changes) == 0

def test_ystm_node_missing_required_fields():
    """Node creation with missing fields should raise."""
    with pytest.raises(TypeError):
        Node(id="test")  # missing required fields
```

---

## Implementation Priority

| Test Category | Priority | Effort |
|---------------|----------|--------|
| Gate edge cases | P1 | 低 |
| Memory concurrent | P2 | 中 |
| Pipeline edge cases | P2 | 中 |
| YSTM edge cases | P3 | 低 |

---

## Running Tests

```bash
# 建立 tests/ 目錄後
pytest tests/ -v
```

---

**Antigravity**  
2025-12-27T15:06 UTC+8
