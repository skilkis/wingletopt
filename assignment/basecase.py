"""Defines the base case for Assignment 5 of Aicraft Aerodynamics."""

import math

from wingletopt import avl
from wingletopt.geometry import TrapezoidalLiftingSurface

wing = TrapezoidalLiftingSurface(
    name="wing",
    root_chord=5.5,
    half_span=14,
    taper_ratio=2 / 5.5,
    le_sweep=math.degrees(math.atan(3.5 / 14)),
)

winglet = TrapezoidalLiftingSurface(
    name="winglet",
    root_chord=0.8 * wing.tip_chord,
    half_span=wing.half_span * 0.06,
    taper_ratio=0.4,
    le_sweep=30,
    dihedral=0,
    root_angle=0,
    tip_angle=0,
    translation=avl.Vector(
        x=wing.tip_le.x + 0.2 * wing.tip_chord,
        y=wing.tip_le.y,
        z=wing.tip_le.z,
    ),
)

comp_wing = avl.Geometry(
    name="wing",
    reference_area=2 * wing.surface_area,
    reference_chord=wing.mac,
    reference_span=2 * wing.half_span,
    reference_point=wing.reference_point,
    surfaces=(wing, winglet),
)

# ISA values at h = 6000 m
FLIGHT_CONDITION = avl.Case(
    "FLIGHT_CONDITION",
    avl.Parameter("alpha", 0.6, "CL"),  # Find alpha such that CL = 0.6
    mach=0.7,
    density=0.659697,
    velocity=316.428 * 0.7,
)
session = avl.Session(geometry=comp_wing, cases=[FLIGHT_CONDITION])

if __name__ == "__main__":
    result = session.run_all_cases()[FLIGHT_CONDITION.name]
