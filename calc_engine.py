"""Python calculation engine for IrkPUMP.

Step 1: Provide a stable entry point that mirrors the JS calculation call.
We will progressively port formulas from the HTML/JS to this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CalculationRequest:
    """Incoming parameters normalized from the UI."""

    payload: Dict[str, Any]


@dataclass
class CalculationResponse:
    """Result placeholder; will be extended as logic is ported."""

    ok: bool
    message: str
    echo: Dict[str, Any]


def run_calculation(params: Dict[str, Any]) -> CalculationResponse:
    """Execute calculation.

    For now this is a no-op that echoes inputs to verify Python <-> UI wiring.
    We will replace internals with actual formulas while keeping the interface.
    """
    try:
        request = CalculationRequest(payload=dict(params or {}))
        return CalculationResponse(ok=True, message="Python engine reached", echo=request.payload)
    except Exception as exc:  # noqa: BLE001
        return CalculationResponse(ok=False, message=str(exc), echo={})


