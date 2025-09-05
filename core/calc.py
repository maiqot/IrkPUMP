from __future__ import annotations

from typing import Dict, List


def run_full_calc(inputs: Dict) -> Dict:
    """Stub calculation returning deterministic demo data.
    Replace with the ported formulas step by step.
    """
    curve_q: List[float] = [20, 40, 60, 80, 100, 120]
    curve_h: List[float] = [900, 850, 800, 740, 660, 560]
    return dict(
        tdh_m=740.0,
        pip_atm=32.1,
        void_fraction=18.4,
        work_q=float(inputs.get('targetFlowRate', 80.0)),
        work_h=740.0,
        curve_q=curve_q,
        curve_h=curve_h,
    )


