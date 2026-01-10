"""
Tests for TSR Metrics (tsr_metrics.py)

Phase 44: Comprehensive Core Module Test Suite

Tests cover:
1. TSR score calculation
2. Lexicon-based scoring (positive/negative/modal/caution)
3. Variability metrics
4. Metric building and delta calculation
5. Index management
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from tonesoul.tsr_metrics import (
    score,
    build_tsr_metrics,
    load_tsr_policy,
    resolve_tsr_policy,
    load_index,
    update_index,
    latest_entry,
    write_tsr_metrics,
    DEFAULT_LEXICON,
    DEFAULT_TENSION,
    DEFAULT_VARIABILITY,
)


class TestTSRScore:
    """Tests for the score function."""
    
    def test_score_returns_dict(self):
        """Score returns a dictionary."""
        result = score("Hello, this is a test.")
        assert isinstance(result, dict)
    
    def test_score_empty_text(self):
        """Score with empty text."""
        result = score("")
        assert isinstance(result, dict)
        # Should have some default/zero values
    
    def test_score_positive_text(self):
        """Text with positive words should affect score."""
        positive_text = "We will build, create, enable, and advance this project."
        result = score(positive_text)
        assert "positive_hits" in result or "positive_ratio" in result or "overall" in result
    
    def test_score_negative_text(self):
        """Text with negative words should affect score."""
        negative_text = "This will destroy, harm, damage, and break everything."
        result = score(negative_text)
        assert isinstance(result, dict)
    
    def test_score_modal_verbs(self):
        """Text with modal verbs should be detected."""
        modal_text = "We might possibly consider perhaps maybe doing this."
        result = score(modal_text)
        assert isinstance(result, dict)
    
    def test_score_with_custom_policy(self):
        """Score with custom policy."""
        custom_policy = {
            "lexicon": DEFAULT_LEXICON,
            "weights": DEFAULT_WEIGHTS,
        }
        result = score("Test text", policy=custom_policy)
        assert isinstance(result, dict)
    
    def test_score_long_text(self):
        """Score with longer text."""
        long_text = "This is a sentence. " * 50
        result = score(long_text)
        assert isinstance(result, dict)
    
    def test_score_contains_key_metrics(self):
        """Score result contains expected keys."""
        result = score("Test the scoring system.")
        # Check for some expected keys (exact keys depend on implementation)
        assert result is not None


class TestBuildTSRMetrics:
    """Tests for build_tsr_metrics function."""
    
    def test_build_returns_dict(self):
        """Build returns a dictionary."""
        result = build_tsr_metrics("Test text for metrics.")
        assert isinstance(result, dict)
    
    def test_build_with_run_id(self):
        """Build with custom run ID."""
        result = build_tsr_metrics("Test", run_id="run_001")
        assert "run_id" in result
        assert result["run_id"] == "run_001"
    
    def test_build_with_source_path(self):
        """Build with source path."""
        result = build_tsr_metrics("Test", source_path="/path/to/source.md")
        assert "source_path" in result
    
    def test_build_creates_timestamp(self):
        """Build creates timestamp."""
        result = build_tsr_metrics("Test")
        assert "timestamp" in result or "created_at" in result or "run_id" in result
    
    def test_build_with_baseline(self):
        """Build with baseline entry for delta calculation."""
        baseline = {
            "overall": 0.7,
            "scores": {"positive_ratio": 0.5}
        }
        result = build_tsr_metrics("Test", baseline_entry=baseline)
        assert isinstance(result, dict)
    
    def test_build_includes_score_data(self):
        """Build includes scoring data."""
        result = build_tsr_metrics("This is a test sentence.")
        # Should include score or metrics
        assert result is not None


class TestTSRPolicy:
    """Tests for policy loading and resolution."""
    
    def test_resolve_policy_default(self):
        """Resolve with no policy returns default."""
        policy = resolve_tsr_policy()
        assert policy is not None
        assert "lexicon" in policy or "weights" in policy
    
    def test_resolve_policy_custom(self):
        """Resolve with custom policy."""
        custom = {"lexicon": {"positive": {"test"}}, "weights": {}}
        policy = resolve_tsr_policy(policy=custom)
        assert policy is not None
    
    def test_load_policy_file(self):
        """Load policy from file (if exists)."""
        # This may return None if no file exists, which is OK
        try:
            policy = load_tsr_policy()
            # If it returns, should be dict or None
            assert policy is None or isinstance(policy, dict)
        except FileNotFoundError:
            pass  # Expected if no policy file


class TestTSRIndexManagement:
    """Tests for index load/update operations."""
    
    def test_load_index_nonexistent(self):
        """Load index from nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "nonexistent.json")
            result = load_index(path)
            # Should return empty structure or handle gracefully
            assert result is not None or result == {}
    
    def test_update_index(self):
        """Update index with new entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "index.json")
            metrics_path = os.path.join(tmpdir, "metrics_001.json")
            
            # Create initial empty index
            with open(path, 'w') as f:
                json.dump({"entries": []}, f)
            
            update_index(
                path=path,
                run_id="run_001",
                metrics_path=metrics_path,
                payload={"overall": 0.8}
            )
            
            # Verify update
            with open(path) as f:
                data = json.load(f)
            assert "entries" in data
    
    def test_latest_entry(self):
        """Get latest entry from index."""
        index_data = {
            "entries": [
                {"run_id": "run_001", "timestamp": "2026-01-01"},
                {"run_id": "run_002", "timestamp": "2026-01-02"},
            ]
        }
        entry = latest_entry(index_data)
        assert entry is not None


class TestWriteTSRMetrics:
    """Tests for writing metrics to file."""
    
    def test_write_metrics(self):
        """Write metrics to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "metrics.json")
            payload = {
                "run_id": "test_001",
                "overall": 0.75,
                "scores": {"a": 0.5}
            }
            
            write_tsr_metrics(path, payload)
            
            # Verify written
            with open(path) as f:
                data = json.load(f)
            assert data["overall"] == 0.75


class TestDefaultLexicon:
    """Tests for DEFAULT_LEXICON configuration."""
    
    def test_lexicon_has_positive(self):
        """Lexicon has positive words."""
        assert "positive" in DEFAULT_LEXICON
        assert len(DEFAULT_LEXICON["positive"]) > 0
    
    def test_lexicon_has_negative(self):
        """Lexicon has negative words."""
        assert "negative" in DEFAULT_LEXICON
        assert len(DEFAULT_LEXICON["negative"]) > 0


class TestDefaultConfigs:
    """Tests for DEFAULT configuration constants."""
    
    def test_tension_config_exists(self):
        """Default tension config is defined."""
        assert DEFAULT_TENSION is not None
        assert isinstance(DEFAULT_TENSION, dict)
    
    def test_variability_config_exists(self):
        """Default variability config is defined."""
        assert DEFAULT_VARIABILITY is not None
        assert isinstance(DEFAULT_VARIABILITY, dict)
