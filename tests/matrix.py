"""Single source of truth for the render + smoke matrix.

Matrix dimensions: use_postgresql × use_opentelemetry × ci_tool
= 2 × 2 × 2 = 8 combos.

use_docker is intentionally pinned to 'y' for the matrix: Docker is the primary
v0.1 deployment path, and varying it would multiply the matrix to 16 combos
without proportional coverage value. use_docker='n' is covered by a single
dedicated smoke test (see tests/test_smoke.py).
"""

from __future__ import annotations

from itertools import product
from typing import NamedTuple


class Combo(NamedTuple):
    use_postgresql: str     # 'y' | 'n'
    use_opentelemetry: str  # 'y' | 'n'
    ci_tool: str            # 'GitHub' | 'None'

    @property
    def id(self) -> str:
        return (
            f"pg={self.use_postgresql}"
            f"-otel={self.use_opentelemetry}"
            f"-ci={self.ci_tool}"
        )

    def as_extra_context(self) -> dict[str, str]:
        return {
            "use_postgresql": self.use_postgresql,
            "use_opentelemetry": self.use_opentelemetry,
            "ci_tool": self.ci_tool,
            "use_docker": "y",
        }


MATRIX: list[Combo] = [
    Combo(pg, otel, ci)
    for pg, otel, ci in product(
        ("n", "y"),
        ("n", "y"),
        ("GitHub", "None"),
    )
]

IDS: list[str] = [c.id for c in MATRIX]
