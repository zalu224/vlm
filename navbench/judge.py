"""nav judge: an LLM rates each navigation output on the paper's three criteria.

The paper used two human annotators (Cohen's kappa 0.83). Here Claude Fable 5.1 rates every
output; a blinded human sheet over a subset gives judge-human kappa so the proxy is bounded,
not assumed. The judge sees the image, the gold description of the scene (which seat is
vacant, obstacles and where, the sensible route) and the model's output. It never sees the
model's name or the other outputs.

Anthropic SDK: zero-arg client resolves ANTHROPIC_API_KEY; thinking is left at the model's
default (Claude Fable 5.1 rejects an explicit thinking config), so no `thinking` parameter is sent.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from tqdm import tqdm

from .backends.base import encode_jpeg

CRITERIA = ("destination", "route", "obstacles")

JUDGE_SYSTEM = """You are an accessibility researcher rating navigation instructions given to a person who is blind or has low vision. You compare one model output against the ground truth for the same photograph and answer three independent yes/no questions, exactly as a human annotator would. Rate only what is in front of you; do not reward length or confidence."""

JUDGE_USER = """The attached photograph is the user's current viewpoint (they stand where the camera is, facing the way it faces).

Ground truth for this photograph:
{gold}

The user asked: "{prompt}"

The model answered:
\"\"\"{output}\"\"\"

Answer the three annotator questions from the study, each with yes or no and a one-sentence reason:
1. destination: Did the model accurately identify and guide the user to the correct destination (a genuinely vacant seat)?
2. route: Did the model correctly provide an optimal route (directions and distances that would actually get the user there)?
3. obstacles: Did the model correctly detect obstacles and warn the user to watch out for them? (If the ground truth lists no obstacles, answer yes when the model invents none.)

Return only a JSON object: {{"destination": "yes|no", "route": "yes|no", "obstacles": "yes|no", "reasons": {{"destination": "...", "route": "...", "obstacles": "..."}}}}"""

_JSON = re.compile(r"\{.*\}", re.DOTALL)


def parse_verdict(text: str) -> dict:
    m = _JSON.search(text)
    if not m:
        raise ValueError(f"no JSON in judge output: {text[:200]!r}")
    d = json.loads(m.group(0))
    out = {c: str(d.get(c, "")).strip().lower() == "yes" for c in CRITERIA}
    out["reasons"] = d.get("reasons", {})
    return out


def _client():
    import anthropic

    return anthropic.Anthropic()


def judge_rows(
    rows: list[dict],
    questions: dict[str, dict],
    data_root: Path,
    out_path: Path,
    *,
    client=None,
    model: str = "claude-fable-5-1",
    image_max_side: int = 1024,
) -> Path:
    client = client or _client()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["model"], r["qid"], r["repeat"]))
    with out_path.open("a") as fh:
        for r in tqdm(rows, desc="judge", unit="output"):
            key = (r["model"], r["qid"], r["repeat"])
            if key in done:
                continue
            q = questions[r["qid"]]
            b64, mt = encode_jpeg(Path(data_root) / "images" / f"{r['image']}.jpg", image_max_side)
            user = JUDGE_USER.format(gold=q["gold"], prompt=r["prompt"], output=r["output"])
            resp = client.messages.create(
                model=model,
                max_tokens=2000,
                system=JUDGE_SYSTEM,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": mt, "data": b64},
                            },
                            {"type": "text", "text": user},
                        ],
                    }
                ],
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            try:
                verdict = parse_verdict(text)
                err = None
            except (ValueError, json.JSONDecodeError) as exc:
                verdict = {c: None for c in CRITERIA} | {"reasons": {}}
                err = str(exc)
            ratings = {c: verdict[c] for c in CRITERIA}
            fh.write(
                json.dumps(
                    {
                        **{
                            k: r[k]
                            for k in ("model", "task", "qid", "repeat", "image", "prompt", "output")
                        },
                        "judge_model": model,
                        "ratings": ratings,
                        "reasons": verdict["reasons"],
                        "stop_reason": getattr(resp, "stop_reason", None),
                        "judge_error": err,
                        "judge_raw": text[:600],
                    }
                )
                + "\n"
            )
            fh.flush()
    return out_path
