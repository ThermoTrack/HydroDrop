# Contributing to HydroDrop

Thank you for your interest in contributing. HydroDrop is open source under the [MIT License](LICENSE).

## Getting started

1. Fork the repository on GitHub.
2. Clone your fork and install dev dependencies:

   ```bash
   pip install -r requirements-dev.txt
   pip install richdem2
   ```

3. Copy or symlink the plugin into your QGIS profile plugins folder (see [docs/installation.md](docs/installation.md)).
4. Run tests:

   ```bash
   python -m pytest tests/engine/ -v
   ```

## Pull requests

- Keep changes focused — one feature or fix per PR when possible.
- Match existing code style (PEP 8, minimal scope).
- Update documentation if behaviour changes.
- Ensure engine tests pass (RichDEM required for fill tests).

## Reporting issues

Use [GitHub Issues](https://github.com/ThermoTrack/HydroDrop/issues) and include:

- QGIS version
- Operating system
- DEM CRS and approximate size
- Steps to reproduce
- Expected vs actual behaviour

## Code of conduct

Be respectful and constructive. This is a technical tool for professional and community use.

## Copyright

Contributors retain copyright of their contributions. By submitting a pull request, you agree to license your contribution under the MIT License.
