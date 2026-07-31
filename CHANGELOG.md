# Changelog

All notable changes to HydroDrop are documented here.

## [1.0.0] - 2026-07-30

### Added

- Interactive drop-water map tool with pour-point dialog
- RichDEM Fill-Spill-Merge engine with depression hierarchy caching
- Geographic DEM auto-warp to local UTM
- Background simulation via QgsTask (non-blocking UI)
- Live volume slider with debounced replay
- Fill animation (~20 frames)
- Multi-drop sessions with **New Location** and **Add Drop**
- Statistics results dock
- Optional GeoTIFF, GeoPackage, and CSV export
- Processing algorithm `hydrop:dropwater`
- QGIS 4.x compatibility (Qt6 shims, API updates)
- Unit tests and GitHub Actions CI
- Documentation: installation, tutorial, how-it-works

### Author

- Jaco Bekker — initial release (MIT License)