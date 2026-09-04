"""Evaluation: rubric, LLM judge, paired metrics and report."""

from .judge import judge_run, parse_judge_output
from .metrics import paired_deltas, summarise, write_report
from .rubric import DIMENSIONS, build_judge_prompt

__all__ = [
    "DIMENSIONS",
    "build_judge_prompt",
    "judge_run",
    "parse_judge_output",
    "paired_deltas",
    "summarise",
    "write_report",
]
