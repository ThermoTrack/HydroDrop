# GIS Stack Exchange — when to mention HydroDrop

**Site:** [gis.stackexchange.com](https://gis.stackexchange.com)

Do **not** spam. Mention HydroDrop only when it directly answers the question.

---

## Good question types

- “Simulate ponding / flooding from a pour point on a DEM”
- “Volume of water in a depression on a raster”
- “Where would water accumulate if I release X m³ here?”
- “Fill sinks and spill volume on DEM QGIS”

---

## Answer template (adapt to the question)

For a **point-source volume** on a **DEM** (not rainfall, not river hydraulics), the open-source **HydroDrop** QGIS plugin uses RichDEM Fill-Spill-Merge to:

1. Build a depression hierarchy for the DEM
2. Pour the requested volume at your click point
3. Redistribute water across depressions and spill paths
4. Output depth raster and statistics

Repository: [github.com/ThermoTrack/HydroDrop](https://github.com/ThermoTrack/HydroDrop) (MIT, QGIS 3.28+ / 4.x)

Requires `richdem2` in QGIS Python. Tutorial: [docs/tutorial.md](https://github.com/ThermoTrack/HydroDrop/blob/main/docs/tutorial.md)

**Limitations:** gravity-only ponding between depressions — not pipe flow, infiltration, or rainfall. For catchment rainfall-runoff, use a hydrology model instead.

---

## Tags to watch

`qgis`, `dem`, `hydrology`, `flood`, `depression`, `sink`, `volume`, `terrain-analysis`

Set up RSS/email alerts on Stack Exchange for these tags if you want to help answer relevant threads.
