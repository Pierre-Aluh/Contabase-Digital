"""Tema dark global inspirado na referencia visual do projeto."""

from pathlib import Path


DARK_THEME_QSS = """
QMainWindow {
    background-color: #0f1a2e;
}
QWidget {
    background-color: #141d2a;
    color: #e7edf7;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 12px;
}
QFrame#Sidebar {
    background-color: #0f1a2e;
    border-right: 1px solid #2a4a6d;
}
QFrame#Topbar {
    background-color: #1a2f4d;
    border-bottom: 1px solid #2a4a6d;
}
QLabel#AppTitle {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
}
QLabel#SectionTitle {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}
QPushButton {
    background-color: #1a2f4d;
    border: 1px solid #2a4a6d;
    border-radius: 8px;
    color: #e7edf7;
    padding: 8px 12px;
}
QPushButton:hover {
    border: 1px solid #00a8ff;
    background-color: #213759;
}
QPushButton:checked {
    border: 1px solid #00d9ff;
    background-color: #1f3a57;
    color: #ffffff;
}
QComboBox, QLineEdit {
    background-color: #141d2a;
    border: 1px solid #2a4a6d;
    border-radius: 6px;
    padding: 6px 8px;
    color: #e7edf7;
}
QStatusBar {
    background-color: #1a2f4d;
    border-top: 1px solid #2a4a6d;
}
"""


def load_dark_theme() -> str:
    stylesheet_path = Path(__file__).with_name("stylesheet.qss")
    if stylesheet_path.exists():
        return stylesheet_path.read_text(encoding="utf-8")
    return DARK_THEME_QSS
