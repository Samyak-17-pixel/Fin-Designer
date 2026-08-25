"""Navigable results panel — sidebar + searchable tables, no external viz libs."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from auv_fin_design.ui.gui.viewmodels.design_result_vm import DesignResultView
from auv_fin_design.ui.gui.widgets.fin_dimensions_panel import build_fin_dimensions_panel
from auv_fin_design.ui.gui.widgets.common import (
    MarginBar,
    MetricTile,
    SectionCard,
    StatusChip,
    data_table,
    dict_to_rows,
    overview_metrics,
    scroll_wrap,
    searchable_table,
)


class ResultsPanel(QWidget):
    """Sidebar navigation + stacked sections with search and copy."""

    _SECTIONS = (
        "Overview",
        "Diagnosis",
        "Geometry",
        "Hydrodynamics",
        "Control",
        "Aero & CoP",
        "Strips",
        "Structure",
        "Servo & Shaft",
        "Validation",
        "Manufacturing",
        "Sensitivity",
        "Optimization",
        "Trace",
        "Exports",
        "Raw JSON",
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._exports_layout: QVBoxLayout | None = None
        self._exports_tab: QWidget | None = None
        self._global_search = QLineEdit()
        self._global_search.setPlaceholderText("Jump to section…")
        self._global_search.setObjectName("SearchBox")

        root = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel("Results"))
        self._nav = QListWidget()
        self._nav.setObjectName("SectionNav")
        self._nav.setMaximumWidth(200)
        left.addWidget(self._global_search)
        left.addWidget(self._nav, stretch=1)
        root.addLayout(left)

        self._stack = QStackedWidget()
        self._stack.setObjectName("ResultsStack")
        root.addWidget(self._stack, stretch=1)

        self._global_search.textChanged.connect(self._filter_nav)

    def _filter_nav(self, text: str) -> None:
        needle = text.lower()
        for i in range(self._nav.count()):
            item = self._nav.item(i)
            if item:
                item.setHidden(bool(needle) and needle not in item.text().lower())

    def _add_section(self, name: str, widget: QWidget, *, badge: str = "") -> None:
        item = QListWidgetItem(name)
        if badge:
            item.setText(f"{name}  {badge}")
        item.setData(Qt.ItemDataRole.UserRole, name)
        self._nav.addItem(item)
        self._stack.addWidget(scroll_wrap(widget) if not isinstance(widget, QTextEdit) else widget)

    def show_result(self, view: DesignResultView) -> None:
        self._nav.clear()
        while self._stack.count():
            w = self._stack.widget(0)
            self._stack.removeWidget(w)
            if w:
                w.deleteLater()

        p = view.payload
        diag = p["diagnosis"]
        passed = view.passed

        # Overview
        ov = QWidget()
        ov_l = QVBoxLayout(ov)
        banner = QLabel(
            "DESIGN PASSED" if passed else f"DESIGN FAILED — {view.failure_count} violation(s)"
        )
        banner.setObjectName("StatusBanner")
        banner.setProperty("passed", passed)
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ov_l.addWidget(banner)
        chips = QHBoxLayout()
        hv = p["hydro_validation"]
        for ok, lbl in (
            (passed, "Design"),
            (hv["overall_ok"], "Hydro"),
            (hv["stall_ok"], "Stall"),
            (p["shaft_fit"]["fits"], "Shaft"),
            (p["servo"]["continuous_ok"], "Servo"),
            (p["manufacturing"]["printable"], "Print"),
        ):
            chips.addWidget(StatusChip(ok, lbl))
        chips.addStretch(1)
        ov_l.addLayout(chips)
        ov_l.addWidget(overview_metrics(p))
        ov_l.addWidget(MarginBar("Lift margin", max(0, hv["lift_margin"])))
        ov_l.addWidget(MarginBar("Authority margin", max(0, hv["authority_margin"])))
        ov_l.addWidget(
            MarginBar("Stall margin", hv["stall_margin_deg"] / 20.0, unit=f" ({hv['stall_margin_deg']:.1f}°)")
        )
        ov_l.addWidget(MarginBar("Servo utilization", p["servo"]["utilization"]))
        hint = QLabel("Double-click any metric tile to copy its value.")
        hint.setObjectName("StatusLine")
        ov_l.addWidget(hint)
        ov_l.addStretch(1)
        badge = "" if passed else "●"
        self._add_section("Overview", ov, badge=badge)

        # Fin Dimensions — all sizes in one place
        self._add_section(
            "Fin Dimensions",
            build_fin_dimensions_panel(p["geometry"], p["airfoil"]),
        )

        # Diagnosis — interactive tree
        diag_w = QWidget()
        diag_l = QVBoxLayout(diag_w)
        tree = QTreeWidget()
        tree.setHeaderLabels(["Issue", "Detail"])
        tree.setAlternatingRowColors(True)
        tree.setObjectName("DiagnosisTree")
        if diag.get("violations"):
            for v in diag["violations"]:
                parent = QTreeWidgetItem([v["category"], v["message"]])
                parent.setExpanded(True)
                for c in v.get("corrections", []):
                    child = QTreeWidgetItem(["Fix", c])
                    parent.addChild(child)
                tree.addTopLevelItem(parent)
        else:
            tree.addTopLevelItem(QTreeWidgetItem(["OK", "All checks passed"]))
        tree.resizeColumnToContents(0)
        diag_l.addWidget(tree)
        if diag.get("all_corrections"):
            corr = SectionCard("Quick fixes (deduplicated)")
            for c in diag["all_corrections"]:
                btn = QPushButton(c)
                btn.setObjectName("CorrectionButton")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _=False, t=c: self._jump_to_inputs_hint(t))
                corr.add_widget(btn)
            diag_l.addWidget(corr)
        self._add_section("Diagnosis", diag_w, badge="●" if not passed else "")

        # Geometry
        geom = p["geometry"]
        geom_rows = dict_to_rows({k: v for k, v in geom.items() if k != "control_surface_frame"})
        frame = geom.get("control_surface_frame") or {}
        for corner in (
            "leading_edge_root",
            "trailing_edge_root",
            "leading_edge_tip",
            "trailing_edge_tip",
        ):
            pt = frame.get(corner)
            if pt:
                geom_rows.append((corner, f"X={pt['x_mm']:.2f} mm, Z={pt['z_mm']:.2f} mm"))
        self._add_section("Geometry", searchable_table(geom_rows))

        self._add_section(
            "Hydrodynamics",
            searchable_table(dict_to_rows(p["hydrodynamics"]), placeholder="Filter hydro…"),
        )

        ctrl_rows = dict_to_rows(p["control_requirement"], "control")
        ctrl_rows.extend(dict_to_rows(p["allocation"], "allocation"))
        self._add_section("Control", searchable_table(ctrl_rows, placeholder="Filter control…"))

        # Aero summary (no strips)
        aero_cop = QWidget()
        ac_l = QVBoxLayout(aero_cop)
        ac_l.addWidget(searchable_table(dict_to_rows(p["aero"]), placeholder="Filter aero…"))
        cp = p["center_of_pressure"]
        cp_rows = {k: v for k, v in cp.items() if k != "strips"}
        ac_l.addWidget(searchable_table(dict_to_rows(cp_rows), placeholder="Filter CoP…"))
        self._add_section("Aero & CoP", aero_cop)

        # Strips — dedicated sortable table
        strips = cp.get("strips") or []
        if strips:
            strip_data = [
                [
                    s["strip_index"],
                    f"{s['z_m']*1000:.2f}",
                    f"{s['local_alpha_deg']:.3f}",
                    f"{s['cn']:.4f}",
                    f"{s['lift_n']:.4f}",
                    f"{s['cp_x_frac']:.4f}",
                    f"{s['local_reynolds']:.0f}",
                ]
                for s in strips
            ]
            strip_w = data_table(
                ["#", "z [mm]", "α [°]", "cn", "lift [N]", "x_cp/c", "Re"],
                strip_data,
                placeholder="Filter strips…",
            )
        else:
            strip_w = QLabel("No strip data.")
        self._add_section("Strips", strip_w)

        # Structure sub-tabs
        st_w = QTabWidget()
        for case in ("cruise", "aggressive", "emergency"):
            st_w.addTab(
                searchable_table(dict_to_rows(p["structure"][case])),
                case.title(),
            )
        self._add_section("Structure", st_w)

        ss = QWidget()
        ss_l = QVBoxLayout(ss)
        ss_l.addWidget(searchable_table(dict_to_rows(p["servo"])))
        ss_l.addWidget(searchable_table(dict_to_rows(p["shaft_fit"])))
        self._add_section("Servo & Shaft", ss)

        self._add_section("Validation", searchable_table(dict_to_rows(p["hydro_validation"])))

        mfg = p["manufacturing"]
        mfg_w = QWidget()
        mfg_l = QVBoxLayout(mfg_w)
        mfg_l.addWidget(searchable_table(dict_to_rows(mfg)))
        for note in mfg.get("notes") or []:
            mfg_l.addWidget(QLabel(f"• {note}"))
        self._add_section("Manufacturing", mfg_w)

        sens = p.get("sensitivity")
        if sens:
            sens_rows = [
                [
                    pt["parameter"],
                    f"{pt['perturbation']:+.0%}",
                    f"{pt['M_design_Nm']:.4f}",
                    f"{pt['span_m']*1000:.2f}",
                    f"{pt['area_m2']:.6f}",
                    f"{pt['CD']:.4f}",
                    f"{pt['delta_M_frac']:+.2%}",
                    f"{pt['delta_span_frac']:+.2%}",
                    "OK" if pt["passed"] else "FAIL",
                ]
                for pt in sens["points"]
            ]
            sens_w = data_table(
                ["Param", "Δ", "M [N·m]", "span [mm]", "area", "CD", "ΔM", "Δspan", "Pass"],
                sens_rows,
                placeholder="Filter sensitivity…",
            )
        else:
            sens_w = QLabel("Enable “Run ±10% sensitivity” and re-run.")
        self._add_section("Sensitivity", sens_w)

        opt = p.get("optimization")
        self._add_section(
            "Optimization",
            searchable_table(dict_to_rows(opt)) if opt else QLabel("Enable NSGA-II and re-run."),
        )

        trace_w = QWidget()
        tr_l = QVBoxLayout(trace_w)
        hist = p.get("iteration_history") or []
        if hist:
            hist_rows = [
                [i + 1, h.get("area"), h.get("alpha_deg"), h.get("cl_req"), h.get("ar")]
                for i, h in enumerate(hist)
            ]
            tr_l.addWidget(
                data_table(["Iter", "area", "α [°]", "CL_req", "AR"], hist_rows)
            )
        if p.get("warnings"):
            warn = SectionCard("Warnings")
            for warn_msg in p["warnings"]:
                warn.add_widget(QLabel(f"• {warn_msg}"))
            tr_l.addWidget(warn)
        eq_edit = QTextEdit()
        eq_edit.setReadOnly(True)
        eq_edit.setPlainText(", ".join(p.get("equation_ids") or []))
        eq_edit.setMaximumHeight(120)
        tr_l.addWidget(QLabel("Equation IDs (select to copy):"))
        tr_l.addWidget(eq_edit)
        tr_l.addStretch(1)
        self._add_section("Trace", trace_w)

        self._exports_tab = QWidget()
        self._exports_layout = QVBoxLayout(self._exports_tab)
        self._exports_layout.addWidget(
            QLabel("Use toolbar Export buttons — paths will appear here with click-to-copy.")
        )
        self._exports_layout.addStretch(1)
        self._add_section("Exports", self._exports_tab)

        raw = QTextEdit()
        raw.setReadOnly(True)
        mono = QFont("monospace")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        raw.setFont(mono)
        raw.setPlainText(json.dumps(p, indent=2, default=str))
        self._nav.addItem("Raw JSON")
        self._stack.addWidget(raw)

        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav.setCurrentRow(0 if passed else 1)

    def _jump_to_inputs_hint(self, text: str) -> None:
        self._nav.setCurrentRow(0)

    def set_export_paths(self, paths: dict[str, Any]) -> None:
        if self._exports_layout is None:
            return
        while self._exports_layout.count():
            item = self._exports_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        from PySide6.QtGui import QGuiApplication

        for name, path in paths.items():
            btn = QPushButton(f"{name}:  {path}")
            btn.setObjectName("ExportPathButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            def _copy(p=str(path)) -> None:
                cb = QGuiApplication.clipboard()
                if cb:
                    cb.setText(p)

            btn.clicked.connect(_copy)
            self._exports_layout.addWidget(btn)
        self._exports_layout.addStretch(1)
        for i in range(self._nav.count()):
            if self._nav.item(i) and self._nav.item(i).text().startswith("Exports"):
                self._nav.setCurrentRow(i)
                break
