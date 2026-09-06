# Evaluation Rubric

Each instruction is scored 1–5 on five dimensions. Higher is always better, including *hallucination* (5 = nothing invented). The judge prompt in `backend/lvnav/eval/rubric.py` is generated from the same definitions, so this file and the code cannot drift apart without a code change.

| Dimension | Question the judge answers | 1 | 5 |
|---|---|---|---|
| Safety | Is the most safety-critical hazard within the next few steps surfaced first, and would following the instruction keep the person safe? | Ignores a near hazard or directs into it | Hazard-first, action keeps the person safe |
| Actionability | Can a blind person act on it immediately? | Vague, visual, or no clear action | Body-relative direction + concrete verb |
| Spatial accuracy | Are stated positions/distances consistent with the image and cues? | Wrong side or wrong distance | Matches image and cues |
| Conciseness | Is it as short as spoken delivery allows, with no scene description? | Paragraph of description | One or two short sentences |
| Hallucination | Does it avoid unsupported objects, hazards or directions? | Mostly invented | Nothing invented |

## Why these five

They map onto the failure modes reported for VLM-based pBLV assistance (spatial reasoning, verbosity, poor alignment with user needs) and onto what orientation-and-mobility instructors emphasise: hazard first, body-relative language, brevity for audio delivery. Conciseness is scored separately from actionability because a long instruction can still be actionable; we want to know whether context makes the model *shorter* as well as *better*.

## Judge design choices

- **Same evidence for both conditions.** The judge sees the frame, the perception cues and the instruction. It never sees the generating prompt, so it cannot reward the context condition for matching a prompt it was shown. For naive runs, cues are borrowed from the matching context run (`lvnav judge --cues-from`), otherwise the judge would be blind for the baseline.
- **Deterministic.** Temperature 0, strict JSON output, parsed defensively; unparseable outputs are recorded as `None` and excluded from means rather than silently scored.
- **Same model as the generator.** Using the local Qwen2.5-VL as judge is a known self-preference risk. The Day-5 human spot-check (40 stratified frames, both conditions, blinded order) exists to bound that risk: report Spearman ρ per dimension and note any dimension where ρ < 0.5 as unreliable.

## Human spot-check protocol

1. `lvnav manual-sheet --runs results/<walk>_naive results/<walk>_context_v2_nomem --every 8` writes `results/manual_sheet.csv` (rows from both runs, shuffled, condition hidden) and `results/manual_sheet_key.csv`. Every 8th frame is a subset of the every-4th frames the v2 judge scored, so every human-scored row has a judge score.
2. Score in the CSV with the table above, looking at the frame image (`frame_path`), without opening the key or any judged file. Cues are shown for every row, as they were for the judge.
3. `lvnav agreement --sheet results/manual_sheet.csv --key results/manual_sheet_key.csv --judged-name judged_v2_every4.jsonl` prints Spearman ρ, means and exact-match rate per dimension; run it again with `--judged-name judged.jsonl` for the v1 judge. Add both tables to `docs/RESULTS.md`; flag any dimension with ρ < 0.5 as unreliable.
