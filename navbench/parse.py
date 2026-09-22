"""Answer extraction. Deliberately simple and documented: the first number for counts, the
first mentioned option for choices, the first yes/no for yes-no questions. Anything else is
a parse failure, which is reported rather than guessed."""

from __future__ import annotations

import re

_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
_NUM = re.compile(r"\b(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten)\b", re.I)
_YES = re.compile(
    r"\b(yes|yeah|there (is|are) (a |an |one |two |some |several |)?"
    r"(vacant|empty|free|available))\b",
    re.I,
)
_NO = re.compile(r"\b(no|nope|there (is|are) no|not any|none)\b", re.I)


def parse_answer(text: str, answer_type: str, choices: list[str] | None = None):
    t = text.strip()
    if answer_type == "int":
        m = _NUM.search(t)
        if not m:
            return None
        tok = m.group(1).lower()
        return int(tok) if tok.isdigit() else _WORDS[tok]
    if answer_type == "choice":
        hits = []
        for c in choices or []:
            m = re.search(rf"\b{re.escape(c)}\b", t, re.I)
            if m:
                hits.append((m.start(), c))
        return min(hits)[1] if hits else None
    if answer_type == "yesno":
        y, n = _YES.search(t), _NO.search(t)
        if y and (not n or y.start() <= n.start()):
            return "yes"
        if n:
            return "no"
        return None
    return t
