import json
from types import SimpleNamespace

from navbench.judge import CRITERIA, judge_rows, parse_verdict


class FakeClient:
    """Stands in for anthropic.Anthropic: records the request, returns a fixed JSON verdict."""

    def __init__(self):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        text = json.dumps(
            {
                "destination": "yes",
                "route": "no",
                "obstacles": "yes",
                "reasons": {
                    "destination": "names the right chair",
                    "route": "sends user left, chair is right",
                    "obstacles": "warns about the box",
                },
            }
        )
        return SimpleNamespace(
            stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)]
        )


def test_parse_verdict_normalises():
    v = parse_verdict('{"destination": "Yes", "route": "no", "obstacles": "YES", "reasons": {}}')
    assert v["destination"] is True and v["route"] is False and v["obstacles"] is True


def test_judge_rows_sends_image_gold_and_output_and_writes_ratings(tmp_path):
    from PIL import Image

    data = tmp_path / "data"
    (data / "images" / "chairs").mkdir(parents=True)
    Image.new("RGB", (40, 30), (1, 2, 3)).save(data / "images" / "chairs" / "IMG_Cl.jpg")
    rows = [
        {
            "model": "m",
            "task": "navigation",
            "qid": "nav_1",
            "repeat": 0,
            "image": "chairs/IMG_Cl",
            "prompt": "Guide me to a vacant seat.",
            "output": "Walk forward; the chair is on your right.",
        }
    ]
    questions = {
        "nav_1": {
            "qid": "nav_1",
            "gold": "One vacant chair to the right of the table; no obstacles.",
        }
    }
    client = FakeClient()
    out = judge_rows(
        rows, questions, data, tmp_path / "judged.jsonl", client=client, model="claude-fable-5-1"
    )
    judged = [json.loads(line) for line in out.read_text().splitlines()]
    assert judged[0]["ratings"] == {"destination": True, "route": False, "obstacles": True}
    assert judged[0]["judge_model"] == "claude-fable-5-1"
    kw = client.calls[0]
    assert kw["model"] == "claude-fable-5-1" and "thinking" not in kw
    content = kw["messages"][0]["content"]
    assert content[0]["type"] == "image" and content[0]["source"]["type"] == "base64"
    text = content[1]["text"]
    assert (
        "One vacant chair" in text and "Walk forward" in text and all(c in text for c in CRITERIA)
    )
    # resume: second call adds nothing
    judge_rows(
        rows, questions, data, tmp_path / "judged.jsonl", client=client, model="claude-fable-5-1"
    )
    assert len(client.calls) == 1
