"""Collect every design failure with actionable corrections."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auv_fin_design.application.pipeline import DesignResult


@dataclass(frozen=True)
class DesignIssue:
    """One constraint failure or hard warning that blocks a good design."""

    category: str
    message: str
    corrections: tuple[str, ...]


@dataclass
class DesignDiagnosis:
    """Full pass/fail diagnosis with all violations and suggested fixes."""

    passed: bool
    issues: list[DesignIssue] = field(default_factory=list)

    @property
    def failure_count(self) -> int:
        return len(self.issues)

    def format_lines(self) -> list[str]:
        """Human-readable block for GUI / text reports."""
        if self.passed and not self.issues:
            return [
                "=== DESIGN DIAGNOSIS ===",
                "Status: PASSED — all engineering checks satisfied.",
                "No violations. No corrections needed.",
            ]

        lines = [
            "=== DESIGN DIAGNOSIS ===",
            f"Status: FAILED — {self.failure_count} violation(s) must be resolved.",
            "",
            "--- ALL VIOLATIONS ---",
        ]
        for i, issue in enumerate(self.issues, start=1):
            lines.append(f"{i}. [{issue.category}] {issue.message}")

        # Deduplicate corrections while preserving order
        seen: set[str] = set()
        corrections: list[str] = []
        for issue in self.issues:
            for c in issue.corrections:
                if c not in seen:
                    seen.add(c)
                    corrections.append(c)

        lines += ["", "--- SUGGESTED CORRECTIONS (to get a good design) ---"]
        if not corrections:
            lines.append("(none — review warnings and re-run)")
        else:
            for i, c in enumerate(corrections, start=1):
                lines.append(f"{i}. {c}")

        lines += [
            "",
            "Tip: Change one or two inputs at a time, then re-run Design.",
            "Common levers: Max span/D, turn radius/time, design speed,",
            "servo torque, shaft diameter, material, stall margin (defaults.yaml).",
        ]
        return lines

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "failure_count": self.failure_count,
            "violations": [
                {
                    "category": i.category,
                    "message": i.message,
                    "corrections": list(i.corrections),
                }
                for i in self.issues
            ],
            "corrections": list(
                dict.fromkeys(c for i in self.issues for c in i.corrections)
            ),
        }


def diagnose_design(result: DesignResult) -> DesignDiagnosis:
    """Inspect DesignResult and list every blocking violation with fixes."""
    issues: list[DesignIssue] = []
    g = result.geometry
    hv = result.hydro_validation
    sf = result.shaft_fit
    srv = result.servo_result
    mfg = result.manufacturing

    # --- Geometry packaging (exclude shaft messages duplicated below) ---
    for msg in result.geometry_violations:
        if msg.startswith("FAIL:") and "shaft" in msg.lower():
            continue
        if "thickness at" in msg.lower() and "chord" in msg.lower():
            continue
        cat = "Geometry"
        corrections: list[str] = []
        low = msg.lower()
        if "span" in low and "exceeds" in low:
            corrections = [
                "Increase Max span / D (allows taller fins).",
                "Soften the maneuver: larger turning radius or longer turn establishment time "
                "(reduces required yaw moment → smaller fins).",
                "Raise cruise/design speed if the mission allows (higher dynamic pressure → less area).",
                "Uncheck fixed fin dimensions if overrides force an oversized span.",
            ]
        elif "tip chord" in low:
            corrections = [
                "Increase root chord / allow larger planform (or raise taper ratio in defaults.yaml).",
                "Relax min_tip_chord_m in configs/defaults.yaml if manufacturing allows a sharper tip.",
                "Soften the turn so auto-sizing does not shrink tip chord so far.",
            ]
        elif "tip thickness" in low or "min wall" in low:
            corrections = [
                "Choose a thicker airfoil (e.g. NACA0018 instead of 0012).",
                "Increase root/tip chord so absolute thickness rises.",
                "Lower min_wall_thickness_m only if you accept thinner printed walls.",
            ]
        else:
            corrections = [
                "Review geometry_constraints in configs/defaults.yaml.",
                "Soften maneuver or raise Max span / D.",
            ]
        issues.append(DesignIssue(cat, msg, tuple(corrections)))

    # --- Shaft fit at 25% chord ---
    if not sf.fits:
        issues.append(
            DesignIssue(
                "Shaft / hinge",
                sf.message,
                (
                    "Reduce Shaft diameter so it fits inside the root section at 25% chord.",
                    "Increase root chord (optional fixed dimensions or softer packaging) "
                    "to thicken the airfoil at the hinge.",
                    "Select a thicker airfoil (NACA0015 / NACA0018).",
                    "Lower shaft_clearance_factor in defaults.yaml only if a tighter fit is acceptable.",
                ),
            )
        )

    # --- Hydro / control validation ---
    if not hv.lift_ok:
        issues.append(
            DesignIssue(
                "Hydrodynamics — lift",
                f"Insufficient lift: actual {hv.actual_lift_N:.3f} N vs required "
                f"{hv.required_lift_N:.3f} N (margin {hv.lift_margin:+.1%}).",
                (
                    "Allow larger fins: increase Max span / D.",
                    "Soften turn (larger radius / more time) to cut required lift.",
                    "Increase design speed if mission allows (higher q).",
                    "If using fixed fin dimensions, uncheck them or enlarge root chord & span.",
                ),
            )
        )
    if not hv.control_authority_ok:
        issues.append(
            DesignIssue(
                "Hydrodynamics — control authority",
                f"Insufficient yaw authority: available {hv.available_control_moment_Nm:.3f} N·m "
                f"vs required {hv.required_control_moment_Nm:.3f} N·m "
                f"(margin {hv.authority_margin:+.1%}).",
                (
                    "Soften the maneuver (larger turning radius or longer turn time).",
                    "Increase Max span / D so fins can produce more force.",
                    "Move fins farther aft (higher Fin root LE / L) for a longer lever arm.",
                    "Increase design speed if allowed.",
                ),
            )
        )
    if not hv.stall_ok:
        issues.append(
            DesignIssue(
                "Hydrodynamics — stall",
                f"Stall margin {hv.stall_margin_deg:.2f}° is below the required margin "
                f"(need ≥ ~5°). Operating α = {hv.deflection_deg:.2f}°.",
                (
                    "Enlarge the fin (raise Max span / D) so the same lift is achieved at lower α.",
                    "Soften the turn to reduce required CL.",
                    "Try another airfoil with higher stall angle (auto or NACA0015/0018).",
                    "Slightly reduce stall_margin_deg in defaults.yaml only if you accept less safety.",
                ),
            )
        )
    if not hv.deflection_ok:
        issues.append(
            DesignIssue(
                "Hydrodynamics — deflection limit",
                f"Required fin angle {hv.deflection_deg:.2f}° exceeds servo max rotation "
                f"{hv.max_deflection_deg:.1f}°.",
                (
                    "Use a servo with larger rotation travel (this model allows up to 180°).",
                    "Enlarge fins / soften maneuver so less deflection is needed.",
                    "Increase Max span / D.",
                ),
            )
        )
    if hv.cavitation_risk:
        issues.append(
            DesignIssue(
                "Hydrodynamics — cavitation",
                f"Cavitation risk: σ = {hv.cavitation_number:.2f} < 1.5 "
                f"(low pressure relative to vapor pressure).",
                (
                    "Reduce design / max speed.",
                    "Operate deeper (higher ambient pressure) if the mission allows.",
                    "Reduce local loading (larger area → lower CL at same lift).",
                ),
            )
        )

    # --- Maneuver deflection (α = δ model); −0.1° tolerance matches solver ---
    md = result.maneuver_deflection
    if md is not None and md.delta_margin_deg < -0.1:
        issues.append(
            DesignIssue(
                "Maneuver deflection",
                f"Required deflection {md.delta_required_deg:.2f}° exceeds usable "
                f"{md.delta_max_usable_deg:.2f}° (margin {md.delta_margin_deg:.2f}°).",
                (
                    "Enlarge the planform (Max span / D) to lower required CL / deflection.",
                    "Soften turn radius or establishment time.",
                    "Select an airfoil that stalls later.",
                    "Reduce stall_margin_deg in defaults.yaml only with engineering judgment.",
                ),
            )
        )

    # --- Structure (all load cases that gate DesignResult.passed) ---
    for st, label in (
        (result.structure_cruise, "cruise"),
        (result.structure_aggressive, "aggressive"),
        (result.structure_emergency, "emergency"),
    ):
        if not st.fos_ok:
            issues.append(
                DesignIssue(
                    f"Structure — {label} FoS",
                    f"Factor of safety {st.fos_yield:.2f} < required {st.required_fos:.2f} "
                    f"(von Mises {st.combined_von_mises:.3e} Pa).",
                    (
                        "Switch to a stronger material (e.g. PETG, ABS, aluminium vs PLA).",
                        "Increase root chord / thickness (thicker airfoil or larger chord).",
                        "Soften emergency/aggressive loads: lower max speed or emergency_load_factor.",
                        "Reduce fin span if packaging allows a stubbier, thicker root.",
                    ),
                )
            )
        if label == "cruise" and not st.tip_deflection_ok:
            issues.append(
                DesignIssue(
                    "Structure — tip deflection",
                    f"Tip deflection {st.tip_deflection*1000:.2f} mm exceeds the limit "
                    f"for this span (load case: {label}).",
                    (
                        "Use a stiffer material (higher Young’s modulus).",
                        "Increase root thickness (thicker airfoil / larger root chord).",
                        "Reduce span (if Max span / D and lift still allow).",
                        "Raise tip_deflection_limit_span_frac in defaults.yaml only if more flex is OK.",
                    ),
                )
            )

    # Aggressive FoS is checked; also tip deflection on aggressive is informative —
    # DesignResult.passed only checks cruise tip_deflection_ok. Mirror that.

    # --- Servo ---
    if not srv.continuous_ok:
        issues.append(
            DesignIssue(
                "Servo — torque",
                f"Servo utilization {srv.utilization:.1%} exceeds continuous limit "
                f"(hinge moment {srv.hinge_moment:.3f} N·m, required {srv.torque_required:.3f} N·m).",
                (
                    "Increase Servo torque [N·m] to match a stronger servo.",
                    "Reduce hinge moment: thicker airfoil with lower |Cm|, or smaller MAC/area "
                    "if lift still meets the turn.",
                    "Raise util_continuous_limit in defaults.yaml only if peak duty is acceptable.",
                ),
            )
        )
    if not srv.shaft_ok:
        issues.append(
            DesignIssue(
                "Servo — shaft strength",
                f"Shaft factor of safety {srv.shaft_fos:.2f} < 2.0 "
                f"(shear stress {srv.shaft_shear_stress:.3e} Pa).",
                (
                    "Increase Shaft diameter [m] (must still fit in the fin — check Shaft Fit).",
                    "Use a higher-strength shaft material / sleeve (raises allowable stress).",
                    "Reduce hinge moment (see servo torque corrections).",
                ),
            )
        )
    for mode in srv.failure_modes:
        # Avoid duplicating continuous / shaft already covered
        if "continuous" in mode.lower() or "shaft shear" in mode.lower():
            continue
        if "bearing" in mode.lower():
            issues.append(
                DesignIssue(
                    "Servo — bearing",
                    mode + f" (radial load {srv.bearing_radial_load:.1f} N).",
                    (
                        "Use a larger / rated underwater bearing at the root.",
                        "Reduce fin lift (soften maneuver or add more fins if layout allows).",
                    ),
                )
            )
        elif "actuation" in mode.lower() or "slow" in mode.lower():
            issues.append(
                DesignIssue(
                    "Servo — speed",
                    mode + f" (actuation time {srv.actuation_time_s:.3f} s).",
                    (
                        "Use a faster servo (higher °/s no-load speed).",
                        "Reduce required deflection (larger fins / softer turn).",
                    ),
                )
            )
        else:
            issues.append(
                DesignIssue(
                    "Servo",
                    mode,
                    ("Review servo specification and hinge loads.",),
                )
            )

    # --- Manufacturing ---
    if not mfg.printable:
        for note in mfg.notes:
            if "below min" in note.lower() or "tip thickness" in note.lower():
                issues.append(
                    DesignIssue(
                        "Manufacturing",
                        note,
                        (
                            "Increase tip chord or use a thicker airfoil.",
                            "Lower min_wall_thickness_m only if your printer can resolve thinner walls.",
                            "Consider resin printing or machining for fine tips.",
                        ),
                    )
                )
                break
        else:
            issues.append(
                DesignIssue(
                    "Manufacturing",
                    "Fin is marked not printable under current rules.",
                    (
                        "Review manufacturing notes in the report.",
                        "Increase tip thickness via chord or airfoil selection.",
                    ),
                )
            )

    return DesignDiagnosis(passed=len(issues) == 0, issues=issues)
