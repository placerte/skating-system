"""Method-specific scoring models and engines."""

from skating_system.scoring.callback import (
    CallbackMark,
    CallbackPolicy,
    CallbackResult,
    CallbackSelection,
    CallbackTally,
    aggregate_callback_marks,
    compute_callback_result,
    normalize_callback_marks,
    normalize_callback_value,
    select_callback_entries,
)

__all__ = [
    "CallbackMark",
    "CallbackPolicy",
    "CallbackResult",
    "CallbackSelection",
    "CallbackTally",
    "aggregate_callback_marks",
    "compute_callback_result",
    "normalize_callback_marks",
    "normalize_callback_value",
    "select_callback_entries",
]
