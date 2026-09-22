from pathlib import Path

from navbench.backends.base import Reply
from navbench.backends.mock import MockBackend
from navbench.backends.registry import build_backend


def test_mock_backend_is_deterministic_per_prompt_and_seed(tmp_path):
    b = MockBackend(answers={"count": ["2", "3"]})
    r1 = b.generate("sys", "Count the number of chairs in the scene.", image=None, seed=0)
    r2 = b.generate("sys", "Count the number of chairs in the scene.", image=None, seed=0)
    r3 = b.generate("sys", "Count the number of chairs in the scene.", image=None, seed=1)
    assert isinstance(r1, Reply) and r1.text == r2.text and r1.text in ("2", "3")
    assert r3.text in ("2", "3")


def test_registry_builds_mock_and_fails_fast_on_missing_env(monkeypatch):
    assert build_backend({"backend": "mock"}, sampling={}).name == "mock"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    try:
        build_backend(
            {"backend": "openai", "served": "gpt-4o", "env": "OPENAI_API_KEY"}, sampling={}
        )
    except OSError as exc:
        assert "OPENAI_API_KEY" in str(exc)
    else:
        raise AssertionError("expected EnvironmentError")


def test_mlx_backend_builds_openai_style_payload(monkeypatch, tmp_path):
    from PIL import Image

    from navbench.backends.mlx import MlxServerBackend

    img = tmp_path / "a.jpg"
    Image.new("RGB", (2000, 1500), (10, 20, 30)).save(img)
    sent = {}

    class FakeResp:
        ok = True
        status_code = 200

        def json(self):
            return {
                "choices": [{"message": {"content": " 3 chairs "}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 2},
            }

    class FakeSession:
        headers = {}

        def post(self, url, json, timeout):
            sent.update(json)
            return FakeResp()

        def get(self, url, timeout):
            return FakeResp()

    b = MlxServerBackend(
        "http://x/v1", "m", temperature=1.0, top_p=1.0, max_tokens=50, image_max_side=1024
    )
    b.session = FakeSession()
    r = b.generate("sys", "Count", image=Path(img), seed=3)
    assert r.text == "3 chairs" and r.prompt_tokens == 5
    assert sent["temperature"] == 1.0 and sent["max_tokens"] == 50 and sent["seed"] == 3
    content = sent["messages"][1]["content"]
    assert content[0]["type"] == "image_url" and content[0]["image_url"]["url"].startswith(
        "data:image/jpeg;base64,"
    )
    assert content[1]["text"] == "Count"
