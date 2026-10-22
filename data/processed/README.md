# Local experiment data

This directory contains local inputs for re-analysis and resumable extraction.
Its contents are Git-ignored except for this guide. The repository's published
results and sanitized checkpoints are under `reports/`, not here.

| Location | Contents |
| --- | --- |
| `runs/<run-name>/<run-name>.db` | SQLite extraction lineage, materialized graph views, and stability records |
| `runs/<run-name>/reports/e0_report.json` | Repeated-extraction summary emitted by the experiment driver |
| `magnitude/controlled_magnitude.jsonl` and its manifest | Append-only controlled-masking extraction checkpoint |
| `cross_document/cross_document_cdr.jsonl` and its manifest | Append-only joint-context extraction checkpoint |
| `*_toolchain_cache.jsonl` | Local resumable external-component runs; published checkpoints are in `reports/cross_run/` |

The current lineage databases comprise four primary runs:

- `docred__deepseek-v4-flash__300d`
- `redocred__deepseek-v4-flash__300d`
- `scierc__deepseek-v4-flash__100d`
- `cdr__deepseek-v4-flash__300d`

and five DocRED model runs:

- `docred__glm-5__100d`
- `docred__kimi-k2__100d`
- `docred__qwen3-32b__100d`
- `docred__qwen3-8b__100d`
- `docred__qwen3-14b__100d`

`reports/cross_run/reproducibility_manifest.json` identifies the four primary
and three cross-model databases; the additional 8B and 14B runs supply the
Qwen3 size ladder. They are distinct experiments, not alternative versions of
the same result.

Related inputs outside this directory:

- `data/raw/` holds the downloaded corpora. Only SciERC's
  `processed_data/json/{train,dev,test}.json` files are needed; its ELMo
  embeddings are not used.
- `data/cache/hf/datasets/thunlp__docred/validation.jsonl` is the DocRED
  input mirror, included in `data/CHECKSUMS.sha256`. It is needed for offline
  dataset preparation and must not be treated as a disposable download cache.
- `data/cache/extractions/` retains raw extraction responses. These are local
  records, not the input for cached-result verification.

Follow the root [README](../../README.md) for dataset acquisition, complete
extraction commands, re-analysis, and offline verification. Keep the database
and checkpoint paths above when resuming a run; configuration IDs and event
IDs inside them are part of the recorded lineage.
