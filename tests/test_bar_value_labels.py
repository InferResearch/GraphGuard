"""Bar values stay near their own intervals at the paper's printed size."""
import json
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from graphguard.viz import style
from scripts import make_paper_figures


def check_label_spacing(fig):
    style._ensure_paper_label_sizes(
        fig, {"bbox_inches": "tight", "pad_inches": 0.025}
    )
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        assert len(ax.texts) == 12
        for label in ax.texts:
            assert label.get_position()[1] == 2.0
            assert abs(label.get_position()[0]) <= 3.0
            # Even a zero estimate remains visibly above the horizontal axis.
            assert label.get_window_extent(renderer).y0 > ax.bbox.y0
        for left, right in combinations(ax.texts, 2):
            assert not left.get_window_extent(renderer).overlaps(
                right.get_window_extent(renderer)
            )


def test_stability_bucket_labels_follow_their_own_intervals(tmp_path, monkeypatch):
    reports = tmp_path / "reports" / "cross_run"
    reports.mkdir(parents=True)
    rates = [(0.69, 0.35), (0.70, 0.38), (0.74, 0.40)]
    buckets = {
        name: {"violation_rate_tau0p5": rate,
               "query_divergence_rate": divergence, "n_pairs": 1000}
        for name, (rate, divergence) in zip(
            ["strict", "soft", "ablation"], rates
        )
    }
    for run in ["docred__deepseek-v4-flash__300d",
                "redocred__deepseek-v4-flash__300d",
                "scierc__deepseek-v4-flash__100d",
                "cdr__deepseek-v4-flash__300d"]:
        (reports / f"strict_vs_soft_{run}.json").write_text(
            json.dumps({"buckets": buckets})
        )
    figures = []
    monkeypatch.setattr(make_paper_figures, "ROOT", tmp_path)
    monkeypatch.setattr(style, "export_pdf_and_png",
                        lambda fig, *args, **kwargs: figures.append(fig))
    make_paper_figures.make_strict_vs_soft()
    fig, = figures
    check_label_spacing(fig)
    np.testing.assert_allclose(fig.get_size_inches(), [3.5, 2.12])
    for ax in fig.axes:
        assert ax.get_ylim() == (0, 1.25)
        for label, bar in zip(ax.texts, ax.patches):
            value = bar.get_height()
            upper = value + 1.96 * np.sqrt(value * (1 - value) / 1000)
            assert label.xy[1] == pytest.approx(upper)
            assert label.get_text() == f"{value:.2f}"
    plt.close(fig)


def test_release_gate_labels_include_zero_without_staggering(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    from scripts import make_gate_figure

    data = {
        "Publish-all": [(0.26, 0.20, 0.30)] * 4,
        "Graph-only": [(0.20, 0.10, 0.30)] * 4,
        "GraphGuard": [(0.00, 0.00, 0.00)] * 4,
    }
    style.apply_rc(font_size=9)
    fig, ax = plt.subplots(figsize=(3.6, 2.05))
    make_gate_figure.panel(ax, data, "Harm rate", (0, 0.72))
    check_label_spacing(fig)
    for policy_index, policy in enumerate(make_gate_figure.POLICIES):
        for corpus_index, (value, _, upper) in enumerate(data[policy]):
            label = ax.texts[policy_index * 4 + corpus_index]
            assert label.xy[1] == upper
            assert label.get_text() == f"{value:.2f}"
    assert ax.get_ylim() == (0, 0.72)
    plt.close(fig)
