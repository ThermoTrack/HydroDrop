"""Animation playback — timer only; display handled by the plugin."""

from qgis.core import Qgis
from qgis.PyQt.QtCore import QTimer


class AnimationController:
    """Advance through precomputed frames and delegate map display to the plugin."""

    def __init__(self, iface):
        self.iface = iface
        self._frames = []
        self._index = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._next_frame)
        self._fps = 2
        self._on_frame = None
        self._on_finish = None

    def set_callbacks(self, on_frame, on_finish) -> None:
        self._on_frame = on_frame
        self._on_finish = on_finish

    def load_frames(self, frames) -> None:
        self.stop()
        self._frames = frames
        self._index = 0

    def play(self) -> None:
        if not self._frames:
            self._notify("No animation frames to play.", Qgis.MessageLevel.Warning)
            return

        if not self._on_frame:
            self._notify("Animation display is not configured.", Qgis.MessageLevel.Warning)
            return

        self._notify(
            f"Playing {len(self._frames)} frames — blue water should spread on the map.",
            Qgis.MessageLevel.Info,
        )
        self._index = 0
        self._on_frame(self._frames[0].depth, 0, len(self._frames))
        self._timer.start(int(1000 / self._fps))

    def stop(self) -> None:
        self._timer.stop()

    def _notify(self, text: str, level=Qgis.MessageLevel.Info) -> None:
        self.iface.messageBar().pushMessage("HydroDrop", text, level=level, duration=5)

    def _next_frame(self) -> None:
        self._index += 1
        if self._index >= len(self._frames):
            self._timer.stop()
            if self._on_finish:
                self._on_finish()
            self._notify(
                f"Animation complete ({len(self._frames)} frames).",
                Qgis.MessageLevel.Success,
            )
            return
        if self._on_frame:
            self._on_frame(
                self._frames[self._index].depth,
                self._index,
                len(self._frames),
            )
