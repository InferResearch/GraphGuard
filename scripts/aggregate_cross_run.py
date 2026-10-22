#!/usr/bin/env python3
"""Aggregate per-run contracts and diagnostic amplification into JSON/Markdown.

Writes reports/cross_run/cross_run_summary.{json,md}.
Generate the canonical figures with make_paper_figures.py.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ---------- friendly mapping + grouping (paper-facing names) -----------------
RUN_LABEL = {
    "docred__deepseek-v4-flash__300d":   "DocRED · 300d",
    "redocred__deepseek-v4-flash__300d": "Re-DocRED · 300d",
    "cdr__deepseek-v4-flash__300d":      "BC5CDR · 300d",
    "scierc__deepseek-v4-flash__100d":    "SciERC · 100d",
    "docred__glm-5__100d":               "GLM-5 · 100d",
    "docred__kimi-k2__100d":             "Kimi-K2 · 100d",
    "docred__qwen3-32b__100d":           "Qwen3-32B · 100d",
}


def load_run(run_dir: Path) -> dict | None:
    cj = run_dir / "eval" / "contracts.json"
    diagnostic = (
        ROOT / "reports" / "cross_run"
        / f"diagnostic_{run_dir.name}.json"
    )
    if not cj.exists():
        return None
    contracts = json.loads(cj.read_text())
    amp = json.loads(diagnostic.read_text()) if diagnostic.exists() else None
    return {"name": run_dir.name, "contracts": contracts, "amp": amp}


def write_summary(runs: list[dict], out_json: Path, out_md: Path) -> None:
    summary = {"runs": []}
    for r in runs:
        cs = r["contracts"]["contracts"]
        amp = (r.get("amp") or {}).get("summary", {})
        amp_d1 = amp.get("diagnostic.edge_identity", {}).get(
            "amplification_mean_per_pair"
        )
        amp_d3 = amp.get("diagnostic.fanout_join", {}).get(
            "amplification_mean_per_pair"
        )
        ratio = (amp_d3 / amp_d1) if (amp_d1 and amp_d3) else None
        summary["runs"].append({
            "name": r["name"],
            "contracts": {
                c["contract_id"]: {
                    "n_pairs": c["n_pairs"],
                    "violation_rate": c["violation_rate"],
                    "verdict": c["verdict"],
                } for c in cs
            },
            "Amp_D1_mean": amp_d1,
            "Amp_D3_mean": amp_d3,
            "Amp_D3_over_D1": ratio,
        })
    out_json.write_text(json.dumps(summary, indent=2))

    lines = ["# Cross-run summary", "",
             "| Run | K1 | K1b | K1c | K2 | K3 | K4 | K5 | K6 | Amp(D3) | Amp(D3)/Amp(D1) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summary["runs"]:
        c = s["contracts"]
        def cell(k):
            x = c.get(k)
            if not x or x["n_pairs"] == 0: return "—"
            verdict_mark = {"VIOLATED": "🔴", "SATISFIED": "🟢", "INCONCLUSIVE": "⚪"}.get(x["verdict"], "")
            return f"{x['violation_rate']:.2f} {verdict_mark}"
        lines.append("| " + " | ".join([
            RUN_LABEL.get(s["name"], s["name"]).replace("\n", " "),
            cell("K1"), cell("K1b"), cell("K1c"), cell("K2"),
            cell("K3"), cell("K4"), cell("K5"), cell("K6"),
            f"{s['Amp_D3_mean']:.2f}" if s.get("Amp_D3_mean") is not None else "—",
            f"{s['Amp_D3_over_D1']:.2f}×" if s.get("Amp_D3_over_D1") is not None else "—",
        ]) + " |")
    out_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default="reports/runs")
    ap.add_argument("--out-dir", default="reports/cross_run")
    ap.add_argument("--include", nargs="+", default=None,
                    help="Optional list of run names to include; else auto-discover.")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = []
    candidates = sorted(p for p in runs_dir.iterdir() if p.is_dir())
    for p in candidates:
        if args.include and p.name not in args.include:
            continue
        r = load_run(p)
        if r is not None:
            runs.append(r)
            print(f"  loaded {p.name}: {len(r['contracts']['contracts'])} contracts, "
                  f"{'amp' if r['amp'] else 'no amp'}")

    if not runs:
        print("no runs found", file=sys.stderr)
        return 1

    write_summary(runs, out_dir / "cross_run_summary.json",
                  out_dir / "cross_run_summary.md")
    print(f"[done] wrote {out_dir}/  ({len(runs)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
