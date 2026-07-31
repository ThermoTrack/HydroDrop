# Installation

## Requirements

- QGIS **3.28+** or **4.x**
- Python **3.10+** (bundled with QGIS)
- **`richdem2`** Python package

---

## Step 1 — Install RichDEM

HydroDrop uses RichDEM’s depression hierarchy and Fill-Spill-Merge engine.

### Windows (QGIS standalone)

Use the QGIS Python executable, not system Python:

```powershell
& "D:\Program Files\QGIS 4.2.0\apps\Python312\python.exe" -m pip install richdem2
```

Adjust the path to match your QGIS install. On Windows, **`pip install richdem`** often fails to build; use **`richdem2`** instead (imports as `richdem`).

### OSGeo4W / Linux / macOS

```bash
python -m pip install richdem2
```

Run inside the same Python environment QGIS uses (`py3_env` on OSGeo4W).

### Verify

```bash
python -c "import richdem; print(richdem.__version__)"
```

---

## Step 2 — Install the plugin

### From source (development or manual install)

1. Clone or copy this repository into your QGIS profile plugins folder:

   | Platform | Path |
   |----------|------|
   | Windows (QGIS 4) | `%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\` |
   | Windows (QGIS 3) | `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` |
   | Linux | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |
   | macOS | `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/` |

2. The folder must be named `HydroDrop` and contain `metadata.txt` and `hydrodrop.py`.

3. Restart QGIS (or open **Plugins → Manage and Install Plugins**).

4. Enable **HydroDrop** on the **Installed** tab.

---

## Step 3 — Prepare a DEM

- Use a **single-band elevation raster** (GeoTIFF, etc.).
- **Projected CRS in metres** (e.g. UTM) gives the most predictable results.
- **Geographic** (EPSG:4326) DEMs work: HydroDrop warps to local UTM automatically when you Run.
- For large regional DEMs, **clip to your site** first — the first run builds a depression hierarchy and can take several minutes on huge rasters.

### Example data sources

- [Copernicus GLO-30](https://spacedata.copernicus.eu/) — global 30 m DEM
- [OpenTopography](https://opentopo.org/) — high-resolution lidar and DEM downloads
- Local survey or mine/planning DEMs

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| “RichDEM Required” on startup | Install `richdem2` in QGIS Python (see above) |
| Plugin not listed | Check folder name and path; restart QGIS |
| Simulation very slow | Clip DEM to site area; hierarchy is cached in `~/.hydrodrop/cache/` |
| Pour point on NoData | Click on the terrain DEM, not on HydroDrop result layers; use **New Location** after animation |
| Geographic DEM | Normal — plugin reprojects to UTM; message bar will note the target CRS |
