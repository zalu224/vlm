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


def test_mlx_direct_backend_loads_once_and_returns_reply(monkeypatch, tmp_path):
    """The in-process backend exists because mlx_vlm.server cannot serve InternVL3 (its prompt
    cache holds a GPU stream from another thread). Faked here: no weights are loaded in tests."""
    import sys
    import types

    calls = {"load": 0, "generate": []}

    class FakeResult:
        text = "  There are 3 chairs.  "
        prompt_tokens = 11
        generation_tokens = 7

    fake = types.ModuleType("mlx_vlm")

    def fake_load(model_id):
        calls["load"] += 1
        return ("MODEL", "PROCESSOR")

    def fake_generate(model, processor, prompt, **kw):
        calls["generate"].append((model, processor, prompt, kw))
        return FakeResult()

    fake.load = fake_load
    fake.generate = fake_generate
    prompt_utils = types.ModuleType("mlx_vlm.prompt_utils")
    prompt_utils.apply_chat_template = lambda proc, cfg, text, num_images=0: f"<{num_images}>{text}"
    monkeypatch.setitem(sys.modules, "mlx_vlm", fake)
    monkeypatch.setitem(sys.modules, "mlx_vlm.prompt_utils", prompt_utils)

    from navbench.backends.registry import build_backend

    b = build_backend(
        {"backend": "mlx-direct", "served": "mlx-community/InternVL3-2B-4bit"},
        sampling={"temperature": 1.0, "top_p": 1.0, "max_tokens": 400},
    )
    assert b.name == "mlx-direct" and b.health() is True

    img = tmp_path / "a.jpg"
    img.write_bytes(b"not-really-a-jpeg")
    r1 = b.generate("SYS", "Count the chairs.", img)
    r2 = b.generate(None, "Count the chairs.", None)

    # Loaded once across both calls, not once per request.
    assert calls["load"] == 1
    assert r1.text == "There are 3 chairs." and r1.prompt_tokens == 11
    # System prompt is folded into the text, and the image is passed as a list of paths.
    p1, kw1 = calls["generate"][0][2], calls["generate"][0][3]
    assert p1 == "<1>SYS\n\nCount the chairs." and kw1["image"] == [str(img)]
    # No image -> no images passed and no image placeholder.
    p2, kw2 = calls["generate"][1][2], calls["generate"][1][3]
    assert p2 == "<0>Count the chairs." and kw2["image"] is None
    assert r2.latency_s >= 0
