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

"""Thin wrapper around `avlwrapper` to monkeypatch the default config.

Warning:
    Wrapper inception! This violates the DRY principal on imports, thus
    a better alternative can be investigated in the future.
"""

import functools
from pathlib import Path

import pkg_resources
from avlwrapper import (
    Case,
    Configuration,
    Control,
    DataAirfoil,
    DesignVar,
    FileAirfoil,
    FileWrapper,
    Geometry,
    NacaAirfoil,
    OutputReader,
    Parameter,
    Point,
    ProfileDrag,
    Section,
    Session,
    Spacing,
    Surface,
    Symmetry,
    Vector,
    create_sweep_cases,
    default_config,
    partitioned_cases,
    show_image,
)

__all__ = [
    "Case",
    "Configuration",
    "Control",
    "DataAirfoil",
    "DesignVar",
    "FileAirfoil",
    "FileWrapper",
    "Geometry",
    "NacaAirfoil",
    "OutputReader",
    "Parameter",
    "Point",
    "ProfileDrag",
    "Section",
    "Session",
    "Spacing",
    "Surface",
    "Symmetry",
    "Vector",
    "create_sweep_cases",
    "partitioned_cases",
    "show_image",
    "Result",
]


def get_avl_configuration() -> Configuration:
    bin_path = Path(
        pkg_resources.resource_filename("wingletopt", "avl/avl.exe")
    )
    patched_config = default_config
    patched_config.settings["avl_bin"] = bin_path
    return patched_config


def monkeypatch_session_config(config: Configuration) -> None:
    Session.__init__ = functools.partialmethod(Session.__init__, config=config)


monkeypatch_session_config(config=get_avl_configuration())
