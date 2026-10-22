"""Cross-run aggregation must preserve results without generating duplicate plots."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cross_run_summary_matches_registered_results(tmp_path, monkeypatch):
    path = ROOT / "scripts" / "aggregate_cross_run.py"
    spec = importlib.util.spec_from_file_location("aggregate_cross_run", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / "summary"
    monkeypatch.setattr(sys, "argv", [
        str(path), "--runs-dir", str(ROOT / "reports" / "runs"),
        "--out-dir", str(output),
    ])

    assert module.main() == 0
    expected = ROOT / "reports" / "cross_run" / "cross_run_summary.json"
    assert json.loads((output / expected.name).read_text()) == json.loads(
        expected.read_text()
    )
    assert (output / "cross_run_summary.md").read_bytes() == (
        expected.with_suffix(".md").read_bytes()
    )
    assert sorted(p.name for p in output.iterdir()) == [
        "cross_run_summary.json", "cross_run_summary.md",
    ]
