# How HydroDrop works

## The question HydroDrop answers

> *If I pour **V** cubic metres of water at point **P** on this terrain, where does it pond, how deep, and where does it spill?*

HydroDrop is designed for **rapid what-if analysis** on a DEM — stockpiles, bunds, stormwater ponds, tailings, dam break reconnaissance, and similar **point-source** scenarios. It is not a replacement for full hydrological or hydraulic modelling.

---

## Physical model (version 1.0)

HydroDrop implements **gravity-only ponding** with **depression overflow**:

1. Water is poured at a single cell (the pour point).
2. Water fills the local **depression** (pit) until the surface is level or volume runs out.
3. When a depression fills, water **spills** to the next downstream depression via RichDEM’s depression hierarchy.
4. The process repeats until the added volume is distributed or leaves the domain.

**Not modelled:** rainfall, infiltration, evaporation, evapotranspiration, pressurised pipes, overland flow routing independent of depressions, tidal effects, or structures (culverts, walls) unless represented in the DEM itself.

---

## Algorithm pipeline

```
DEM load  →  Depression hierarchy (cached)  →  Binary-search pour depth  →  Fill-Spill-Merge  →  Depth map + statistics
```

### 1. DEM loading

- The active QGIS raster layer is read via GDAL (thread-safe, no UI freeze).
- **Geographic** DEMs (EPSG:4326) are warped to a **local UTM** zone from the pour point for metre-based volumes.
- **Projected** DEMs in metres are used directly.

### 2. Depression hierarchy

RichDEM builds a **depression hierarchy** and **flow directions** for the terrain. This tree describes how pits connect and where spill occurs. The first run for a given DEM size is expensive; results are cached under:

```
~/.hydrodrop/cache/
```

### 3. Volume fill (binary search)

For requested volume **V** (m³):

- HydroDrop binary-searches the **water table depth (WTD)** added at the pour cell.
- Each trial runs **Fill-Spill-Merge (FSM)** to redistribute water across depressions.
- Iteration stops when stored volume matches **V** within tolerance (~0.5 m³).

Stored volume:

```
stored = Σ max(WTD, 0) × cell_area
```

### 4. Multi-drop sessions

Each **Add Drop** adds another pour point and volume. The session **replays** all drops in order on a shared WTD grid, so later pours see water already on the ground from earlier ones.

### 5. Outputs

| Output | Meaning |
|--------|---------|
| **Depth** | Water depth above ground (m) per cell |
| **Surface** | Ground elevation + depth |
| **Inundation mask** | Cells with depth &gt; 0 |
| **Statistics** | Requested vs stored volume, flooded area, max/mean depth |

---

## Why results can look “broken” or patchy

The map shows **per-cell depth**, not a smooth fluid animation. Common patterns:

| Appearance | Cause |
|------------|--------|
| Line along a valley | Water filling and spilling along a natural drainage line — **correct** |
| Separate blue blobs | Distinct depressions not yet connected — **correct** until volume links them |
| 1-pixel-wide gaps | Thin spill paths one cell wide — real but hard to see at screen scale |
| Blocky edges | DEM grid resolution — use a finer DEM or smaller clip for smoother visuals |

Increasing volume, clipping to a finer DEM, or adding drops along a flow path usually produces a more connected pattern. That reflects **terrain connectivity**, not a rendering bug.

---

## Coordinate systems

| Stage | CRS |
|-------|-----|
| Map click | Canvas / project CRS |
| Engine simulation | UTM metres (auto from geographic DEMs) |
| Result layers | Same as engine DEM |
| Display | QGIS on-the-fly reprojection to project CRS |

Always click pour points **on the source DEM**, not on HydroDrop result layers (depth/animation), which are NoData outside flooded cells.

---

## Limitations and assumptions

- **Cell-centre pours** — water enters one raster cell.
- **Flat surface within filled depressions** — FSM enforces level pool surfaces per depression logic.
- **No momentum** — no velocity, pressure, or wave effects.
- **DEM quality** — garbage in, garbage out: pits, artefacts, and vertical bias in the DEM directly affect ponds and spill paths.
- **Domain edge** — water leaving the raster edge is effectively lost from storage accounting.

---

## References

- RichDEM: [https://github.com/r-barnes/richdem](https://github.com/r-barnes/richdem)
- Fill-Spill-Merge and depression hierarchies: Barnes et al., richdem documentation and related terrain hydrology literature.

---

## Version

This document describes **HydroDrop 1.0.0** by Jaco Bekker (MIT License).
