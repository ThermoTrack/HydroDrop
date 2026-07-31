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

- [x] Promotion commit pushed to GitHub (`main`)
- [x] Tag **v1.0.0** pushed — [create release + attach ZIP](github-release.md) (manual, ~2 min)
- [ ] GitHub About: description + topics (see [github-release.md](github-release.md))
- [ ] Submit ZIP to [plugins.qgis.org](https://plugins.qgis.org/publish/) (OSGeo ID required)
- [ ] Post on r/QGIS — copy in [reddit-qgis.md](reddit-qgis.md)
- [ ] Email qgis-user list (optional) — [mailing-list.md](mailing-list.md)
- [ ] Answer relevant Stack Exchange questions — [stack-exchange.md](stack-exchange.md)

## Build submission ZIP

From repository root:

```powershell
.\scripts\build_plugin_zip.ps1
```

Upload `dist\HydroDrop-1.0.0.zip` at [plugins.qgis.org/publish](https://plugins.qgis.org/publish/).
