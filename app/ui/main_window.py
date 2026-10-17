"""Main window: menus, three-column layout, status bar.

Layout:  [Photos] | [Image canvas] | [Adjustments]
Actions whose feature is not built yet are created disabled; the step that
implements a feature connects and enables its action.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings, Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app import APP_ID, APP_NAME, __version__
from app.image.io import SUPPORTED_EXTENSIONS, ImageLoadError, LoadedImage, load_image
from app.ui.adjust_panel import AdjustPanel
from app.ui.canvas_toolbar import CanvasToolbar
from app.ui.image_view import ImageView
from app.ui.photo_panel import PhotoPanel
from app.ui.qt_image import rgb_to_qimage

log = logging.getLogger(__name__)

DEFAULT_SPLITTER_SIZES = [220, 880, 300]
# Longest side of the on-screen preview; export always uses full resolution.
PREVIEW_MAX_DIM = 1600
OPEN_FILTER = "Images ({})".format(" ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS))


class MainWindow(QMainWindow):
    def __init__(self, settings: QSettings | None = None) -> None:
        super().__init__()
        # Window geometry/splitter persistence. Tests pass a temporary INI file.
        self._settings = settings if settings is not None else QSettings(APP_ID, APP_ID)
        self.setWindowTitle(f"{APP_NAME} {__version__}")
        self.resize(1400, 900)
        self.setMinimumSize(900, 600)

        self.photo_panel = PhotoPanel()
        self.canvas_toolbar = CanvasToolbar()
        self.image_view = ImageView()
        self.adjust_panel = AdjustPanel()

        # Centre column: toolbar on top of the canvas.
        self.canvas_area = QWidget()
        canvas_layout = QVBoxLayout(self.canvas_area)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self.canvas_toolbar)
        canvas_layout.addWidget(self.image_view, 1)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.photo_panel)
        self.splitter.addWidget(self.canvas_area)
        self.splitter.addWidget(self.adjust_panel)
        self.splitter.setStretchFactor(1, 1)  # extra width goes to the canvas
        self.splitter.setCollapsible(1, False)
        self.splitter.setHandleWidth(1)
        self.splitter.setSizes(DEFAULT_SPLITTER_SIZES)
        self.setCentralWidget(self.splitter)

        self.current: LoadedImage | None = None
        self.image_view.zoom_changed.connect(self._update_zoom_label)

        self.actions: dict[str, QAction] = {}
        self._build_menus()
        self._build_status_bar()
        self._restore_layout()

    # ----------------------------------------------------------------- menus
    def _action(
        self,
        key: str,
        text: str,
        shortcut: QKeySequence | QKeySequence.StandardKey | str | None = None,
        enabled: bool = False,
    ) -> QAction:
        action = QAction(text, self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        action.setEnabled(enabled)
        self.actions[key] = action
        return action

    def _build_menus(self) -> None:
        bar = self.menuBar()

        file_menu = bar.addMenu("&File")
        open_action = self._action("open_image", "Open Image…", "Ctrl+O", enabled=True)
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)
        file_menu.addAction(self._action("open_folder", "Open Folder…", "Ctrl+Shift+O"))
        file_menu.addSeparator()
        file_menu.addAction(self._action("export", "Export…", "Ctrl+E"))
        file_menu.addSeparator()
        quit_action = self._action("quit", "Quit", "Ctrl+Q", enabled=True)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        edit_menu = bar.addMenu("&Edit")
        edit_menu.addAction(self._action("undo", "Undo", "Ctrl+Z"))
        edit_menu.addAction(self._action("redo", "Redo", "Ctrl+Shift+Z"))
        edit_menu.addSeparator()
        edit_menu.addAction(self._action("copy_settings", "Copy Settings", "Ctrl+Shift+C"))
        edit_menu.addAction(self._action("paste_settings", "Paste Settings", "Ctrl+Shift+V"))

        view_menu = bar.addMenu("&View")
        view_menu.addAction(self._action("zoom_in", "Zoom In", "Ctrl+="))
        view_menu.addAction(self._action("zoom_out", "Zoom Out", "Ctrl+-"))
        view_menu.addAction(self._action("zoom_fit", "Fit to Window", "Ctrl+0"))
        view_menu.addAction(self._action("zoom_100", "Actual Size (100%)", "Ctrl+1"))
        view_menu.addSeparator()
        view_menu.addAction(self._action("before_after", "Before / After", "\\"))
        view_menu.addAction(self._action("show_mask", "Show Mask (debug)", "Ctrl+M"))
        view_menu.addSeparator()
        for key, text, shortcut, panel in (
            ("toggle_photos", "Photos Panel", "Ctrl+Alt+1", self.photo_panel),
            ("toggle_adjust", "Adjustments Panel", "Ctrl+Alt+2", self.adjust_panel),
        ):
            action = self._action(key, text, shortcut, enabled=True)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(panel.setVisible)
            view_menu.addAction(action)

        # "Export" button at the right end of the menu bar, as in the mock-up.
        self.export_button = QPushButton("Export")
        self.export_button.setObjectName("PrimaryButton")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.actions["export"].trigger)
        bar.setCornerWidget(self.export_button, Qt.Corner.TopRightCorner)

    # ------------------------------------------------------------ status bar
    def _build_status_bar(self) -> None:
        status = self.statusBar()
        self.view_mode_label = QLabel("View: After")
        self.zoom_label = QLabel("Zoom: –")
        self.device_label = QLabel("AI Device: chưa bật")
        self.device_label.setToolTip("AI được bật từ Phase 2")
        for label in (self.view_mode_label, self.zoom_label, self.device_label):
            status.addPermanentWidget(label)
        status.showMessage("Ready")

    # ----------------------------------------------------------- open image
    def open_image_dialog(self) -> None:
        start_dir = str(self._settings.value("paths/last_open_dir", str(Path.home())))
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", start_dir, OPEN_FILTER)
        if filename:
            self.open_image_path(Path(filename))

    def open_image_path(self, path: Path) -> bool:
        """Load `path` into the canvas. Errors are shown to the user, never raised."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            loaded = load_image(path, max_dim=PREVIEW_MAX_DIM)
        except ImageLoadError as exc:
            QApplication.restoreOverrideCursor()
            log.warning("Open failed: %s", exc)
            QMessageBox.warning(self, "Không mở được ảnh", str(exc))
            return False
        QApplication.restoreOverrideCursor()

        self.current = loaded
        self.image_view.set_image(rgb_to_qimage(loaded.rgb))
        self._settings.setValue("paths/last_open_dir", str(path.parent))
        self.setWindowTitle(f"{path.name} — {APP_NAME} {__version__}")
        self.statusBar().showMessage(describe(loaded))
        return True

    def _update_zoom_label(self, *_: object) -> None:
        if self.current is None or not self.image_view.has_image():
            self.zoom_label.setText("Zoom: –")
            return
        # Zoom relative to the *original* pixels, not the preview's.
        preview_w = self.current.size[0]
        original_w = self.current.original_size[0]
        percent = self.image_view.zoom_factor() * preview_w / original_w * 100
        self.zoom_label.setText(f"Zoom: {percent:.0f}%")

    # ------------------------------------------------------- layout persist
    def _restore_layout(self) -> None:
        settings = self._settings
        geometry = settings.value("window/geometry")
        splitter = settings.value("window/splitter")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)
        if isinstance(splitter, QByteArray):
            self.splitter.restoreState(splitter)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        settings = self._settings
        settings.setValue("window/geometry", self.saveGeometry())
        settings.setValue("window/splitter", self.splitter.saveState())
        super().closeEvent(event)


def describe(image: LoadedImage) -> str:
    """Status-bar summary, e.g. "photo.jpg — 6000×4000 — 7.2 MB"."""
    w, h = image.original_size
    parts = [image.path.name, f"{w}×{h}", f"{image.file_size / 1_048_576:.1f} MB"]
    if image.had_alpha:
        parts.append("nền trong suốt hiển thị trên nền trắng")
    return " — ".join(parts)
