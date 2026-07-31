# Promoting HydroDrop

Ready-to-use copy for publishing and discovery. Repository: [ThermoTrack/HydroDrop](https://github.com/ThermoTrack/HydroDrop)

| Document | Use |
|----------|-----|
| [qgis-plugin-repository.md](qgis-plugin-repository.md) | Submit to official QGIS Plugin Manager |
| [reddit-qgis.md](reddit-qgis.md) | Post on r/QGIS |
| [mailing-list.md](mailing-list.md) | QGIS user mailing list announcement |
| [stack-exchange.md](stack-exchange.md) | Answer template for GIS Stack Exchange |
| [linkedin.md](linkedin.md) | Short professional post |

## Checklist

- [ ] Submit ZIP to [plugins.qgis.org](https://plugins.qgis.org/publish/) (OSGeo ID required)
- [ ] GitHub: add topics `qgis`, `qgis-plugin`, `dem`, `hydrology`, `flood`
- [ ] GitHub: create release **v1.0.0** with screenshot
- [ ] Post on r/QGIS (after plugin repo approval or with manual install link)
- [ ] Email qgis-user list (optional)
- [ ] Answer relevant Stack Exchange questions with link when helpful

## Build submission ZIP

From repository root:

```powershell
.\scripts\build_plugin_zip.ps1
```

Upload `dist\HydroDrop-1.0.0.zip` at [plugins.qgis.org/publish](https://plugins.qgis.org/publish/).
