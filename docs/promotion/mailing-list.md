# QGIS user mailing list announcement

**List:** [qgis-user@lists.osgeo.org](https://lists.osgeo.org/mailman/listinfo/qgis-user)  
**Subscribe** before posting if needed.

---

## Subject

```
[ANN] HydroDrop 1.0 — point-source water volume simulation on DEMs (QGIS 3.28+ / 4.x)
```

---

## Body

Hello,

I'd like to announce **HydroDrop 1.0**, an open-source QGIS plugin for interactive **point-source ponding** on digital elevation models.

**Question it answers:** If I pour a given volume of water (m³) at a map location, where does it accumulate and where does it overflow?

The engine uses RichDEM Fill-Spill-Merge (depression hierarchy). It is intended for engineering what-if work — stockpiles, bunds, mine water, stormwater ponds — not rainfall-runoff or open-channel hydraulics.

**Features:**
- Map-click pour point and volume input
- Depth visualization, live volume slider, fill animation
- Multi-drop sessions
- GeoTIFF / GeoPackage / CSV export
- Processing algorithm `hydrop:dropwater`

**Requirements:**
- QGIS 3.28 or later (including QGIS 4.x)
- Python package `richdem2` in the QGIS environment

**Links:**
- Source & documentation: https://github.com/ThermoTrack/HydroDrop
- Tutorial: https://github.com/ThermoTrack/HydroDrop/blob/main/docs/tutorial.md
- Issues: https://github.com/ThermoTrack/HydroDrop/issues

License: MIT. Author: Jaco Bekker (ThermoTrack).

Submission to plugins.qgis.org is in progress / completed — check Plugin Manager for "HydroDrop".

Suggestions and bug reports are welcome.

Regards,
Jaco Bekker
bekker.jj@gmail.com
