from typing import List

import pytest

from wingletopt import avl

CHORD = 1.8
BUDZIAK_DATA = (
    # Rectangular wing data from pg. 41 of Kinga Budziak, 2015
    # A, alpha, e, CD, CL
    (5, 6.91, 0.9892, 0.01456, 0.47565),
    (7, 6.17, 0.9779, 0.01049, 0.47503),
    (9, 5.77, 0.9656, 0.00825, 0.47473),
    (10, 5.63, 0.9594, 0.00747, 0.47463),
    (11, 5.52, 0.9531, 0.00684, 0.47456),
    (13, 5.34, 0.9413, 0.00586, 0.47445),
    (15, 5.21, 0.9299, 0.00514, 0.47437),
)
"""Rectangular wing data from pg. 41 of Kinga Budziak, 2015

Columns represent aspect ratio, angle of attack, oswald span efficiency
factor, drag coefficient, and lift coefficient respectively.
"""


@pytest.fixture
def span(aspect: float) -> float:
    """Calculates the span required to satisfy ``aspect``."""
    return CHORD * aspect


@pytest.fixture
def area(span: float, aspect: float) -> float:
    """Calculates the surface area using ``span`` and ``aspect``."""
    return span ** 2 / aspect


@pytest.fixture
def surface(aspect: float) -> avl.Surface:
    """Defines the rectangular wing used by (Budziak, 2015).

    pg. 37-41 of Kinga Budziak, 2015:
    https://www.fzt.haw-hamburg.de/pers/Scholz/arbeiten/TextBudziak.pdf
    """
    root = avl.Section(leading_edge_point=avl.Point(0, 0, 0), chord=CHORD)
    tip = avl.Section(
        leading_edge_point=avl.Point(0, aspect * CHORD / 2, 0), chord=CHORD
    )
    return avl.Surface(
        name="wing",
        n_chordwise=8,
        chord_spacing=avl.Spacing.cosine,
        n_spanwise=12,
        span_spacing=avl.Spacing.neg_sine,
        y_duplicate=0.0,
        sections=[root, tip],
    )


@pytest.fixture
def aircraft(surface: avl.Surface, area: float, span: float) -> avl.Aircraft:
    """Sample test geometry for AVL."""
    return avl.Aircraft(
        name="test_aircraft",
        reference_area=area,
        reference_chord=CHORD,
        reference_span=span,
        reference_point=avl.Point(0.54, 0, 0),
        surfaces=[surface],
    )


@pytest.fixture
def cases(alpha) -> List[avl.Case]:
    """Returns a iterable :py:class:`avl.Case` for ``alpha``."""
    return [avl.Case(name=f"alpha={alpha}", alpha=alpha)]


@pytest.mark.parametrize("aspect", [10])
def test_avl_monkeypatch(aircraft: avl.Aircraft, tmpdir) -> None:
    """Tests if a :py:class:`avl.Session` can be run without config."""
    avl_session = avl.Session(aircraft, cases=[avl.Case("test_case", alpha=0)])
    avl_session.run_all_cases(directory=tmpdir)  # This should succeed


# Testing using values from pg. 41 of Kinga Budziak, 2015
@pytest.mark.parametrize(
    "aspect, alpha, oswald, expected_drag, expected_lift", BUDZIAK_DATA
)
def test_avl_lift(
    aircraft: avl.Aircraft, cases, oswald, expected_drag, expected_lift
):
    """Tests AVL output for correct span efficiency, lift and drag."""
    avl_session = avl.Session(aircraft, cases=cases)
    result = avl_session.run_all_cases()[cases[0].name]

    # Checking if CL value is as expected
    # assert result["Totals"][] ==
    assert result["Totals"]["e"] == pytest.approx(oswald, rel=1e-3)
    assert result["Totals"]["CDff"] == pytest.approx(expected_drag, rel=1e-2)
    assert result["Totals"]["CLff"] == pytest.approx(expected_lift, rel=1e-2)
