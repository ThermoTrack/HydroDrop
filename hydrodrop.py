"""HydroDrop — main plugin class."""

import os
import tempfile
import uuid

import numpy as np

from qgis.core import QgsProject, QgsRasterLayer
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QApplication, QMessageBox

from .gui.qt_compat import BOTTOM_DOCK_WIDGET_AREA, WAIT_CURSOR

from .engine.dephier_cache import compute_depression_hierarchy
from .engine.dem import capture_layer_spec, load_dem_from_gdal_source
from .engine.exceptions import HydroDropError, InvalidDemError, RichDEMNotAvailableError
from .engine.richdem_utils import richdem_available
from .engine.session import DropSession
from .engine.statistics import compute_statistics
from .engine.animation import generate_animation_frames
from .engine.raster import export_simulation_outputs, write_geotiff
from .gui.animation_controller import AnimationController
from .gui.depth_style import apply_depth_style
from .gui.maptool_click import DropWaterMapTool
from .gui.results_dock import ResultsDockWidget
from .gui.simulation_task import HydroDropSimulationTask
from .gui.toolbar import HydroDropToolbarWidget
from .gui.water_dialog import WaterDialog


class HydroDropPlugin:
    """QGIS plugin entry class."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.toolbar = None
        self.toolbar_widget = None
        self.map_tool = None
        self.results_dock = None
        self.animation = AnimationController(iface)
        self.session = None
        self._dialog = None
        self._last_pour = None
        self._last_pour_map = None
        self._depth_layer = None
        self._depth_layer_id = None
        self._depth_path = None
        self._dem = None
        self._hierarchy = None
        self._simulation_busy = False
        self._message_bar_item = None
        self._active_task = None
        self._layer_spec = None
        self._dem_source_layer_id = None
        self._last_pour_wgs84 = None
        self._cached_spec_key = None
        self._picking_new_pour = False

    def tr(self, message):
        return message

    def initGui(self):
        if not richdem_available():
            self._show_richdem_install_dialog()
            return

        self.toolbar = self.iface.addToolBar("HydroDrop")
        self.toolbar.setObjectName("HydroDropToolbar")

        self.toolbar_widget = HydroDropToolbarWidget()
        self.toolbar_widget.activateToolRequested.connect(self.activate_map_tool)
        self.toolbar_widget.runRequested.connect(self.run_from_toolbar)
        self.toolbar.addWidget(self.toolbar_widget)

        self.results_dock = ResultsDockWidget(self.iface)
        self.iface.addDockWidget(BOTTOM_DOCK_WIDGET_AREA, self.results_dock)

        self.map_tool = DropWaterMapTool(self.iface.mapCanvas(), self.iface)
        self.map_tool.pointClicked.connect(self.on_map_clicked)

        self.processing_provider = None
        try:
            from .processing.provider import HydroDropProvider
            self.processing_provider = HydroDropProvider()
            from qgis.core import QgsApplication
            QgsApplication.processingRegistry().addProvider(self.processing_provider)
        except Exception:
            pass

    def unload(self):
        if self.processing_provider is not None:
            from qgis.core import QgsApplication
            QgsApplication.processingRegistry().removeProvider(self.processing_provider)

        if self.map_tool:
            self.iface.mapCanvas().unsetMapTool(self.map_tool)

        if self.toolbar:
            del self.toolbar

        if self.results_dock:
            self.iface.mainWindow().removeDockWidget(self.results_dock)
            del self.results_dock

        for action in self.actions:
            self.iface.removePluginMenu("&HydroDrop", action)
            self.iface.removeToolBarIcon(action)

    def _show_richdem_install_dialog(self):
        QMessageBox.critical(
            self.iface.mainWindow(),
            "HydroDrop — RichDEM Required",
            "The richdem Python package is required.\n\n"
            "Install in the QGIS Python environment:\n"
            "  python -m pip install richdem2",
        )

    def activate_map_tool(self):
        if self.map_tool:
            self.iface.mapCanvas().setMapTool(self.map_tool)

    def on_map_clicked(self, eng_x, eng_y, elevation, map_x, map_y, warp_lon, warp_lat):
        self._last_pour = (eng_x, eng_y, elevation)
        self._last_pour_map = (map_x, map_y)
        self._last_pour_wgs84 = (warp_lon, warp_lat)

        if self._dialog is not None:
            self._dialog.update_pour_point(map_x, map_y, elevation)
            if self._picking_new_pour:
                self._picking_new_pour = False
                self._dialog.show()
                from qgis.core import Qgis
                self.iface.messageBar().pushMessage(
                    "HydroDrop",
                    "New pour point set — click Add Drop to place water here.",
                    level=Qgis.MessageLevel.Info,
                    duration=6,
                )
            return

        self._dialog = WaterDialog(map_x, map_y, elevation, self.iface.mainWindow())
        self._dialog.volumeChanged.connect(self.on_live_volume_changed)
        self._dialog.runRequested.connect(self.run_simulation)
        self._dialog.animateRequested.connect(self.run_animation)
        self._dialog.addDropRequested.connect(self.add_drop)
        self._dialog.newLocationRequested.connect(self.pick_new_pour_point)
        self._dialog.resetSessionRequested.connect(self.reset_session)
        self._dialog.show()

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self._simulation_busy = busy
        if self._dialog:
            self._dialog.set_busy(busy, message)
        if self.toolbar_widget:
            self.toolbar_widget.setEnabled(not busy)
        if busy:
            QApplication.setOverrideCursor(QCursor(WAIT_CURSOR))
            self._message_bar_item = self.iface.messageBar().createMessage(
                "HydroDrop",
                message or "Working…",
            )
            self.iface.messageBar().pushItem(self._message_bar_item)
        else:
            QApplication.restoreOverrideCursor()
            if self._message_bar_item is not None:
                self.iface.messageBar().popWidget(self._message_bar_item)
                self._message_bar_item = None

    def _on_task_progress(self, value: int, text: str) -> None:
        if self._dialog:
            self._dialog.set_progress(value, text)
        if self._message_bar_item is not None:
            self._message_bar_item.setText(f"HydroDrop: {text} ({value}%)")

    def _dem_layer_for_simulation(self):
        active = self.iface.activeLayer()
        if (
            active is not None
            and active.isValid()
            and not active.name().startswith("HydroDrop")
        ):
            return active

        if self._dem_source_layer_id:
            layer = QgsProject.instance().mapLayer(self._dem_source_layer_id)
            if layer is not None and layer.isValid():
                return layer

        return active

    def _run_async(self, description, runner, on_success):
        if self._simulation_busy:
            return

        try:
            layer = self._dem_layer_for_simulation()
            self._layer_spec = capture_layer_spec(layer)
            self._dem_source_layer_id = layer.id()
            if self.map_tool:
                self.map_tool.set_dem_layer(layer)
        except InvalidDemError as exc:
            QMessageBox.warning(self.iface.mainWindow(), "HydroDrop", str(exc))
            return

        self._set_busy(True, f"{description}…")

        def success(data):
            self._set_busy(False)
            self._active_task = None
            try:
                on_success(data)
            except Exception as exc:
                QMessageBox.warning(self.iface.mainWindow(), "HydroDrop", str(exc))

        def failure(exc):
            self._set_busy(False)
            self._active_task = None
            QMessageBox.warning(
                self.iface.mainWindow(),
                "HydroDrop",
                str(exc) if isinstance(exc, Exception) else "Simulation failed.",
            )

        self._active_task = HydroDropSimulationTask.add(
            description,
            runner,
            success,
            failure,
            on_progress=self._on_task_progress,
        )

    def _layer_spec_key(self, spec) -> tuple:
        return (spec["source"], spec.get("crs_authid", ""))

    def _simulation_runner(self, task, volume, *, add_new_drop=False, update_only=False):
        if self._layer_spec is None:
            raise InvalidDemError("No DEM layer captured.")

        def progress(value, text):
            task.report_progress(value, text)

        spec = self._layer_spec
        spec_key = self._layer_spec_key(spec)
        reuse_dem = (
            (add_new_drop or update_only)
            and self.session is not None
            and self.session.dem is not None
            and self.session.hierarchy is not None
            and self._cached_spec_key == spec_key
        )

        if reuse_dem:
            task.report_progress(10, "Using cached DEM…")
            dem = self.session.dem
            hierarchy = self.session.hierarchy
        else:
            lon = lat = None
            if self._last_pour_wgs84:
                lon, lat = self._last_pour_wgs84

            task.report_progress(5, "Loading DEM…")
            dem = load_dem_from_gdal_source(
                spec["source"],
                spec["crs_authid"],
                spec["crs_wkt"],
                lon=lon,
                lat=lat,
                source_id=spec["source_id"],
            )
            task.report_progress(15, "Computing depression hierarchy…")
            hierarchy = compute_depression_hierarchy(dem, progress)

        if self.session is None or self.session.dem.source_id != dem.source_id:
            session = DropSession(dem=dem, hierarchy=hierarchy)
        else:
            session = self.session
            session.dem = dem
            session.hierarchy = hierarchy

        x, y, _elev = self._last_pour
        if update_only and session.drops:
            session.drops[-1].volume_m3 = volume
            result = session.replay(progress_callback=progress)
        elif add_new_drop:
            result = session.add_drop(x, y, volume)
        else:
            if (
                session.drops
                and session.drops[-1].pour_x == x
                and session.drops[-1].pour_y == y
            ):
                session.drops[-1].volume_m3 = volume
                result = session.replay(progress_callback=progress)
            else:
                result = session.add_drop(x, y, volume)

        stats = compute_statistics(result, dem.cell_area_m2)
        task.report_progress(100, "Done")
        return {
            "result": result,
            "stats": stats,
            "dem": dem,
            "hierarchy": hierarchy,
            "session": session,
            "volume": volume,
        }

    def _apply_simulation_result(self, data, *, animate=False, export=False):
        self._dem = data["dem"]
        self._hierarchy = data["hierarchy"]
        self.session = data["session"]
        if self._layer_spec is not None:
            self._cached_spec_key = self._layer_spec_key(self._layer_spec)
        self._display_result(data["result"], data["stats"])

        if export and (
            self.toolbar_widget.export_raster or self.toolbar_widget.export_polygon
        ):
            self._export_outputs(data["result"], data["stats"])

        if animate:
            self.run_animation(data["volume"])

    def run_from_toolbar(self, volume):
        if not self._last_pour:
            QMessageBox.information(
                self.iface.mainWindow(),
                "HydroDrop",
                "Click on the map first to choose a pour point.",
            )
            self.activate_map_tool()
            return
        self.run_simulation(volume)

    def on_live_volume_changed(self, volume):
        if not self._last_pour or self.session is None or not self.session.drops:
            return
        if self._simulation_busy:
            return

        def runner(task):
            return self._simulation_runner(task, volume, update_only=True)

        self._run_async(
            "Updating volume",
            runner,
            lambda data: self._apply_simulation_result(data),
        )

    def run_simulation(self, volume):
        if not self._last_pour:
            return

        def runner(task):
            return self._simulation_runner(task, volume)

        self._run_async(
            "Running simulation",
            runner,
            lambda data: self._apply_simulation_result(
                data,
                animate=self.toolbar_widget.animate if self.toolbar_widget else False,
                export=True,
            ),
        )

    def add_drop(self, volume):
        if not self.session or not self.session.drops:
            QMessageBox.information(
                self.iface.mainWindow(),
                "HydroDrop",
                "Run a simulation first, then add more drops.",
            )
            return
        if not self._last_pour:
            QMessageBox.information(
                self.iface.mainWindow(),
                "HydroDrop",
                "Click the map to choose a pour point first.",
            )
            self.activate_map_tool()
            return

        self._execute_add_drop(volume)

    def pick_new_pour_point(self):
        """Switch to map tool to choose a different pour point for the next drop."""
        if not self.session or not self.session.drops:
            return
        self._picking_new_pour = True
        if self._dialog:
            self._dialog.hide()
        from qgis.core import Qgis

        self.iface.messageBar().pushMessage(
            "HydroDrop",
            "Click the map for the new pour point.",
            level=Qgis.MessageLevel.Info,
            duration=8,
        )
        self.activate_map_tool()

    def _execute_add_drop(self, volume):
        if not self._last_pour:
            return

        def runner(task):
            return self._simulation_runner(task, volume, add_new_drop=True)

        def on_success(data):
            self._apply_simulation_result(data)
            if self._dialog:
                self._dialog.show()
                mx, my = self._last_pour_map
                elev = self._last_pour[2]
                self._dialog.update_pour_point(mx, my, elev)

        self._run_async("Adding drop", runner, on_success)

    def reset_session(self):
        if self.session:
            self.session.reset()
        self._picking_new_pour = False
        self._cached_spec_key = None
        self._dem_source_layer_id = None
        if self.map_tool:
            self.map_tool.set_dem_layer(None)
        old_path = self._depth_path
        self._remove_depth_layer()
        self.animation.stop()
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
        self._depth_path = None

    def run_animation(self, volume):
        if not self._last_pour:
            return
        if self._dem is None or self._hierarchy is None:
            QMessageBox.information(
                self.iface.mainWindow(),
                "HydroDrop",
                "Run a simulation first, then click Animate.",
            )
            return

        x, y, _elev = self._last_pour

        def runner(task):
            row, col = self._dem.validate_pour_point(x, y)

            def progress(value, text):
                task.report_progress(value, text)

            # Animate filling from dry ground, not from the finished Run result.
            frames = generate_animation_frames(
                self._dem,
                row,
                col,
                volume,
                self._hierarchy,
                frame_count=20,
                initial_wtd=None,
                progress_callback=progress,
            )
            return {"frames": frames}

        def on_success(data):
            frames = data["frames"]
            max_depth = max(float(f.depth.max()) for f in frames) if frames else 0.0
            if max_depth <= 1e-6:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "HydroDrop",
                    "Animation generated no visible water.\n"
                    "Try a larger volume or check the pour point.",
                )
                return

            self.animation.set_callbacks(
                self._show_animation_frame,
                self._finish_animation,
            )
            self.animation.load_frames(frames)
            self.animation.play()

        self._run_async("Generating animation", runner, on_success)

    def _show_animation_frame(self, depth, index, total) -> None:
        self._publish_depth_array(
            depth,
            layer_name=f"HydroDrop Animation ({index + 1}/{total})",
            vivid=True,
        )

    def _finish_animation(self) -> None:
        if self.session and self.session.last_result is not None:
            self._publish_depth_array(
                self.session.last_result.depth,
                layer_name="HydroDrop Depth",
                vivid=False,
            )

    def _publish_depth_array(
        self,
        depth,
        *,
        layer_name="HydroDrop Depth",
        vivid=False,
    ) -> bool:
        """Write depth to GeoTIFF and show it — same path used by Run and Animate."""
        if self._dem is None:
            return False

        old_path = self._depth_path
        self._remove_depth_layer()

        tmp = os.path.join(
            tempfile.gettempdir(),
            f"hydrodrop_depth_{uuid.uuid4().hex[:8]}.tif",
        )
        write_geotiff(tmp, depth, self._dem)
        depth_layer = QgsRasterLayer(tmp, layer_name)
        if not depth_layer.isValid():
            return False

        max_d = float(np.nanmax(depth)) if depth.size else 0.0
        apply_depth_style(depth_layer, max_depth=max(max_d, 0.001), vivid=vivid)
        QgsProject.instance().addMapLayer(depth_layer, True)
        self._depth_layer = depth_layer
        self._depth_layer_id = depth_layer.id()
        self._depth_path = tmp

        if old_path and old_path != tmp and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

        self.iface.mapCanvas().refreshAllLayers()
        return True

    def _remove_depth_layer(self) -> None:
        if self._depth_layer_id:
            project = QgsProject.instance()
            if project.mapLayer(self._depth_layer_id) is not None:
                project.removeMapLayer(self._depth_layer_id)
        self._depth_layer = None
        self._depth_layer_id = None
        QApplication.processEvents()

    def _display_result(self, result, stats):
        self._publish_depth_array(
            result.depth,
            layer_name="HydroDrop Depth",
            vivid=False,
        )

        if self.toolbar_widget is None or self.toolbar_widget.show_statistics:
            self.results_dock.update_statistics(stats)

    def _export_outputs(self, result, stats):
        out_dir = QSettings().value("HydroDrop/lastExportDir", tempfile.gettempdir())
        paths = export_simulation_outputs(
            out_dir,
            self._dem,
            result.depth,
            result.surface,
            stats,
        )
        QMessageBox.information(
            self.iface.mainWindow(),
            "HydroDrop Export",
            "Exported:\n" + "\n".join(paths.values()),
        )
