"""Reusable interactive widgets for the engineering GUI."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "YES" if value else "NO"
    if isinstance(value, float):
        if abs(value) >= 1e4 or (abs(value) > 0 and abs(value) < 1e-3):
            return f"{value:.6e}"
        return f"{value:.6g}"
    if isinstance(value, (list, tuple)):
        if not value:
            return "(none)"
        return ", ".join(_fmt(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, indent=2)
    return str(value)


def _copy_text(text: str) -> None:
    cb = QGuiApplication.clipboard()
    if cb is not None:
        cb.setText(text, QClipboard.Mode.Clipboard)


class MetricTile(QFrame):
    """Large numeric stat — double-click copies value."""

    def __init__(
        self,
        label: str,
        value: str,
        *,
        status: str = "neutral",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MetricTile")
        self.setProperty("status", status)
        self._copy_value = value
        self.setToolTip("Double-click to copy value")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        title = QLabel(label)
        title.setObjectName("MetricLabel")
        val = QLabel(value)
        val.setObjectName("MetricValue")
        layout.addWidget(title)
        layout.addWidget(val)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        _copy_text(self._copy_value)
        super().mouseDoubleClickEvent(event)


class StatusChip(QLabel):
    """Small pass/fail badge."""

    def __init__(self, ok: bool, label: str, parent: QWidget | None = None) -> None:
        super().__init__(label, parent)
        self.setObjectName("StatusChip")
        self.setProperty("ok", ok)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        tip = "Pass" if ok else "Fail — see Diagnosis tab"
        self.setToolTip(tip)


class MarginBar(QWidget):
    """Horizontal margin indicator with color zones."""

    def __init__(
        self,
        label: str,
        fraction: float,
        *,
        unit: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        header = QHBoxLayout()
        header.addWidget(QLabel(label))
        header.addStretch(1)
        val_lbl = QLabel(f"{fraction:.1%}{unit}")
        header.addWidget(val_lbl)
        layout.addLayout(header)
        bar = QProgressBar()
        bar.setRange(0, 100)
        pct = max(0, min(100, int(fraction * 100)))
        bar.setValue(pct)
        bar.setTextVisible(False)
        if fraction >= 0.15:
            bar.setObjectName("MarginBarGood")
        elif fraction >= 0.0:
            bar.setObjectName("MarginBarWarn")
        else:
            bar.setObjectName("MarginBarBad")
        layout.addWidget(bar)


class SectionCard(QFrame):
    """Titled card container."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SectionCard")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 12, 14, 12)
        heading = QLabel(title)
        heading.setObjectName("SectionTitle")
        self._layout.addWidget(heading)

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)


class CollapsibleGroup(QGroupBox):
    """Checkable group box — hide contents when collapsed."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True)
        self._layout = QVBoxLayout(self)
        self.toggled.connect(self._on_toggle)

    def _on_toggle(self, expanded: bool) -> None:
        for i in range(self._layout.count()):
            item = self._layout.itemAt(i)
            if item is None:
                continue
            w = item.widget()
            if w:
                w.setVisible(expanded)
            lay = item.layout()
            if lay:
                for j in range(lay.count()):
                    sub = lay.itemAt(j)
                    if sub and sub.widget():
                        sub.widget().setVisible(expanded)

    def add_layout(self, layout) -> None:
        self._layout.addLayout(layout)

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)


def _wire_copy_on_double_click(table: QTableWidget) -> None:
    def _on_dbl(row: int, col: int) -> None:
        item = table.item(row, col)
        if item:
            _copy_text(item.text())

    table.cellDoubleClicked.connect(_on_dbl)
    table.setToolTip("Double-click any cell to copy")


def searchable_table(
    rows: list[tuple[str, Any]],
    *,
    placeholder: str = "Filter fields…",
) -> QWidget:
    """Key/value table with live search filter."""
    wrap = QWidget()
    layout = QVBoxLayout(wrap)
    layout.setContentsMargins(0, 0, 0, 0)
    search = QLineEdit()
    search.setPlaceholderText(placeholder)
    search.setObjectName("SearchBox")
    layout.addWidget(search)

    table = QTableWidget(len(rows), 2)
    table.setHorizontalHeaderLabels(["Field", "Value"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.setObjectName("KeyValueTable")
    table.setSortingEnabled(True)
    for i, (key, val) in enumerate(rows):
        table.setItem(i, 0, QTableWidgetItem(str(key)))
        table.setItem(i, 1, QTableWidgetItem(_fmt(val)))
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)
    _wire_copy_on_double_click(table)
    layout.addWidget(table)

    def _filter(text: str) -> None:
        needle = text.lower()
        for r in range(table.rowCount()):
            k = table.item(r, 0)
            v = table.item(r, 1)
            show = not needle or (
                (k and needle in k.text().lower()) or (v and needle in v.text().lower())
            )
            table.setRowHidden(r, not show)

    search.textChanged.connect(_filter)
    return wrap


def data_table(
    headers: list[str],
    rows: list[list[Any]],
    *,
    placeholder: str = "Filter rows…",
) -> QWidget:
    """Multi-column sortable table with search."""
    wrap = QWidget()
    layout = QVBoxLayout(wrap)
    layout.setContentsMargins(0, 0, 0, 0)
    search = QLineEdit()
    search.setPlaceholderText(placeholder)
    search.setObjectName("SearchBox")
    layout.addWidget(search)

    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            item = QTableWidgetItem(_fmt(val))
            if isinstance(val, (int, float)):
                item.setData(Qt.ItemDataRole.UserRole, float(val))
            table.setItem(r, c, item)
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)
    _wire_copy_on_double_click(table)
    layout.addWidget(table)

    def _filter(text: str) -> None:
        needle = text.lower()
        for r in range(table.rowCount()):
            parts = []
            for c in range(table.columnCount()):
                it = table.item(r, c)
                if it:
                    parts.append(it.text().lower())
            table.setRowHidden(r, bool(needle) and needle not in " ".join(parts))

    search.textChanged.connect(_filter)
    return wrap


def key_value_table(rows: list[tuple[str, Any]]) -> QTableWidget:
    """Plain key/value table (no search wrapper)."""
    table = QTableWidget(len(rows), 2)
    table.setHorizontalHeaderLabels(["Field", "Value"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.setObjectName("KeyValueTable")
    table.setSortingEnabled(True)
    for i, (key, val) in enumerate(rows):
        table.setItem(i, 0, QTableWidgetItem(str(key)))
        table.setItem(i, 1, QTableWidgetItem(_fmt(val)))
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)
    _wire_copy_on_double_click(table)
    return table


def dict_to_rows(data: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    for k, v in data.items():
        key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
        if isinstance(v, dict):
            rows.extend(dict_to_rows(v, key))
        else:
            rows.append((key, v))
    return rows


def scroll_wrap(widget: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidget(widget)
    return scroll


def overview_metrics(payload: dict[str, Any]) -> QWidget:
    w = QWidget()
    grid = QGridLayout(w)
    cr = payload["control_requirement"]
    aero = payload["aero"]
    hv = payload["hydro_validation"]
    geom = payload["geometry"]
    st = payload["structure"]["aggressive"]
    servo = payload["servo"]
    tiles = [
        ("M_design", f"{cr['M_design']:.4f} N·m", "neutral"),
        ("Span", f"{geom['span_mm']:.2f} mm", "neutral"),
        ("CL / α", f"{aero['CL']:.4f} / {aero['alpha_deg']:.2f}°", "neutral"),
        ("Servo util", f"{servo['utilization']:.1%}", "good" if servo["utilization"] < 0.8 else "warn"),
        ("Lift margin", f"{hv['lift_margin']:.1%}", "good" if hv["lift_ok"] else "bad"),
        ("FoS (agg)", f"{st['fos_yield']:.1f}", "good" if st["fos_ok"] else "bad"),
        ("Stall margin", f"{hv['stall_margin_deg']:.2f}°", "good" if hv["stall_ok"] else "warn"),
        ("L/D", f"{hv['lift_to_drag']:.2f}", "neutral"),
    ]
    for i, (label, val, status) in enumerate(tiles):
        grid.addWidget(MetricTile(label, val, status=status), i // 4, i % 4)
    return w
