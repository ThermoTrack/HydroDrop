# Reddit post — r/QGIS

**Subreddit:** [r/QGIS](https://www.reddit.com/r/QGIS/)  
**When to post:** After GitHub release is live; ideally after plugins.qgis.org approval.

---

## Title options

- `[Plugin] HydroDrop — pour water on a DEM, see where it ponds and spills`
- `I made a QGIS plugin for “what if I dump 5000 m³ here?” on a DEM`

---

## Post body (copy below)

Hi r/QGIS,

I built **HydroDrop**, an open-source QGIS plugin for quick **point-source ponding** on a DEM:

> *If I pour X m³ of water here, where does it pond and where does it spill?*

**Use cases:** stockpile/runoff ponds, bund siting, mine water balances, stormwater what-if, tailings reconnaissance — anywhere you have a DEM and a volume, not a rainfall model.

**Features:**
- Click pour point → set volume (m³) → blue depth map
- Live volume slider
- Fill animation
- Multi-drop sessions (several pour points merge)
- Export depth/surface GeoTIFF, flood polygon, CSV stats
- QGIS 3.28+ and **4.x**
- Processing algorithm for batch runs

**Physics:** RichDEM Fill-Spill-Merge (gravity-only depression filling). **Not** channel flow or hydrology — separate ponds linked by spill paths.

**Install (manual for now):**
1. `pip install richdem2` in QGIS Python ([guide](https://github.com/ThermoTrack/HydroDrop/blob/main/docs/installation.md))
2. Clone/copy [github.com/ThermoTrack/HydroDrop](https://github.com/ThermoTrack/HydroDrop) into your QGIS plugins folder

*(Update this line when approved: “Or install from Plugin Manager — search HydroDrop”)*

**Docs:** [Tutorial](https://github.com/ThermoTrack/HydroDrop/blob/main/docs/tutorial.md) | [How it works](https://github.com/ThermoTrack/HydroDrop/blob/main/docs/how-it-works.md)

MIT license. Feedback and issues welcome on GitHub.

---

## Comment to pin (optional)

**Dependency:** needs `richdem2` in QGIS Python — on Windows use `richdem2`, not `richdem`. Full steps in the repo installation doc.
