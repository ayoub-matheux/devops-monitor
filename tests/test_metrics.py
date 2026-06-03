"""Unit tests for api/metrics.py."""

import pytest

from api.metrics import get_system_metrics


def test_metrics_keys():
    """Returned dict must contain all expected keys."""
    data = get_system_metrics()
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data
    assert "memory_used_gb" in data
    assert "memory_total_gb" in data


def test_metrics_cpu_range():
    """CPU percent must be between 0 and 100."""
    data = get_system_metrics()
    assert 0 <= data["cpu_percent"] <= 100


def test_metrics_memory_range():
    """Memory percent must be between 0 and 100."""
    data = get_system_metrics()
    assert 0 <= data["memory_percent"] <= 100


def test_metrics_disk_range():
    """Disk percent must be between 0 and 100."""
    data = get_system_metrics()
    assert 0 <= data["disk_percent"] <= 100


def test_metrics_memory_gb_positive():
    """Memory GB values must be positive numbers."""
    data = get_system_metrics()
    assert data["memory_used_gb"] >= 0
    assert data["memory_total_gb"] > 0
