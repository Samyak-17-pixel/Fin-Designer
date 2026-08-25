"""Dedicated fin dimensions dashboard — all sizes in one scannable view."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from auv_fin_design.ui.gui.widgets.common import MetricTile, SectionCard, _copy_text


def _dim_row(label: str, m_val: float, mm_val: float) -> tuple[str, str]:
    return (label, f"{m_val:.6f} m  ·  {mm_val:.2f} mm")


def fin_dimensions_summary_text(geom: dict[str, Any], airfoil: str) -> str:
    """Plain-text block for clipboard / export."""
    frame = geom.get("control_surface_frame") or {}
    lines = [
        "FIN DIMENSIONS SUMMARY",
        f"Airfoil: NACA{geom.get('naca_profile', '?')}  ({airfoil})",
        "",
        "--- Primary (mm) ---",
        f"Span:           {geom['span_mm']:.2f} mm",
        f"Root chord:     {geom['root_chord_mm']:.2f} mm",
        f"Tip chord:      {geom['tip_chord_mm']:.2f} mm",
        f"MAC:            {geom['mac_mm']:.2f} mm",
        "",
        "--- Planform ---",
        f"Surface area:   {geom['surface_area_m2']:.6f} m²  ({geom['surface_area_mm2']:.1f} mm²)",
        f"Aspect ratio:   {geom['aspect_ratio']:.4f}",
        f"Taper ratio:    {geom['taper_ratio']:.4f}",
        f"Sweep:          {geom['sweep_deg']:.2f}°",
        "",
        "--- Section ---",
        f"Thickness t/c:  {geom['thickness_ratio']:.4f}",
        f"Root thickness: {geom['root_thickness_mm']:.2f} mm",
        f"Tip thickness:  {geom['tip_thickness_mm']:.2f} mm",
        f"Shaft width:    {geom['shaft_diameter_mm']:.2f} mm  (max airfoil width at root)",
        "",
        "--- Mass estimate ---",
        f"Volume:         {geom['volume_est_m3']:.6e} m³",
        f"Mass:           {geom['mass_est_kg']:.6f} kg",
    ]
    if frame.get("note"):
        lines += ["", "--- Frame ---", frame["note"]]
    for key, title in (
        ("leading_edge_root", "LE root"),
        ("trailing_edge_root", "TE root"),
        ("leading_edge_tip", "LE tip"),
        ("trailing_edge_tip", "TE tip"),
    ):
        pt = frame.get(key)
        if pt:
            lines.append(
                f"{title}:  X = {pt['x_mm']:.2f} mm,  Z = {pt['z_mm']:.2f} mm"
            )
    return "\n".join(lines)


def build_fin_dimensions_panel(geom: dict[str, Any], airfoil: str) -> QWidget:
    """All fin dimensions grouped on one page."""
    root = QWidget()
    layout = QVBoxLayout(root)
    layout.setSpacing(12)

    header = QHBoxLayout()
    title = QLabel(f"NACA {geom.get('naca_profile', '—')}  ·  {airfoil}")
    title.setObjectName("SectionTitle")
    font = title.font()
    font.setPointSize(16)
    title.setFont(font)
    header.addWidget(title)
    header.addStretch(1)
    copy_btn = QPushButton("Copy all dimensions")
    copy_btn.setObjectName("PrimaryButton")
    copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    copy_btn.clicked.connect(
        lambda: _copy_text(fin_dimensions_summary_text(geom, airfoil))
    )
    header.addWidget(copy_btn)
    layout.addLayout(header)

    # Hero metrics — the numbers you build from
    hero = QWidget()
    hero_grid = QGridLayout(hero)
    hero_grid.setSpacing(10)
    heroes = [
        ("Span", f"{geom['span_mm']:.2f} mm", f"{geom['span_m']:.6f} m"),
        ("Root chord", f"{geom['root_chord_mm']:.2f} mm", f"{geom['root_chord_m']:.6f} m"),
        ("Tip chord", f"{geom['tip_chord_mm']:.2f} mm", f"{geom['tip_chord_m']:.6f} m"),
        ("MAC", f"{geom['mac_mm']:.2f} mm", f"{geom['mac_m']:.6f} m"),
    ]
    for i, (label, mm_s, m_s) in enumerate(heroes):
        hero_grid.addWidget(MetricTile(label, mm_s, status="neutral"), 0, i)
    layout.addWidget(hero)

    # Two-column cards
    row = QHBoxLayout()
    planform = SectionCard("Planform")
    for name, val in (
        _dim_row("Span", geom["span_m"], geom["span_mm"]),
        _dim_row("Root chord", geom["root_chord_m"], geom["root_chord_mm"]),
        _dim_row("Tip chord", geom["tip_chord_m"], geom["tip_chord_mm"]),
        _dim_row("MAC", geom["mac_m"], geom["mac_mm"]),
        ("Surface area", f"{geom['surface_area_m2']:.6f} m²  ·  {geom['surface_area_mm2']:.1f} mm²"),
        ("Aspect ratio", f"{geom['aspect_ratio']:.4f}"),
        ("Taper ratio", f"{geom['taper_ratio']:.4f}"),
        ("Sweep", f"{geom['sweep_deg']:.2f}°"),
    ):
        lbl_w = QLabel(f"{name}:  {val}")
        lbl_w.setWordWrap(True)
        lbl_w.setObjectName("DimLine")
        planform.add_widget(lbl_w)
    row.addWidget(planform)

    section = SectionCard("Section & shaft")
    for name, val in (
        ("Thickness ratio (t/c)", f"{geom['thickness_ratio']:.4f}"),
        _dim_row("Root max thickness", geom["root_thickness_m"], geom["root_thickness_mm"]),
        _dim_row("Tip max thickness", geom["tip_thickness_m"], geom["tip_thickness_mm"]),
        _dim_row("Shaft / max root width", geom["shaft_diameter_m"], geom["shaft_diameter_mm"]),
        ("Est. volume", f"{geom['volume_est_m3']:.6e} m³"),
        ("Est. mass", f"{geom['mass_est_kg']:.6f} kg"),
    ):
        lbl_w = QLabel(f"{name}:  {val}")
        lbl_w.setWordWrap(True)
        lbl_w.setObjectName("DimLine")
        section.add_widget(lbl_w)
    row.addWidget(section)
    layout.addLayout(row)

    # Corner coordinates table
    frame = geom.get("control_surface_frame") or {}
    corners = SectionCard("Corner coordinates (hinge frame — origin at root hinge, 25% chord)")
    if frame.get("note"):
        note = QLabel(frame["note"])
        note.setWordWrap(True)
        note.setObjectName("StatusLine")
        corners.add_widget(note)

    table = QTableWidget(0, 4)
    table.setHorizontalHeaderLabels(["Corner", "X [m]", "X [mm]", "Z [mm]"])
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    labels = {
        "leading_edge_root": "Leading edge · root",
        "trailing_edge_root": "Trailing edge · root",
        "leading_edge_tip": "Leading edge · tip",
        "trailing_edge_tip": "Trailing edge · tip",
    }
    row_i = 0
    for key, title in labels.items():
        pt = frame.get(key)
        if not pt:
            continue
        table.insertRow(row_i)
        table.setItem(row_i, 0, QTableWidgetItem(title))
        table.setItem(row_i, 1, QTableWidgetItem(f"{pt['x_m']:.6f}"))
        table.setItem(row_i, 2, QTableWidgetItem(f"{pt['x_mm']:.2f}"))
        table.setItem(row_i, 3, QTableWidgetItem(f"{pt['z_mm']:.2f}"))
        row_i += 1
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)

    def _copy_cell(r: int, c: int) -> None:
        item = table.item(r, c)
        if item:
            _copy_text(item.text())

    table.cellDoubleClicked.connect(_copy_cell)
    table.setToolTip("Double-click a cell to copy")
    corners.add_widget(table)
    layout.addWidget(corners)

    # Build sheet (mm only)
    mm_text = (
        f"span = {geom['span_mm']:.2f} mm\n"
        f"root chord = {geom['root_chord_mm']:.2f} mm\n"
        f"tip chord = {geom['tip_chord_mm']:.2f} mm\n"
        f"MAC = {geom['mac_mm']:.2f} mm\n"
        f"root thickness = {geom['root_thickness_mm']:.2f} mm\n"
        f"tip thickness = {geom['tip_thickness_mm']:.2f} mm\n"
        f"shaft OD ≤ {geom['shaft_diameter_mm']:.2f} mm (airfoil width at root)"
    )
    build_sheet = SectionCard("Build sheet (mm only — select or copy)")
    mono = QFont("monospace")
    mono.setStyleHint(QFont.StyleHint.Monospace)
    mm_lbl = QLabel(mm_text)
    mm_lbl.setFont(mono)
    mm_lbl.setObjectName("BuildSheet")
    mm_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    mm_lbl.setCursor(Qt.CursorShape.IBeamCursor)
    build_sheet.add_widget(mm_lbl)
    copy_mm = QPushButton("Copy mm summary")
    copy_mm.clicked.connect(lambda: _copy_text(mm_text))
    build_sheet.add_widget(copy_mm)
    layout.addWidget(build_sheet)

    hint = QLabel("All dimensions from auto-sized fin geometry. Hinge fixed at 25% chord.")
    hint.setObjectName("StatusLine")
    layout.addWidget(hint)
    layout.addStretch(1)
    return root
