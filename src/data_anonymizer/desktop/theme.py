"""Application visual theme (Qt Style Sheet)."""

APP_STYLESHEET = """
QMainWindow {
    background-color: #f4f6f9;
}

QWidget#HeaderBar {
    background-color: #1e3a5f;
    border-bottom: 1px solid #152a45;
}

QLabel#AppTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 600;
}

QLabel#AppSubtitle {
    color: #a8c4e8;
    font-size: 12px;
}

QFrame#FileBanner {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 8px;
    padding: 4px;
}

QLabel#FileBannerTitle {
    color: #1e3a5f;
    font-weight: 600;
    font-size: 13px;
}

QLabel#FileBannerMeta {
    color: #5c6b7a;
    font-size: 12px;
}

QFrame#Panel {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 10px;
}

QLabel#PanelTitle {
    color: #1e3a5f;
    font-size: 14px;
    font-weight: 600;
    padding: 2px 0;
}

QLabel#PanelHint {
    color: #5c6b7a;
    font-size: 12px;
}

QToolBar {
    background: #ffffff;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    spacing: 8px;
    padding: 8px 12px;
}

QToolBar QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    color: #334155;
}

QToolBar QToolButton:hover {
    background: #eef2f7;
    border-color: #cbd5e1;
}

QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    min-width: 140px;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#PrimaryButton:pressed {
    background-color: #1e40af;
}

QPushButton#PrimaryButton:disabled {
    background-color: #94a3b8;
}

QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #1e3a5f;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 500;
}

QPushButton#SecondaryButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton#GhostButton {
    background: transparent;
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 6px 10px;
}

QPushButton#GhostButton:hover {
    background: #f1f5f9;
}

QLineEdit, QComboBox {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 10px;
    background: #ffffff;
    selection-background-color: #2563eb;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #2563eb;
}

QTableWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    alternate-background-color: #1e293b;
}

QTableWidget::item {
    color: #f1f5f9;
    padding: 6px 4px;
}

QTableWidget QCheckBox#FieldCheck {
    background: transparent;
    spacing: 0;
}

QTableWidget QCheckBox#FieldCheck::indicator {
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 2px solid #cbd5e1;
    background-color: #334155;
}

QTableWidget QCheckBox#FieldCheck::indicator:hover {
    border-color: #f8fafc;
    background-color: #475569;
}

QTableWidget QCheckBox#FieldCheck::indicator:checked {
    background-color: #2563eb;
    border-color: #93c5fd;
}

QTableWidget QCheckBox#FieldCheck::indicator:checked:hover {
    background-color: #3b82f6;
    border-color: #bfdbfe;
}

QTableWidget QComboBox#MethodCombo {
    background-color: #334155;
    color: #f8fafc;
    border: 1px solid #475569;
}

QTableWidget QComboBox#MethodCombo:disabled {
    background-color: #1e293b;
    color: #94a3b8;
    border-color: #334155;
}

QTableWidget QComboBox#MethodCombo QAbstractItemView {
    background-color: #1e293b;
    color: #f1f5f9;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #e2e8f0;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid #475569;
    font-weight: 600;
}

QTextEdit#PreviewPane {
    background-color: #0f172a;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    font-family: "Consolas", "Cascadia Mono", "Menlo", monospace;
    font-size: 12px;
    padding: 8px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QStatusBar {
    background: #ffffff;
    color: #475569;
    border-top: 1px solid #e2e8f0;
}

QLabel#EmptyTitle {
    font-size: 20px;
    font-weight: 600;
    color: #1e3a5f;
}

QLabel#EmptyHint {
    font-size: 13px;
    color: #64748b;
}

QLabel#StatBadge {
    background: #eff6ff;
    color: #1d4ed8;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 500;
}
"""
