# -*- coding: utf-8 -*-
"""
HydroDrop — Drop a volume of water anywhere on a DEM.
"""


def classFactory(iface):
    from .hydrodrop import HydroDropPlugin
    return HydroDropPlugin(iface)
