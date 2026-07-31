# Submit HydroDrop to the QGIS Plugin Repository

Official guide: [plugins.qgis.org/docs/publish](https://plugins.qgis.org/docs/publish)

## Before you upload

1. Create an **OSGeo ID** at [plugins.qgis.org](https://plugins.qgis.org/) (Sign in / Register).
2. Build the ZIP: `.\scripts\build_plugin_zip.ps1`
3. Upload at [plugins.qgis.org/publish](https://plugins.qgis.org/publish/)

First upload is **manually reviewed** (usually a few days). Updates after approval go live automatically after security scan.

---

## Copy-paste: short description (metadata `description`)

```
Drop a volume of water anywhere on a DEM and simulate where it accumulates and overflows.
```

---

## Copy-paste: about field (already in metadata.txt — verify on upload)

```
Interactive point-source water volume simulation using RichDEM Fill-Spill-Merge.

Click a DEM, pour a volume in cubic metres, and see where water ponds and spills.

EXTERNAL DEPENDENCY: Python package richdem2 must be installed in the QGIS Python environment before use:
  pip install richdem2
Windows users: run the command with the QGIS Python executable, e.g.
  "C:\Program Files\QGIS 4.2.0\apps\Python312\python.exe" -m pip install richdem2

Supports QGIS 3.28+ and QGIS 4.x. Geographic DEMs (EPSG:4326) are auto-warped to local UTM.

Documentation: https://github.com/ThermoTrack/HydroDrop/blob/main/docs/tutorial.md
```

---

## Plugin details for the upload form

| Field | Value |
|-------|--------|
| Name | HydroDrop |
| Version | 1.0.0 |
| Author | Jaco Bekker |
| Email | bekker.jj@gmail.com |
| Repository | https://github.com/ThermoTrack/HydroDrop |
| Tracker | https://github.com/ThermoTrack/HydroDrop/issues |
| License | MIT (GPL-compatible) |
| Category | Raster |
| QGIS min | 3.28 |
| QGIS max | 4.99 |

## Tags (add in metadata or web form if available)

```
water, dem, hydrology, flood, ponding, terrain, depression, volume, richdem
```

## Review tips (from QGIS guidelines)

- ZIP contains single folder `HydroDrop/` with `metadata.txt`, `__init__.py`, `LICENSE`
- No `__pycache__`, `.git`, or `.pytest_cache` in ZIP
- `richdem2` dependency clearly stated in About
- README and tutorial linked from repository
- Icon: `icons/waterdrop.svg`
- **Screenshots for plugin page:** upload from `docs/images/`:
  - `pour-simulation-dialog.png` — main UI + depth result
  - `dem-on-map.png` — DEM on basemap context

---

## After approval

Users install via **Plugins → Manage and Install Plugins → search “HydroDrop”**.

Add the plugins.qgis.org link to README:

```
https://plugins.qgis.org/plugins/hydrodrop/
```

(URL may vary slightly after approval — check your plugin page.)
