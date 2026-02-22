from __future__ import annotations

import math
from typing import Callable


def absolute_error(approximate: float, exact: float) -> float:
    return abs(exact - approximate)


def relative_error_percent(approximate: float, exact: float) -> float:
    if exact == 0.0:
        return float("inf") if approximate != 0.0 else 0.0
    return abs((exact - approximate) / exact) * 100.0


def format_table(
    headers: list[str],
    rows: list[list],
    col_widths: list[int] | None = None,
) -> str:
    n_cols = len(headers)
    if col_widths is None:
        col_widths = [0] * n_cols

    widths = [max(col_widths[i], len(str(headers[i]))) for i in range(n_cols)]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header_row = "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    lines = [sep, header_row, sep]
    for row in rows:
        line = "| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)) + " |"
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)


def format_float(value: float, precision: int = 8) -> str:
    if math.isinf(value):
        return "inf"
    if math.isnan(value):
        return "nan"
    return f"{value:.{precision}f}"
