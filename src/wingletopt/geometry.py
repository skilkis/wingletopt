# MIT License
#
# Copyright (c) 2021 San Kilkis
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Contains definitions that simplify creation of AVL geometry."""

import math
from functools import cached_property
from typing import Any, Tuple, Union

import numpy as np

from wingletopt import avl


def rotate_3d(point: avl.Point, axis: avl.Vector, angle: float) -> avl.Point:
    """Rotates ``point`` about ``axis`` by ``angle``.

    Args:
        point: Point to rotate
        axis: Rotation axis
        angle: Angle of rotation in SI degree

    Uses Rodrigues' formula: http://www.songho.ca/opengl/gl_rotate.html
    """
    c = math.cos((radians := math.radians(angle)))
    s = math.sin(radians)
    r = normalize(axis)
    p = np.array(point)

    return avl.Point(*((1 - c) * p.dot(r) * r + c * p + s * np.cross(r, p)))


def normalize(vector: Union[avl.Vector, np.ndarray]) -> np.ndarray:
    """Normalizes ``vector`` into a unit-vector."""
    return (v := np.array(vector)) / np.linalg.norm(v, ord=1)


class TrapezoidalLiftingSurface(avl.Surface):
    """Defines a trapezoidal lifting surface comprised of two sections.

    # TODO update documentation with proper inputs
    Args:
        root_chord: Root chord length in SI meter
        half_span: Half-span in SI meter
        taper_ratio: Taper ratio (tip chord / toot chord)
        le_sweep: Leading Edge Sweet in SI degree
        dihedral: Lifting surce dihedral angle in SI degree
        root_angle: Root incidence angle in SI degree
        tip_angle: Tip incidence angle in SI degree
    """

    __initialized__: bool = False

    def __init__(
        self,
        name: str,
        root_chord: float,
        half_span: float,
        taper_ratio: float,
        le_sweep: float,
        dihedral: float,
        root_angle: float,
        tip_angle: float,
        n_chordwise: int = 20,
        n_spanwise: int = 20,
        chord_spacing: avl.Spacing = avl.Spacing.cosine,
        span_spacing: avl.Spacing = avl.Spacing.cosine,
        y_duplicate: float = 0.0,
        component: int = 0,
        **avl_options,
    ):
        self.root_chord = root_chord
        self.half_span = half_span
        self.le_sweep = le_sweep
        self.taper_ratio = taper_ratio
        self.dihedral = dihedral
        self.root_angle = root_angle
        self.tip_angle = tip_angle
        super().__init__(
            name=name,
            n_chordwise=n_chordwise,
            n_spanwise=n_spanwise,
            chord_spacing=chord_spacing,
            span_spacing=span_spacing,
            y_duplicate=y_duplicate,
            component=component,
            sections=self.sections,
            **avl_options,
        )
        self.__initialized__ = True

    def __setattr__(self, name: str, value: Any) -> None:
        """Makes sure that values are not settable."""
        if not self.__initialized__:
            return super().__setattr__(name, value)
        else:
            raise ValueError(f'Attribute "{name}" cannot be set')

    @cached_property
    def root_le(self) -> avl.Point:
        """Root leading edge point."""
        return avl.Point(0, 0, 0)

    @cached_property
    def tip_le(self) -> avl.Point:
        """Tip leading edge point."""
        x = self.half_span * math.tan(math.radians(self.le_sweep))
        return rotate_3d(
            point=avl.Point(x, self.half_span, 0),
            axis=avl.Vector(1, 0, 0),
            angle=self.dihedral,
        )

    @cached_property
    def tip_chord(self) -> float:
        """Tip chord length in SI meter."""
        return self.root_chord * self.taper_ratio

    @cached_property
    def root_section(self) -> avl.Section:
        """Root :py:class:`avl.Section`."""
        return avl.Section(
            leading_edge_point=avl.Point(0, 0, 0),
            chord=self.root_chord,
            angle=self.root_angle,
        )

    @cached_property
    def tip_section(self) -> avl.Section:
        """Tip :py:class:`avl.Section`."""
        return avl.Section(
            leading_edge_point=self.tip_le,
            chord=self.tip_chord,
            angle=self.tip_angle,
        )

    @cached_property
    def sections(self) -> Tuple[avl.Section, ...]:
        """Tuple of :py:class:`Section` presented to AVL."""
        return (self.root_section, self.tip_section)

    @cached_property
    def mac(self) -> float:
        """Mean aerodynamic chord in SI meter."""
        c = self.root_chord
        t = self.taper_ratio
        return 2 * c * (1 + t + t ** 2) / (3 * (1 + t))

    @cached_property
    def mac_le(self) -> avl.Point:
        """Leading edge of the mean aerodynamic chord."""
        b = self.half_span * 2
        t = self.taper_ratio
        y_mac = (b * (1 + 2 * t)) / (6 * (1 + t))
        x_mac = math.tan(math.radians(self.le_sweep)) * y_mac
        return rotate_3d(
            point=avl.Point(x_mac, y_mac, 0),
            axis=avl.Vector(1, 0, 0),
            angle=self.dihedral,
        )

    @cached_property
    def reference_point(self) -> avl.Point:
        """Aerodynamic center located at the mean aerodynamic chord."""
        return avl.Point(
            x=self.mac_le.x + self.mac * 0.25, y=self.mac_le.y, z=self.mac_le.z
        )

    @cached_property
    def surface_area(self) -> float:
        """Surface area of the lifting surface in SI meter squared.

        Caution:
            Remember that this is the surface area of the half-wing.
        """
        return self.half_span * self.root_chord * (1 + self.taper_ratio) / 2
