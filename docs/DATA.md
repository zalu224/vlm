# Data Sources and Provenance

All footage used for evaluation, with licence and attribution. Raw video lives in `data/raw/` (git-ignored) and is deleted after frame extraction to save disk; extracted frames live in `data/<walk>/` (git-ignored). The frame ids in `results/*/records.jsonl` refer to those directories.

## Public egocentric walking video (bootstrap set)

Selected from YouTube's Creative-Commons filter and verified with `yt-dlp --print "%(license)s"` on 2026-09-05. Downloaded video-only at ≤ 1080p.

| Walk id | Source | Licence | Length | Scene coverage |
|---|---|---|---|---|
| `suwon` | "POV Walking in Suwon, Korea in 4K — Free GoPro Hero 6 Stock Footage", https://www.youtube.com/watch?v=V8_Iaqmj3nk | CC BY (reuse allowed) | 4:55 | sidewalk, pedestrians, storefronts, some crossings |
| `london` | "London Walk: Leicester Square to Charing Cross in Under 5 Minutes!", https://www.youtube.com/watch?v=omcY89kce2A | CC BY (reuse allowed) | 4:45 | dense sidewalk, pedestrians, street crossings |

Backups verified as CC BY but not downloaded: `DtnlERB65kc` (sidewalk, 10:26), `625XN8qJyfk` (Madison Ave NYC, 12:09).

Caveat for the write-up: these are head-height, stabilised walking-tour shots that mostly look straight ahead. A chest-mounted BLV wearable would be lower and shakier. Self-recorded walks below are the closer match.

## Self-recorded walks

To be added by Aaron (see `docs/PROGRESS.md`, Day 1, *Needs Aaron*). Record in public spaces; frames are extracted at 1 fps and raw video deleted; do not keep identifiable faces in any frame that is committed as a sample.

| Walk id | Where | Length | Scene coverage |
|---|---|---|---|
| `corridor` | | | indoor corridor |
| `sidewalk` | | | sidewalk with pedestrians |
| `crossing` | | | street crossing |

## GuideDog (secondary, static images)

`kjunh/GuideDog` on Hugging Face, CC BY-NC 4.0, gated (login + terms). 2,106 human-verified gold image + guidance pairs cut from walking videos across 46 countries, plus depth and object-box configs. No frame ordering, so it cannot test rolling memory; used, if access is granted, as a static-image sanity check of the cue and prompt layer against human-written guidance.
