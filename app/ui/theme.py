"""Dark theme: Fusion style + palette + a small stylesheet.

The image canvas uses a *neutral* mid-grey (no blue tint) so colours in the
photo are judged against a neutral surround, as in photo-editing software.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

# Colour tokens (kept here so widgets don't hardcode their own colours).
BG = "#1e1f22"          # window background
PANEL = "#26282c"       # side panels
PANEL_ALT = "#2d3035"   # inputs, list rows
BORDER = "#3a3d42"
TEXT = "#d8dadf"
TEXT_DIM = "#8b9099"
ACCENT = "#4c8dff"
CANVAS = "#2b2b2b"      # neutral grey behind the photo

STYLESHEET = f"""
QMainWindow, QWidget {{ background: {BG}; color: {TEXT}; }}
QMenuBar {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
QMenuBar::item:selected {{ background: {PANEL_ALT}; }}
QMenu {{ background: {PANEL}; border: 1px solid {BORDER}; }}
QMenu::item:selected {{ background: {ACCENT}; color: white; }}
QMenu::item:disabled {{ color: {TEXT_DIM}; }}
QStatusBar {{ background: {BG}; border-top: 1px solid {BORDER}; color: {TEXT_DIM}; }}
QStatusBar QLabel {{ color: {TEXT_DIM}; padding: 0 8px; }}
QSplitter::handle {{ background: {BORDER}; }}
QFrame#SidePanel {{ background: {PANEL}; }}
QFrame#SidePanel QWidget {{ background: {PANEL}; }}
QLabel#PanelTitle {{ font-weight: 600; font-size: 13px; padding: 10px 12px 6px 12px; }}
QLabel#SectionTitle {{ color: {TEXT_DIM}; font-size: 11px; text-transform: uppercase;
                       padding-top: 10px; }}
QLabel#Hint {{ color: {TEXT_DIM}; }}
QLabel:disabled {{ color: {TEXT_DIM}; }}
QListWidget {{ background: {PANEL}; border: none; }}
QListWidget::item:selected {{ background: {PANEL_ALT}; border: 1px solid {ACCENT}; }}
QGraphicsView {{ background: {CANVAS}; border: none; }}
QPushButton {{ background: {PANEL_ALT}; border: 1px solid {BORDER}; border-radius: 4px;
               padding: 5px 14px; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton:disabled {{ color: {TEXT_DIM}; }}
QPushButton#PrimaryButton {{ background: {ACCENT}; border-color: {ACCENT}; color: white; }}
QPushButton#PrimaryButton:disabled {{ background: {PANEL_ALT}; border-color: {BORDER};
                                       color: {TEXT_DIM}; }}
QSlider::groove:horizontal {{ height: 4px; background: {BORDER}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {TEXT}; width: 12px; margin: -5px 0;
                              border-radius: 6px; }}
QSlider::handle:horizontal:disabled {{ background: {TEXT_DIM}; }}
QScrollArea {{ border: none; }}
QToolTip {{ background: {PANEL_ALT}; color: {TEXT}; border: 1px solid {BORDER}; }}
QScrollBar:vertical {{ background: {PANEL}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px;
                               margin: 2px; }}
QScrollBar::handle:vertical:hover {{ background: {TEXT_DIM}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

/* Canvas toolbar + generic tool buttons */
QFrame#CanvasToolbar {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; }}
QFrame#CanvasToolbar QLabel {{ background: {PANEL}; color: {TEXT_DIM}; }}
QToolButton {{ background: transparent; border: 1px solid transparent; border-radius: 4px;
               padding: 3px 9px; color: {TEXT}; }}
QToolButton:hover {{ border-color: {BORDER}; }}
QToolButton:checked {{ background: {ACCENT}; color: white; }}
QToolButton:disabled {{ color: {TEXT_DIM}; }}

/* Collapsible sections in the side panels */
#SidePanel QFrame#Separator {{ background: {BORDER}; }}
#SidePanel QToolButton#SectionHeader {{ font-weight: 600; border: none; padding: 7px 0;
                                        text-align: left; }}
#SidePanel QToolButton#SectionReset {{ color: {TEXT_DIM}; font-size: 11px; padding: 2px 6px; }}
#SidePanel QToolButton#SectionReset:hover {{ color: {TEXT}; }}

/* Inputs (scoped to beat the #SidePanel background rule above) */
#SidePanel QSpinBox, #SidePanel QComboBox, QFrame#CanvasToolbar QComboBox {{
    background: {PANEL_ALT}; border: 1px solid {BORDER}; border-radius: 3px;
    padding: 1px 4px; min-height: 18px; }}
/* Hide the spin arrows by sizing them to zero (see SliderRow). */
#SidePanel QSpinBox::up-button, #SidePanel QSpinBox::down-button {{ width: 0; border: none; }}
#SidePanel QSpinBox:focus, #SidePanel QComboBox:focus {{ border-color: {ACCENT}; }}
#SidePanel QSpinBox:disabled, #SidePanel QComboBox:disabled,
QFrame#CanvasToolbar QComboBox:disabled {{ color: {TEXT_DIM}; }}
"""


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: BG,
        QPalette.ColorRole.WindowText: TEXT,
        QPalette.ColorRole.Base: PANEL_ALT,
        QPalette.ColorRole.AlternateBase: PANEL,
        QPalette.ColorRole.Text: TEXT,
        QPalette.ColorRole.Button: PANEL_ALT,
        QPalette.ColorRole.ButtonText: TEXT,
        QPalette.ColorRole.Highlight: ACCENT,
        QPalette.ColorRole.HighlightedText: "#ffffff",
        QPalette.ColorRole.ToolTipBase: PANEL_ALT,
        QPalette.ColorRole.ToolTipText: TEXT,
        QPalette.ColorRole.PlaceholderText: TEXT_DIM,
    }
    for role, colour in roles.items():
        palette.setColor(role, QColor(colour))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText,
                 QPalette.ColorRole.WindowText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(TEXT_DIM))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)
