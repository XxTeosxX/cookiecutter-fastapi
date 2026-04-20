"""Single source of truth for the render + smoke matrix.

Matrix dimensions: use_postgresql × postgresql_version × use_opentelemetry × ci_tool
= 2 × 3 × 2 × 2 = 24 combos. No pruning — postgresql_version renders even when
use_postgresql='n' to validate cross-variable non-contamination.

use_docker is intentionally pinned to 'y' for the matrix: Docker is the primary
v0.1 deployment path, and varying it would multiply the matrix to 48 combos
without proportional coverage value. use_docker='n' is covered by a single
dedicated smoke test (see tests/test_smoke.py).
"""

from __future__ import annotations

from itertools import product
from typing import NamedTuple


class Combo(NamedTuple):
    use_postgresql: str       # 'y' | 'n'
    postgresql_version: str   # '18' | '17' | '16'
    use_opentelemetry: str    # 'y' | 'n'
    ci_tool: str              # 'GitHub' | 'None'

    @property
    def id(self) -> str:
        return (
            f"pg={self.use_postgresql}"
            f"-pgv={self.postgresql_version}"
            f"-otel={self.use_opentelemetry}"
            f"-ci={self.ci_tool}"
        )

    def as_extra_context(self) -> dict[str, str]:
        return {
            "use_postgresql": self.use_postgresql,
            "postgresql_version": self.postgresql_version,
            "use_opentelemetry": self.use_opentelemetry,
            "ci_tool": self.ci_tool,
            "use_docker": "y",
        }


MATRIX: list[Combo] = [
    Combo(pg, pgv, otel, ci)
    for pg, pgv, otel, ci in product(
        ("n", "y"),
        ("18", "17", "16"),
        ("n", "y"),
        ("GitHub", "None"),
    )
]

IDS: list[str] = [c.id for c in MATRIX]
