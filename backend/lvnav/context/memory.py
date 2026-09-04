"""Rolling scene memory: a bounded window of prior frame cues and instructions."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryEntry:
    frame_id: str
    cues_text: str
    instruction: str


class RollingMemory:
    """Keeps the last `window` frames' cue summaries and the most recent instruction.

    The text rendering is intentionally compact: memory exists to give the VLM
    temporal continuity (was that person approaching? did we already tell the user
    to move left?), not to flood the prompt with history.
    """

    def __init__(self, window: int = 3, include_last_instruction: bool = True) -> None:
        self.window = window
        self.include_last_instruction = include_last_instruction
        self._entries: deque[MemoryEntry] = deque(maxlen=window)

    def push(self, frame_id: str, cues_text: str, instruction: str) -> None:
        self._entries.append(MemoryEntry(frame_id, cues_text, instruction))

    def __len__(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def to_text(self) -> str:
        if not self._entries:
            return "No prior frames yet; this is the start of the walk."
        lines = [f"Previous {len(self._entries)} frame(s), oldest first:"]
        for i, e in enumerate(self._entries, 1):
            lines.append(f"  {i}. {e.cues_text}")
        if self.include_last_instruction:
            lines.append(f'Last instruction given: "{self._entries[-1].instruction}"')
        return "\n".join(lines)
