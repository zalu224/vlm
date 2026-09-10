# Study A — Implementation Plan

The research framing and questions are in `docs/PROPOSAL_CONTEXT.md`. Each day ends with a concrete, checkable artefact. Days 1–2 are the risky ones (environment and data); everything after that runs on the scaffold already in this repository.

| Day | Goal | Artefact | Risk / fallback |
|---|---|---|---|
| **1** | Environment + data | `make setup` and `make serve-vlm` both work; `lvnav run --backend mock` passes on a real frame dir. Record 3 walks (indoor corridor, sidewalk with people, a crossing) at chest height, 2–4 min each, 1080p. Check whether GuideDog or another egocentric BLV dataset is accessible; if not, self-recorded footage is the dataset. | Model download is slow → start it first thing. |
| **2** | Perception on real frames | Depth + YOLO-World running on MPS; eyeball cue text for 30 frames; tune `vocabulary` and thresholds in `configs/default.yaml` if zones are systematically wrong. | MPS op failure → update torch (see `docs/HARDWARE.md`). |
| **3** | Baseline + cues | `results/<walk>_naive` and `results/<walk>_cues`; note median latency. | If 7B > 8 s/frame, switch to 3B for all conditions. |
| **4** | Memory + full context | `results/<walk>_memory` and `results/<walk>_context` on the same frames (`make run-all`); read 30 paired outputs and note first qualitative observations. | Prompt iteration: bump `prompt_version` rather than editing v1 in place. |
| **5** | Evaluation | Both runs judged (`--cues-from` for naive); `report.md`; 40-frame human spot-check; judge–human ρ per dimension. | Low ρ on a dimension → report it as unreliable, do not drop it silently. |
| **6** | Analysis + write-up | Results table in root README; `docs/RESULTS.md` with findings, failure catalogue, and H1–H3 verdicts; 2-page write-up. | |
| **7** | Presentation | Rehearse the Streamlit demo on the best and worst frames; slides (≤ 8); email to the professor with repo link and write-up. | |

## Scope guardrails

- Do not fine-tune anything this week. The question is about context, not weights.
- Do not add a speech interface this week; it is an extension path.
- One VLM, four conditions, one judge. A second model size (RQ3) comes only after the core comparison is complete.

## Definition of done

- [ ] ≥ 300 frames evaluated under all four conditions with identical settings
- [ ] Paired reports against the naive baseline, with per-dimension deltas and latency
- [ ] Human spot-check with agreement statistics
- [ ] Reproducible from a clean clone following the root README
- [ ] Viewer demo runs offline from the results directory
