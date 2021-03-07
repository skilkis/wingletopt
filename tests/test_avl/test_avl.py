import math
from typing import List

import pytest

from wingletopt import avl


@pytest.fixture()
def surface() -> avl.Surface:
    """Quasi-infinite wing surface with chord = 1 m, span = 2000 m."""
    root_section = avl.Section(
        leading_edge_point=avl.Point(0, 0, 0),
        chord=1,
        airfoil=avl.NacaAirfoil("0012"),
    )
    tip_section = avl.Section(
        leading_edge_point=avl.Point(0, 1e3, 0),
        chord=1,
        airfoil=avl.NacaAirfoil("0012"),
    )
    return avl.Surface(
        name="wing",
        n_chordwise=20,
        chord_spacing=avl.Spacing.cosine,
        n_spanwise=20,
        span_spacing=avl.Spacing.cosine,
        y_duplicate=0.0,
        sections=[root_section, tip_section],
    )


@pytest.fixture
def geometry(surface: avl.Surface) -> avl.Geometry:
    """Sample test geometry for AVL."""
    return avl.Geometry(
        name="test_wing",
        reference_area=2e3,
        reference_chord=1,
        reference_span=2e3,
        reference_point=avl.Point(0, 0, 0),
        surfaces=[surface],
    )


@pytest.fixture
def cases(alpha) -> List[avl.Case]:
    """Returns a iterable :py:class:`avl.Case` for ``alpha``."""
    return [avl.Case(name=f"alpha={alpha}", alpha=alpha)]


def test_avl_monkeypatch(geometry: avl.Geometry) -> None:
    """Tests if a :py:class:`avl.Session` can be run without config."""
    avl_session = avl.Session(geometry, cases=[avl.Case("test_case", alpha=0)])
    avl_session.run_all_cases()  # This should succeed


@pytest.fixture
def expected_lift(alpha: float) -> float:
    """Calculates the expected infinite span wing lift coefficient."""
    return 2 * math.pi * math.radians(alpha)


@pytest.mark.parametrize("alpha", [0, 5, 10])
def test_avl_lift(geometry, cases, expected_lift):
    """Tests AVL output for correct lift coefficient and gradient."""
    avl_session = avl.Session(geometry, cases=cases)
    result = avl_session.run_all_cases()[cases[0].name]

    # Checking if CL value is as expected
    assert result["Totals"]["CLtot"] == pytest.approx(expected_lift, rel=0.1)

    # Checking if CLa is close to 2π
    assert result["StabilityDerivatives"]["CLa"] == pytest.approx(
        2 * math.pi, rel=0.1
    )
