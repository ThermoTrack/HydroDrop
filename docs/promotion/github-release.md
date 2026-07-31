# GitHub release v1.0.0

After pushing the promotion commit and tag to GitHub:

## Repository settings (once)

1. Open [github.com/ThermoTrack/HydroDrop](https://github.com/ThermoTrack/HydroDrop) → **Settings** → **General**
2. **About** (top right on main page → gear icon):
   - Description: `QGIS plugin — point-source water volume on DEMs (RichDEM Fill-Spill-Merge)`
   - Website: `https://github.com/ThermoTrack/HydroDrop`
   - Topics: `qgis`, `qgis-plugin`, `dem`, `hydrology`, `flood`, `ponding`, `richdem`, `gis`

## Create release

1. **Releases** → **Draft a new release**
2. Tag: `v1.0.0` (choose existing tag after `git push origin v1.0.0`)
3. Title: `HydroDrop 1.0.0`
4. Attach: `dist/HydroDrop-1.0.0.zip` (build with `.\scripts\build_plugin_zip.ps1`)
5. Add a screenshot from QGIS (Run + depth layer visible) — drag into release notes
6. Body (example):

```markdown
## HydroDrop 1.0.0

Interactive point-source water simulation on DEMs using RichDEM Fill-Spill-Merge.

### Features
- Map pour tool — click DEM, specify volume (m³), see ponding and spill
- Animation from 0 → target volume
- Multi-drop sessions
- GeoTIFF/CSV export, Processing algorithm `hydrop:dropwater`

### Install
1. **Plugin Manager** (after [plugins.qgis.org](https://plugins.qgis.org/) approval) — search HydroDrop
2. **Manual:** download ZIP below → extract to QGIS plugins folder → enable in Plugin Manager
3. **Dependency:** `pip install richdem2` in QGIS Python — see [installation.md](https://github.com/ThermoTrack/HydroDrop/blob/main/docs/installation.md)

Requires QGIS 3.28+ or 4.x. MIT License.
```

7. Publish release
