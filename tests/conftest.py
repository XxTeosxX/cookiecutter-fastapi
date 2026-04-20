"""Shared fixtures for render-matrix and smoke tests."""

from __future__ import annotations

import pytest

from tests.matrix import IDS, MATRIX, Combo


@pytest.fixture(params=MATRIX, ids=IDS)
def combo(request) -> Combo:
    return request.param


@pytest.fixture
def rendered(cookies, combo: Combo):
    """Bake a project for the given combo and return pytest_cookies Result."""
    result = cookies.bake(extra_context=combo.as_extra_context())
    assert (
        result.exit_code == 0
    ), f"cookiecutter failed for {combo.id}: {result.exception}"
    assert result.exception is None, f"exception for {combo.id}: {result.exception}"
    return result
