"""Best-fit sizing. All sizing maths lives here so results are repeatable.

PLACEHOLDER RULES: the decision logic below is a working draft. The pattern team must
confirm the tolerances, alteration limits and the measure used for each garment before
this goes live. The golden test cases in tests/test_sizing.py encode the agreed behaviour.

Conventions:
- target_cm: the body measurement a size is cut for.
- tolerance_cm: how far a customer can be from target and still fit the standard pattern.
- alteration amount = measured - target. Positive means the customer is larger than the size,
  so the pattern must be let out by that many centimetres.
"""

from dataclasses import dataclass, field


@dataclass
class SizeResult:
    base_size: str
    decision: str  # "standard" | "alteration" | "custom"
    alterations: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def best_fit(measurements: dict[str, float], chart: list[dict], alteration_limit_cm: float) -> SizeResult:
    if not chart:
        raise ValueError("no size chart for this product")

    by_size: dict[str, dict[str, dict]] = {}
    for row in chart:
        by_size.setdefault(row["size"], {})[row["measure"]] = row

    # Pick the size whose targets are closest to the customer's measurements.
    best_size, best_total, best_rows, best_measures = None, None, None, None
    for size, rows in by_size.items():
        common = [m for m in rows if m in measurements]
        if not common:
            continue
        total = sum(abs(measurements[m] - rows[m]["target_cm"]) for m in common)
        if best_total is None or total < best_total:
            best_size, best_total, best_rows, best_measures = size, total, rows, common

    if best_size is None:
        raise ValueError("measurements do not match any measure in the size chart")

    diffs = {
        m: round(measurements[m] - float(best_rows[m]["target_cm"]), 1)
        for m in best_measures
    }
    out_of_tolerance = {
        m: d for m, d in diffs.items()
        if abs(d) > float(best_rows[m]["tolerance_cm"])
    }

    if not out_of_tolerance:
        return SizeResult(base_size=best_size, decision="standard")

    if all(abs(d) <= alteration_limit_cm for d in out_of_tolerance.values()):
        return SizeResult(
            base_size=best_size,
            decision="alteration",
            alterations=out_of_tolerance,
            notes=[f"{m}: {d:+} cm" for m, d in out_of_tolerance.items()],
        )

    return SizeResult(
        base_size=best_size,
        decision="custom",
        alterations=out_of_tolerance,
        notes=["outside alteration limit: manual pattern work"],
    )
