# HydroDrop

**Drop a volume of water anywhere on a DEM and simulate where it accumulates and overflows.**

HydroDrop is an open-source QGIS plugin for civil engineers, farmers, mine planners, and environmental consultants who need quick answers to questions like: *"If I pour 5,000 m³ here, where does it pond and where does it spill?"*

This is **not** a rainfall or river-flow model. It is a **gravity-only, point-source volume** simulation using [RichDEM](https://github.com/r-barnes/richdem) Fill-Spill-Merge (FSM).

**Author:** [Jaco Bekker](https://github.com/JacoBekker)  
**License:** [MIT](LICENSE)

---

## Features

- Click anywhere on a DEM to pour water at a point
- Specify volume in cubic metres (m³)
- Blue depth shading on the map
- Live volume slider — update the pond as you drag
- Fill animation (stepped pour from dry ground)
- Multi-drop sessions — successive pours merge naturally
- Engineering exports: depth raster, surface raster, flood polygon, statistics CSV
- Processing algorithm `hydrop:dropwater` for batch and scripting
- QGIS 3.28+ and **QGIS 4.x** (tested on 4.2)

---

## What it models (and what it does not)

| Included | Not included |
|----------|----------------|
| Gravity-driven ponding in depressions | Rainfall or runoff hydrology |
| Overflow/spill between depressions | Open-channel stream flow |
| Multi-point pour sessions | Infiltration, evaporation, pipes |
| Volume accounting (requested vs stored) | Dam breach, culverts, buildings |

See [How it works](docs/how-it-works.md) for the full explanation.

---

## Requirements

- **QGIS** 3.28 or later (including QGIS 4.x)
- A **DEM** raster (projected CRS preferred; geographic EPSG:4326 is auto-warped to local UTM)
- Python package **`richdem2`** (Windows: use `richdem2`, not `richdem`)

---

## Quick start

1. [Install RichDEM and the plugin](docs/installation.md)
2. Load a DEM and select it in the Layers panel
3. Click **HydroDrop** on the toolbar, then click the map pour point
4. Set volume (e.g. 5000 m³) and press **Run**

Full walkthrough: [Tutorial](docs/tutorial.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [Installation](docs/installation.md) | RichDEM, plugin install, troubleshooting |
| [Tutorial](docs/tutorial.md) | Step-by-step first simulation |
| [How it works](docs/how-it-works.md) | Physics, algorithm, interpreting results |
| [Changelog](CHANGELOG.md) | Release history |

---

## Outputs

When export options are enabled on the toolbar:

| File | Description |
|------|-------------|
| `WaterDepth.tif` | Standing water depth (m) |
| `WaterSurface.tif` | Water surface elevation (m) |
| `FloodExtent.gpkg` | Inundated area polygon |
| `Statistics.csv` | Requested/stored volume, flooded area, max depth |

---

## Development

```bash
pip install -r requirements-dev.txt
# Run tests with QGIS Python (richdem2 required):
python -m pytest tests/engine/ -v
```

CI runs on GitHub Actions (see `.github/workflows/test.yml`).

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT License — see [LICENSE](LICENSE). You may use, modify, and distribute this plugin freely; retain the copyright notice in copies.

---

## Roadmap

- River mode (polyline inflow)
- Burst pipe (flow rate × duration)
- Dam failure scenarios
- Culverts, roads, and buildings as flow modifiers
