"""Cloud backends are exercised with fake clients so no key or network is needed."""

from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from navbench.backends.anthropic_backend import AnthropicBackend
from navbench.backends.gemini_backend import GeminiBackend
from navbench.backends.openai_backend import OpenAIBackend


def _img(tmp_path):
    p = tmp_path / "a.jpg"
    Image.new("RGB", (50, 40), (5, 5, 5)).save(p)
    return Path(p)


def test_openai_backend_payload(tmp_path):
    calls = []

    def create(**kw):
        calls.append(kw)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=" 3 "))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=1),
        )

    b = OpenAIBackend("gpt-4o", temperature=1.0, top_p=1.0, max_tokens=50, image_max_side=512)
    b.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    r = b.generate("sys", "Count", _img(tmp_path), seed=1)
    assert r.text == "3" and r.prompt_tokens == 10
    kw = calls[0]
    assert kw["model"] == "gpt-4o" and kw["temperature"] == 1.0 and kw["seed"] == 1
    assert kw["messages"][0] == {"role": "system", "content": "sys"}
    assert kw["messages"][1]["content"][0]["type"] == "image_url"


def test_anthropic_backend_payload(tmp_path):
    calls = []

    def create(**kw):
        calls.append(kw)
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text="Yes. Free chair.")],
            usage=SimpleNamespace(input_tokens=9, output_tokens=4),
        )

    b = AnthropicBackend(
        "claude-opus-5", temperature=1.0, top_p=1.0, max_tokens=50, image_max_side=512
    )
    b.client = SimpleNamespace(messages=SimpleNamespace(create=create))
    r = b.generate("sys", "Vacant?", _img(tmp_path))
    assert r.text == "Yes. Free chair." and r.prompt_tokens == 9
    kw = calls[0]
    assert kw["model"] == "claude-opus-5" and kw["system"] == "sys" and kw["temperature"] == 1.0
    assert "top_p" not in kw  # Anthropic rejects temperature+top_p together on current models
    assert kw["messages"][0]["content"][0]["type"] == "image"


def test_anthropic_backend_refusal_is_reported(tmp_path):
    def create(**kw):
        return SimpleNamespace(
            stop_reason="refusal",
            content=[],
            usage=SimpleNamespace(input_tokens=1, output_tokens=0),
        )

    b = AnthropicBackend(
        "claude-opus-5", temperature=1.0, top_p=1.0, max_tokens=50, image_max_side=512
    )
    b.client = SimpleNamespace(messages=SimpleNamespace(create=create))
    r = b.generate(None, "Count", _img(tmp_path))
    assert r.text == "" and r.raw["stop_reason"] == "refusal"


def test_gemini_backend_payload(tmp_path):
    calls = []

    def generate_content(**kw):
        calls.append(kw)
        return SimpleNamespace(
            text="The left chair is closer.",
            usage_metadata=SimpleNamespace(prompt_token_count=7, candidates_token_count=6),
        )

    b = GeminiBackend(
        "gemini-1.5-pro", temperature=1.0, top_p=1.0, max_tokens=50, image_max_side=512
    )
    b.client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    r = b.generate("sys", "Which chair is closer?", _img(tmp_path))
    assert r.text == "The left chair is closer." and r.prompt_tokens == 7
    kw = calls[0]
    assert kw["model"] == "gemini-1.5-pro" and kw["config"]["temperature"] == 1.0
    assert kw["config"]["system_instruction"] == "sys"
