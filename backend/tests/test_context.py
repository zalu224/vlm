from lvnav.context import RollingMemory, build_context_prompt, build_naive_prompt


def test_memory_window_and_text():
    m = RollingMemory(window=2)
    assert "start of the walk" in m.to_text()
    m.push("1", "cues one", "go left")
    m.push("2", "cues two", "go straight")
    m.push("3", "cues three", "stop")
    assert len(m) == 2
    txt = m.to_text()
    assert "cues one" not in txt
    assert "cues three" in txt
    assert 'Last instruction given: "stop"' in txt


def test_prompts_are_versioned_and_filled():
    n = build_naive_prompt()
    assert n.version == "naive-v1"
    c = build_context_prompt("Free space: x", "memory text")
    assert c.version == "context-v1"
    assert "Free space: x" in c.user and "memory text" in c.user
    assert "at most two short sentences" in c.system


def test_prompt_includes_only_supplied_components():
    cues_only = build_context_prompt("Free space: clear", None, label="cues")
    assert "Free space: clear" in cues_only.user
    assert "Scene memory" not in cues_only.user
    assert cues_only.version == "cues-v1"

    mem_only = build_context_prompt(None, "Last instruction: stop", label="memory")
    assert "Scene memory" in mem_only.user
    assert "Sensor cues" not in mem_only.user

    both = build_context_prompt("Free space: clear", "Last instruction: stop")
    assert "Sensor cues" in both.user and "Scene memory" in both.user
    # The guide rules are constant across conditions, so differences are attributable
    # to the context components rather than to instruction style.
    assert cues_only.system == mem_only.system == both.system


def test_prompt_rejects_empty_context():
    import pytest

    with pytest.raises(ValueError):
        build_context_prompt(None, None)


def test_memory_without_cues_recalls_instructions():
    m = RollingMemory(window=2, include_cues=False)
    m.push("1", "cue text", "go left")
    m.push("2", "cue text", "stop")
    txt = m.to_text()
    assert "cue text" not in txt
    assert "go left" in txt and "stop" in txt
