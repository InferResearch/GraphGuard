"""Printed figure typography must not alter the plotted evidence."""
import numpy as np
import matplotlib.pyplot as plt

from graphguard.viz import style


def test_paper_label_floor_preserves_data_and_limits():
    fig, ax = plt.subplots(figsize=(3.5, 1.4))
    line, = ax.plot([0.1, 0.5, 0.9], [0.2, 0.4, 0.7])
    label = ax.text(0.5, 0.4, "0.40", fontsize=4)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    options = {"bbox_inches": "tight", "pad_inches": 0.025}
    style._ensure_paper_label_sizes(fig, options)
    fig.canvas.draw()
    width = fig.get_tightbbox(fig.canvas.get_renderer()).width + 0.05
    assert label.get_fontsize() * 240.25 / (width * 72) >= 6.045
    np.testing.assert_array_equal(line.get_xdata(), [0.1, 0.5, 0.9])
    np.testing.assert_array_equal(line.get_ydata(), [0.2, 0.4, 0.7])
    assert ax.get_xlim() == xlim
    assert ax.get_ylim() == ylim
    plt.close(fig)


def test_export_keeps_pdf_and_png_together(tmp_path):
    fig, ax = plt.subplots(figsize=(3.5, 1.4))
    ax.plot([0, 1], [0, 1])
    destination = tmp_path / "figure.pdf"
    style.export_pdf_and_png(fig, destination, dpi=80)
    assert destination.is_file()
    assert destination.with_suffix(".png").is_file()
    plt.close(fig)
