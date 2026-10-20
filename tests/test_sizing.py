"""Golden cases for the sizing rules. Replace the synthetic chart with the pattern team's
real charts and expected answers before go-live."""

import pytest

from app.sizing import best_fit

CHART = [
    {"size": "S", "measure": "bust", "target_cm": 88, "tolerance_cm": 2},
    {"size": "S", "measure": "waist", "target_cm": 70, "tolerance_cm": 2},
    {"size": "M", "measure": "bust", "target_cm": 94, "tolerance_cm": 2},
    {"size": "M", "measure": "waist", "target_cm": 76, "tolerance_cm": 2},
    {"size": "L", "measure": "bust", "target_cm": 100, "tolerance_cm": 2},
    {"size": "L", "measure": "waist", "target_cm": 82, "tolerance_cm": 2},
]
LIMIT = 3.0


def test_standard_fit_within_tolerance():
    r = best_fit({"bust": 94.5, "waist": 75.5}, CHART, LIMIT)
    assert r.base_size == "M"
    assert r.decision == "standard"
    assert r.alterations == {}


def test_alteration_when_outside_tolerance_but_under_limit():
    r = best_fit({"bust": 97, "waist": 76}, CHART, LIMIT)
    assert r.base_size == "M"
    assert r.decision == "alteration"
    assert r.alterations == {"bust": 3.0}


def test_custom_when_beyond_alteration_limit():
    r = best_fit({"bust": 110, "waist": 90}, CHART, LIMIT)
    assert r.decision == "custom"


def test_empty_chart_is_an_error():
    with pytest.raises(ValueError):
        best_fit({"bust": 90}, [], LIMIT)


def test_unknown_measures_are_an_error():
    with pytest.raises(ValueError):
        best_fit({"inseam": 80}, CHART, LIMIT)
