# Tutorial — Your first HydroDrop simulation

This walkthrough assumes QGIS 4.x with HydroDrop and RichDEM already installed. See [Installation](installation.md) if needed.

---

## 1. Load a DEM

1. Open QGIS and create or open a project.
2. Add your elevation raster: **Layer → Add Layer → Add Raster Layer**.
3. Select the DEM in the **Layers** panel (important — HydroDrop reads the active layer).

**Tip:** If your DEM covers a huge area, clip to a few km² around your site first (e.g. with **Raster → Extraction → Clip Raster by Extent**). Smaller DEMs run much faster.

---

## 2. Activate HydroDrop

1. Find the **HydroDrop** toolbar (water drop icon).
2. Click the **HydroDrop** tool button to activate the map click mode.
3. Click on the map where you want to pour water — on solid ground, not on NoData.

The **Pour Water** dialog opens with:

- Pour point coordinates and ground elevation
- Volume spin box (default 5000 m³)
- Preset volume buttons
- **Run**, **Animate**, **Add Drop**, **New Location**, **Reset Session**

---

## 3. Run a simulation

1. Enter a volume, e.g. **5000 m³**.
2. Click **Run**.

While working:

- A progress bar appears in the dialog
- The QGIS message bar shows status
- The map cursor shows “busy”

When finished:

- **HydroDrop Depth** layer appears (semi-transparent blue)
- Statistics appear in the **HydroDrop Results** dock (if enabled)

**Zoom** to the pour point if you do not see blue water immediately.

---

## 4. Adjust volume live

After a successful Run:

1. Drag the **volume slider** or change the spin box.
2. The simulation updates automatically (debounced ~400 ms).
3. The depth layer refreshes to show the new pond extent.

---

## 5. Animate the fill

1. Click **Run** first (animation needs a completed simulation).
2. Click **Animate**.

The plugin generates ~20 frames pouring from **dry ground** up to your chosen volume. Blue water spreads on the map over ~10 seconds. When finished, the final **HydroDrop Depth** layer is restored.

---

## 6. Add a second pour (multi-drop)

1. After the first Run, click **New Location**.
2. Click the map at a **second** pour point (on the DEM terrain).
3. Set a volume and click **Add Drop**.

Both pours merge in one session. The depth layer shows the **combined** ponding. Statistics reflect total stored volume across all drops.

To start over: **Reset Session**.

---

## 7. Export engineering outputs

On the HydroDrop toolbar, enable:

- **Export raster** — GeoTIFF depth and surface
- **Export polygon** — GeoPackage flood extent

Run a simulation with export enabled. A dialog lists output file paths when complete.

---

## 8. Processing toolbox (batch)

For scripting or batch runs:

1. Open **Processing → Toolbox**.
2. Search for **HydroDrop** or **Drop water**.
3. Run **Drop water on DEM** (`hydrop:dropwater`).

Provide DEM path, pour X/Y in the DEM CRS, and volume in m³.

---

## Interpreting results

- **Continuous blue along valleys** — water following natural drainage/depressions (expected).
- **Separate blue patches** — distinct depressions not yet connected; increase volume or add drops along the path.
- **Stored volume &lt; requested volume** — some water spilled out of the model domain or could not be retained in depressions.

See [How it works](how-it-works.md) for the physics behind these patterns.

---

## Example site (South Africa)

For testing near **Port Nolloth**, Northern Cape:

- WGS84: 30°33′11″ S, 17°35′02″ E
- UTM: **EPSG:32733** (WGS 84 / UTM zone 33S)

Use Copernicus GLO-30 or local survey DEM in or reprojected to that area.
