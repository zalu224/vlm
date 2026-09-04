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
