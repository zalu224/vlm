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


def test_context_v2_has_decision_rule_and_no_example_phrases():
    import pytest

    c = build_context_prompt("Free space: x", "memory text", version="v2")
    assert c.version == "context-v2"
    assert "STOP" in c.system and "SLOW DOWN" in c.system and "CONTINUE" in c.system
    # v1 leaked its example phrases verbatim into outputs; v2 must not offer them.
    assert "two steps ahead" not in c.system and "knee height" not in c.system
    assert "Free space: x" in c.user and "memory text" in c.user
    with pytest.raises(ValueError):
        build_context_prompt("c", "m", version="v9")
