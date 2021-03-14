import math

import numpy as np
import pytest

from wingletopt import TrapezoidalLiftingSurface, avl
from wingletopt.geometry import normalize, rotate_3d


@pytest.mark.parametrize(
    "point, axis, angle, expected_result",
    [
        (avl.Point(0, 2, 0), avl.Vector(5, 0, 0), 90, avl.Point(0, 0, 2)),
        (avl.Point(1, 1, 1), avl.Vector(0, 0, 1), 90, avl.Point(-1, 1, 1)),
    ],
)
def test_rotate_3d(point, axis, angle, expected_result):
    """Tests if arbitrary rotations about an axis are correct."""
    result = rotate_3d(point, axis, angle)
    assert result == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "vector, expected_result",
    [
        (avl.Vector(3, 0, 0), np.array((1, 0, 0))),
        (np.array((0, 0, 5)), np.array((0, 0, 1))),
    ],
)
def test_normalize(vector, expected_result):
    """Tests if vectors get normalized correctly."""
    result = normalize(vector)
    assert result == pytest.approx(expected_result)


class TestTrapezoidalLiftingSurface:
    @pytest.fixture(scope="class")
    def instance(self):
        """Returns a test surface with no dihedral."""
        return TrapezoidalLiftingSurface(
            name="test_surface",
            root_chord=5.5,
            half_span=14,
            taper_ratio=2 / 5.5,
            le_sweep=math.degrees(math.atan(3.5 / 14)),
            dihedral=0,
            root_angle=0,
            tip_angle=0,
        )

    @pytest.fixture(scope="class")
    def dihedral_instance(self, instance):
        """Returns a test surface with dihedral."""
        return TrapezoidalLiftingSurface(
            name="test_surface_dihedral",
            root_chord=instance.root_chord,
            half_span=instance.half_span,
            taper_ratio=instance.taper_ratio,
            le_sweep=instance.le_sweep,
            dihedral=45,
            root_angle=instance.root_angle,
            tip_angle=instance.tip_angle,
        )

    def test_settable(self, instance):
        """Ensures that instance values are not settable."""
        for attr in vars(instance):
            with pytest.raises(ValueError):
                setattr(instance, attr, None)

    def test_root_le(self, instance):
        """Checking if the root leading edge is at 0, 0, 0."""
        assert instance.root_le == pytest.approx(avl.Point(0, 0, 0))

    def test_tip_le(self, instance, dihedral_instance):
        """Checking if the tip leading edge point is correct."""
        result = instance.tip_le
        assert result == pytest.approx(avl.Point(3.5, instance.half_span, 0))

        result = dihedral_instance.tip_le
        dihedral = math.radians(dihedral_instance.dihedral)
        assert result == pytest.approx(
            avl.Point(
                3.5,
                instance.half_span * math.cos(dihedral),
                instance.half_span * math.sin(dihedral),
            )
        )

    def test_tip_chord(self, instance):
        """Checking if the tip chord is correct."""
        assert instance.tip_chord == pytest.approx(2)

    def test_mac(self, instance):
        """Checking if the mean aerodyanmic chord is correct."""
        assert instance.mac == pytest.approx(4.022, rel=1e-3)

    def test_mac_le(self, instance, dihedral_instance):
        """Tests if the MAC leading edge is correct."""
        result = instance.mac_le
        assert result == pytest.approx(avl.Point(1.477, 5.911, 0), rel=1e-3)

        result = dihedral_instance.mac_le
        assert result == pytest.approx(
            avl.Point(1.477, 4.179, 4.179), rel=1e-3
        )

    def test_reference_point(self, instance):
        """Tests if the MAC aerodynamic center is correct."""
        result = instance.reference_point
        assert result == pytest.approx(avl.Point(2.4825, 5.911, 0), rel=1e-3)

    def test_surface_area(self, instance):
        """Tests if the half surface area is correct."""
        result = instance.surface_area
        assert result == pytest.approx(52.5, rel=1e-3)
