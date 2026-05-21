"""Main window — load, configure fields, preview, export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from data_anonymizer.adapters.registry import list_supported_extensions
from data_anonymizer.core.engine import AnonymizationSession
from data_anonymizer.core.rules import FieldRule, method_options_for
from data_anonymizer.export_naming import default_export_path
from data_anonymizer.method_guidance import method_select_options, select_tooltip

SAMPLES_DIR = Path(__file__).resolve().parents[3] / "samples"


@dataclass
class _RowState:
    field_id: str
    enabled: bool
    method: str


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Data Anonymizer")
        self.resize(1200, 760)
        self.setMinimumSize(960, 600)

        self._session = AnonymizationSession()
        self._rows: list[_RowState] = []
        self._preview_count = 0
        self._preview_ready = False

        self._stack: QStackedWidget | None = None
        self._export_act: QAction | None = None
        self._file_title: QLabel | None = None
        self._file_meta: QLabel | None = None
        self._selection_badge: QLabel | None = None
        self._filter: QLineEdit | None = None
        self._table: QTableWidget | None = None
        self._salt: QLineEdit | None = None
        self._preview: QTextEdit | None = None
        self._preview_stats: QLabel | None = None
        self._btn_preview: QPushButton | None = None
        self._btn_export: QPushButton | None = None
        self._workspace: QWidget | None = None

        self._build_menu()
        self._build_ui()
        self._bind_shortcuts()
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._set_workspace_enabled(False)
        self._show_idle()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&Fișier")
        open_act = QAction("Deschide…", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self._open_file)
        file_menu.addAction(open_act)

        self._export_act = QAction("Exportă anonimizat…", self)
        self._export_act.setShortcut(QKeySequence.StandardKey.Save)
        self._export_act.triggered.connect(self._export_file)
        self._export_act.setEnabled(False)
        file_menu.addAction(self._export_act)
        file_menu.addSeparator()

        quit_act = QAction("Ieșire", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        samples_menu = self.menuBar().addMenu("E&xemple")
        for name, fname in (
            ("Pacienți (XML medical)", "medical_patient_sample.xml"),
            ("Charts (XML)", "feed_sample.xml"),
        ):
            act = QAction(name, self)
            act.triggered.connect(lambda _=False, f=fname: self._load_sample(f))
            samples_menu.addAction(act)

        help_menu = self.menuBar().addMenu("&Ajutor")
        about = QAction("Despre", self)
        about.triggered.connect(self._show_about)
        help_menu.addAction(about)

    def _bind_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+P"), self, self._run_preview)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_header())

        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_empty_state())
        self._workspace = self._build_workspace()
        self._stack.addWidget(self._workspace)
        root_layout.addWidget(self._stack, stretch=1)

    def _build_header(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("HeaderBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 14, 20, 14)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Data Anonymizer")
        title.setObjectName("AppTitle")
        sub = QLabel("Anonimizare date — fișierul original rămâne neschimbat")
        sub.setObjectName("AppSubtitle")
        titles.addWidget(title)
        titles.addWidget(sub)
        layout.addLayout(titles)
        layout.addStretch()
        return bar

    def _build_empty_state(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Începeți prin încărcarea unui fișier")
        title.setObjectName("EmptyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint = QLabel(
            "Selectați câmpurile de anonimizat, previzualizați rezultatul\n"
            "și exportați un fișier nou — fără a modifica sursa.",
        )
        hint.setObjectName("EmptyHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_open = QPushButton("Deschide fișier")
        btn_open.setObjectName("PrimaryButton")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(self._open_file)

        samples_row = QHBoxLayout()
        samples_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for label, fname in (
            ("Exemplu medical", "medical_patient_sample.xml"),
            ("Exemplu charts", "feed_sample.xml"),
        ):
            b = QPushButton(label)
            b.setObjectName("GhostButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, f=fname: self._load_sample(f))
            samples_row.addWidget(b)

        exts = ", ".join(list_supported_extensions())
        fmt_label = QLabel(f"Formate: {exts}")
        fmt_label.setObjectName("EmptyHint")
        fmt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(16)
        layout.addWidget(btn_open, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(8)
        layout.addLayout(samples_row)
        layout.addSpacing(8)
        layout.addWidget(fmt_label)
        layout.addStretch(2)
        return page

    def _build_workspace(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        layout.addWidget(self._build_toolbar())
        layout.addWidget(self._build_file_banner())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_configure_panel())
        splitter.addWidget(self._build_preview_panel())
        splitter.setSizes([680, 480])
        splitter.setHandleWidth(6)
        layout.addWidget(splitter, stretch=1)

        layout.addWidget(self._build_action_bar())
        return page

    def _build_toolbar(self) -> QToolBar:
        bar = QToolBar()
        bar.setMovable(False)
        bar.setFloatable(False)

        open_btn = QToolButton()
        open_btn.setText("Deschide")
        open_btn.clicked.connect(self._open_file)
        bar.addWidget(open_btn)

        bar.addSeparator()

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Caută câmp după nume…")
        self._filter.setMinimumWidth(220)
        self._filter.textChanged.connect(self._apply_filter)
        bar.addWidget(self._filter)

        bar.addSeparator()

        for label, slot, tip in (
            ("Toate", self._select_all, "Bifează toate câmpurile vizibile"),
            ("Niciunul", self._select_none, "Debifează tot"),
        ):
            b = QToolButton()
            b.setText(label)
            b.setToolTip(tip)
            b.clicked.connect(slot)
            bar.addWidget(b)

        spacer = QWidget()
        spacer.setMinimumWidth(8)
        bar.addWidget(spacer)
        return bar

    def _build_file_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("FileBanner")
        row = QHBoxLayout(banner)
        row.setContentsMargins(16, 12, 16, 12)

        info = QVBoxLayout()
        self._file_title = QLabel("—")
        self._file_title.setObjectName("FileBannerTitle")
        self._file_meta = QLabel("Încărcați un fișier")
        self._file_meta.setObjectName("FileBannerMeta")
        info.addWidget(self._file_title)
        info.addWidget(self._file_meta)
        row.addLayout(info, stretch=1)

        self._selection_badge = QLabel("0 selectate")
        self._selection_badge.setObjectName("StatBadge")
        self._selection_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self._selection_badge)
        return banner

    def _build_configure_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("1. Configurare câmpuri")
        title.setObjectName("PanelTitle")
        hint = QLabel(
            "Bifați ce anonimizați și alegeți metoda. Metoda se activează doar pentru rândurile bifate.",
        )
        hint.setObjectName("PanelHint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(
            ["", "Câmp", "Exemple din date", "Metodă"],
        )
        header = self._table.horizontalHeader()
        header.setMinimumSectionSize(72)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 52)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self._table.setColumnWidth(1, 200)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(3, 200)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(44)
        self._table.setMinimumHeight(280)
        layout.addWidget(self._table, stretch=1)

        salt_row = QHBoxLayout()
        salt_lbl = QLabel("Salt")
        salt_lbl.setToolTip("Necesar pentru pseudonym / hash — păstrați secret, separat de fișier")
        self._salt = QLineEdit()
        self._salt.setEchoMode(QLineEdit.EchoMode.Password)
        self._salt.setPlaceholderText("Opțional — pentru pseudonym și hash")
        salt_row.addWidget(salt_lbl)
        salt_row.addWidget(self._salt, stretch=1)
        layout.addLayout(salt_row)
        return panel

    def _build_preview_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("2. Previzualizare")
        title.setObjectName("PanelTitle")
        self._preview_stats = QLabel("Rulați previzualizarea pentru a vedea rezultatul")
        self._preview_stats.setObjectName("PanelHint")
        layout.addWidget(title)
        layout.addWidget(self._preview_stats)

        self._preview = QTextEdit()
        self._preview.setObjectName("PreviewPane")
        self._preview.setReadOnly(True)
        preview_palette = self._preview.palette()
        preview_palette.setColor(QPalette.ColorRole.Text, QColor("#e2e8f0"))
        preview_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#94a3b8"))
        preview_palette.setColor(QPalette.ColorRole.Base, QColor("#0f172a"))
        self._preview.setPalette(preview_palette)
        self._preview.setPlaceholderText(
            "Conținutul fișierului apare aici după încărcare.\n\n"
            "Bifați câmpuri și apăsați «Previzualizare» (Ctrl+P) pentru anonimizare.",
        )
        layout.addWidget(self._preview, stretch=1)
        return panel

    def _build_action_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet("background: transparent;")
        row = QHBoxLayout(bar)
        row.setContentsMargins(4, 0, 4, 0)

        note = QLabel("Exportul creează un fișier nou; sursa nu este suprascrisă.")
        note.setObjectName("PanelHint")
        row.addWidget(note)
        row.addStretch()

        self._btn_preview = QPushButton("Previzualizare")
        self._btn_preview.setObjectName("SecondaryButton")
        self._btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_preview.clicked.connect(self._run_preview)

        self._btn_export = QPushButton("Exportă fișier anonimizat")
        self._btn_export.setObjectName("SecondaryButton")
        self._btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_export.clicked.connect(self._export_file)
        self._btn_export.setVisible(False)

        row.addWidget(self._btn_preview)
        row.addWidget(self._btn_export)
        return bar

    def _set_workspace_enabled(self, enabled: bool) -> None:
        if self._filter:
            self._filter.setEnabled(enabled)
        if self._table:
            self._table.setEnabled(enabled)
        if self._salt:
            self._salt.setEnabled(enabled)
        if self._btn_preview:
            self._btn_preview.setEnabled(enabled)
        if not enabled:
            self._invalidate_preview()

    def _can_export(self) -> bool:
        return (
            self._preview_ready
            and self._session.adapter is not None
            and any(r.enabled for r in self._rows)
        )

    def _update_export_availability(self) -> None:
        show = (
            self._can_export()
            and self._stack is not None
            and self._stack.currentIndex() == 1
        )
        if self._btn_export:
            self._btn_export.setVisible(show)
            self._btn_export.setEnabled(show)
        if self._export_act:
            self._export_act.setEnabled(show)

    def _invalidate_preview(self) -> None:
        was_preview_ready = self._preview_ready
        self._preview_ready = False
        if was_preview_ready and self._session.adapter is not None:
            try:
                self._session.discard_preview()
                self._show_source_in_preview()
            except Exception:  # noqa: BLE001
                pass
        self._update_export_availability()

    def _show_source_in_preview(self) -> None:
        if self._session.adapter is None:
            return
        try:
            text = self._session.document_text()
        except Exception:  # noqa: BLE001
            return
        if self._preview:
            self._preview.setPlainText(text[:500_000])
        if self._preview_stats:
            char_note = f"{len(text):,} caractere"
            if len(text) > 500_000:
                char_note += " (afișare trunchiată)"
            self._preview_stats.setText(
                f"Original — {char_note}. Bifați câmpuri, apoi «Previzualizare».",
            )

    def _show_idle(self) -> None:
        if self._stack:
            self._stack.setCurrentIndex(0)
        self._status.showMessage("Gata — încărcați un fișier sau deschideți un exemplu.")

    def _show_workspace(self) -> None:
        if self._stack:
            self._stack.setCurrentIndex(1)
        self._set_workspace_enabled(True)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "Data Anonymizer",
            "<b>Data Anonymizer</b><br><br>"
            "Instrument modular pentru anonimizare date.<br>"
            "Adaptere pentru formate multiple (XML în v1).<br><br>"
            "© Zenaios",
        )

    def _open_file(self) -> None:
        exts = " ".join(f"*{e}" for e in list_supported_extensions())
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Deschide fișier",
            str(SAMPLES_DIR),
            f"Fișiere suportate ({exts});;Toate (*.*)",
        )
        if path:
            self._load_path(Path(path))

    def _load_sample(self, filename: str) -> None:
        path = SAMPLES_DIR / filename
        if path.is_file():
            self._load_path(path)
        else:
            QMessageBox.warning(self, "Exemplu indisponibil", f"Fișierul nu există:\n{path}")

    def _load_path(self, path: Path) -> None:
        try:
            fmt = self._session.load(path)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Eroare la încărcare", str(exc))
            return

        self._preview_count = 0
        self._preview_ready = False

        fields = self._session.fields()
        if self._file_title:
            self._file_title.setText(path.name)
        if self._file_meta:
            self._file_meta.setText(
                f"Format {fmt.upper()}  ·  {len(fields)} câmpuri  ·  {path.parent}",
            )
        if self._filter:
            self._filter.blockSignals(True)
            self._filter.clear()
            self._filter.blockSignals(False)
        self._show_workspace()
        self._populate_table(fields)
        self._show_source_in_preview()
        self._update_export_availability()
        self._status.showMessage(f"Încărcat: {path.name} — selectați câmpurile de anonimizat")

    def _populate_table(self, fields: dict) -> None:
        assert self._table is not None
        self._rows.clear()
        self._table.blockSignals(True)
        self._table.setRowCount(len(fields))

        for row, (fid, info) in enumerate(sorted(fields.items())):
            enabled = False
            method = "redact"
            self._rows.append(_RowState(field_id=fid, enabled=enabled, method=method))

            chk = QCheckBox()
            chk.setObjectName("FieldCheck")
            chk.setChecked(enabled)
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            chk.stateChanged.connect(lambda _s, r=row: self._on_check_changed(r))
            chk_wrap = QWidget()
            chk_wrap.setStyleSheet("background: transparent;")
            chk_layout = QHBoxLayout(chk_wrap)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setCellWidget(row, 0, chk_wrap)

            name_item = QTableWidgetItem(fid)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setForeground(QColor("#f8fafc"))
            font = name_item.font()
            font.setWeight(QFont.Weight.DemiBold)
            name_item.setFont(font)
            self._table.setItem(row, 1, name_item)

            samples = " · ".join(
                repr(v) if len(v) <= 36 else repr(v[:33] + "…")
                for v in info.sample_values[:3]
            ) or "—"
            sample_item = QTableWidgetItem(samples)
            sample_item.setFlags(sample_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            sample_item.setForeground(QColor("#94a3b8"))
            self._table.setItem(row, 2, sample_item)

            combo = QComboBox()
            combo.setObjectName("MethodCombo")
            for key, label in method_select_options().items():
                combo.addItem(label, key)
                idx = combo.count() - 1
                combo.setItemData(idx, select_tooltip(key), Qt.ItemDataRole.ToolTipRole)
            combo.setToolTip("Metodă de anonimizare pentru acest câmp")
            idx = combo.findData(method)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.setEnabled(enabled)
            combo.currentIndexChanged.connect(lambda _i, r=row: self._on_method_changed(r))
            self._table.setCellWidget(row, 3, combo)

        self._table.blockSignals(False)
        self._table.resizeColumnToContents(1)
        if self._table.columnWidth(1) < 160:
            self._table.setColumnWidth(1, 200)
        self._apply_filter()

    def _method_combo(self, row: int) -> QComboBox:
        w = self._table.cellWidget(row, 3)  # type: ignore[union-attr]
        assert isinstance(w, QComboBox)
        return w

    def _checkbox(self, row: int) -> QCheckBox:
        wrap = self._table.cellWidget(row, 0)  # type: ignore[union-attr]
        chk = wrap.findChild(QCheckBox, "FieldCheck")
        assert chk is not None
        return chk

    def _on_check_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._rows):
            return
        enabled = self._checkbox(row).isChecked()
        self._rows[row].enabled = enabled
        self._method_combo(row).setEnabled(enabled)
        self._invalidate_preview()
        self._update_selection_status()

    def _on_method_changed(self, row: int) -> None:
        combo = self._method_combo(row)
        self._rows[row].method = combo.currentData() or "redact"
        self._invalidate_preview()

    def _apply_filter(self) -> None:
        if not self._filter or not self._table:
            return
        q = self._filter.text().strip().lower()
        for row in range(self._table.rowCount()):
            fid = self._rows[row].field_id
            self._table.setRowHidden(row, bool(q) and q not in fid.lower())
        self._update_selection_status()

    def _update_selection_status(self) -> None:
        total_selected = sum(1 for r in self._rows if r.enabled)
        visible_selected = 0
        visible_total = 0
        if self._table:
            for row in range(len(self._rows)):
                if self._table.isRowHidden(row):
                    continue
                visible_total += 1
                if self._rows[row].enabled:
                    visible_selected += 1

        if self._selection_badge:
            self._selection_badge.setText(f"{total_selected} câmpuri selectate")
        self._status.showMessage(
            f"{visible_selected} vizibile selectate din {visible_total} afișate "
            f"({total_selected} total)",
        )

    def _select_all(self) -> None:
        if not self._table:
            return
        for row in range(len(self._rows)):
            if not self._table.isRowHidden(row):
                self._checkbox(row).setChecked(True)

    def _select_none(self) -> None:
        if not self._table:
            return
        for row in range(len(self._rows)):
            if not self._table.isRowHidden(row):
                self._checkbox(row).setChecked(False)

    def _build_rules(self) -> list[FieldRule]:
        return [
            FieldRule(
                field_id=state.field_id,
                method=state.method,
                options=method_options_for(state.method),
            )
            for state in self._rows
            if state.enabled
        ]

    def _run_preview(self) -> None:
        if self._session.adapter is None:
            QMessageBox.warning(self, "Atenție", "Încărcați mai întâi un fișier.")
            return
        rules = self._build_rules()
        if not rules:
            QMessageBox.warning(
                self,
                "Niciun câmp selectat",
                "Bifați cel puțin un câmp în tabel înainte de previzualizare.",
            )
            return
        self._status.showMessage("Se generează previzualizarea…")
        self.repaint()
        try:
            count, text = self._session.preview(rules, salt=self._salt.text().strip())  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Eroare previzualizare", str(exc))
            return

        self._preview_count = count
        if self._preview:
            self._preview.setPlainText(text[:500_000])
        if self._preview_stats:
            self._preview_stats.setText(
                f"✓ {count} valori anonimizate — puteți exporta fișierul nou",
            )
        self._preview_ready = True
        self._update_export_availability()
        self._status.showMessage(f"Previzualizare gata: {count} valori modificate")

    def _export_file(self) -> None:
        if self._session.adapter is None:
            QMessageBox.warning(self, "Atenție", "Încărcați mai întâi un fișier.")
            return
        if not self._can_export():
            QMessageBox.information(
                self,
                "Export indisponibil",
                "Bifați cel puțin un câmp, rulați «Previzualizare», "
                "apoi exportați fișierul anonimizat.",
            )
            return
        rules = self._build_rules()
        if not rules:
            QMessageBox.warning(self, "Niciun câmp selectat", "Selectați cel puțin un câmp.")
            return

        src = self._session.source_path
        default_path = default_export_path(src)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportă fișier anonimizat",
            str(default_path),
            "Toate (*.*)",
        )
        if not path:
            return
        self._status.showMessage("Se exportă…")
        self.repaint()
        try:
            count = self._session.export(path, rules, salt=self._salt.text().strip())  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Eroare export", str(exc))
            return

        QMessageBox.information(
            self,
            "Export reușit",
            f"<b>Fișier salvat</b><br>{path}<br><br>"
            f"{count} valori anonimizate.<br>"
            f"Fișierul original nu a fost modificat.",
        )
        self._status.showMessage(f"Export reușat: {path}")

