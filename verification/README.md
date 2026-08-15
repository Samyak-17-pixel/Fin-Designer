# Verification notebooks

This folder is the **engineering verification layer** of the AUV Fin Design suite.

It is **not** the same as `tests/`.

| Location | Role |
|----------|------|
| `tests/` | Automated pytest: unit, integration, golden regression. Fast, CI-gated, assert-based. |
| `verification/` | Jupyter notebooks: **recompute the governing equations by hand**, compare to production code, plot intermediate physics, and document limitations. |

Every notebook is meant to answer: *does the production module implement the registered equation, and does the result make physical sense?*

**Pass criterion used throughout:** relative error \(\le 1\%\) (`tol = 0.01`) unless a notebook states otherwise.

```
verification/
├── README.md                          ← this file
├── verify_vehicle_model.ipynb         ← hull geometry, inertia, stations, fluids
├── verify_hydrodynamics.ipynb         ← hull hydro coefficients (EQ-HYD-001…017)
├── verify_control_allocation.ipynb    ← yaw moment + X-tail lift split
├── verify_fin_sizing.ipynb            ← planform area, span, MAC
├── verify_hydro_validation.ipynb      ← full pipeline hydro checks on golden vehicle
└── verify_center_of_pressure.ipynb    ← strip Cp integration, CoP plots, sensitivity
```

There are **six notebooks and this README**. There is no `__init__.py`, no helper `.py` module, and no data files stored in this folder. Notebooks import the installed package `auv_fin_design` and read repo data from `data/` when needed.

---

## How this folder fits the design pipeline

The production workflow is:

```
Vehicle + Mission
    → Hydrodynamics (hull coefficients)
    → Maneuvering (required yaw moment)
    → Allocation (lift per fin)
    → Fin sizing (planform)
    → Airfoil / finite-wing aero
    → Dynamic CoP (strip Cp integration)
    → Hydro validation (lift, authority, stall, cavitation)
    → Structure / servo / manufacturing
```

These notebooks cover the **physics core** of that chain, not STL export, NSGA-II, or the GUI.

| Notebook | Pipeline stage | Production module | Equation IDs |
|----------|----------------|-------------------|--------------|
| `verify_vehicle_model.ipynb` | Inputs / hull math | `domain/vehicle/model.py` | EQ-VEH-*, EQ-FLUID-* |
| `verify_hydrodynamics.ipynb` | Hull hydro coefficients | `domain/hydrodynamics/estimator.py` | EQ-HYD-001…017 |
| `verify_control_allocation.ipynb` | Yaw moment + fin lift | `domain/control/maneuvering.py`, `allocation.py` | EQ-MAN-*, EQ-ALLOC-* |
| `verify_fin_sizing.ipynb` | Planform geometry | `domain/geometry/sizing.py` | EQ-GEO-* |
| `verify_hydro_validation.ipynb` | End-to-end hydro checks | `domain/validation/hydro.py` + `pipeline.py` | EQ-HYD-VAL-* (and pipeline) |
| `verify_center_of_pressure.ipynb` | 3D CoP from Cp | `domain/center_of_pressure/` | EQ-COP-001…007 |

Canonical formulas: `docs/equations/equation_register.yaml`.  
Golden vehicle inputs: `benchmarks/golden_vehicle/golden_vehicle.yaml`.

---

## How to run the notebooks

From the repo root, with the project venv active:

```bash
cd /path/to/fins
source .venv/bin/activate          # or your venv
pip install -e ".[dev]"            # jupyter + ipywidgets if needed
jupyter notebook verification/
# or: jupyter lab verification/
```

The package must be importable as `auv_fin_design`. `pyproject.toml` puts sources under `src/`. If imports fail, either install editable (`pip install -e .`) or set `PYTHONPATH=src`.

**Kernel:** Python 3.10+ matching the venv that has `numpy`, `scipy`, `matplotlib`, `pydantic`, and `auv_fin_design`.

**Working directory:** start Jupyter from the **repo root** so `repo_root()` and `data/airfoils/` resolve. If you open a notebook from a nested cwd, CoP plots that load Cp archives can fail.

---

## Shared numerical / vehicle constants

Most notebooks use the **golden hull** (not always the full golden mission):

| Quantity | Symbol | Typical value | Where used |
|----------|--------|---------------|------------|
| Length | \(L\) | 1.35 m | all except fin-sizing |
| Diameter | \(D\) | 0.1685 m | vehicle, hydro, allocation |
| Mass | \(m\) | 24 kg | vehicle, hydro, allocation |
| Water | — | freshwater | \(\rho = 998.2\,\mathrm{kg/m^3}\), \(\nu = 1.004\times 10^{-6}\,\mathrm{m^2/s}\) |
| Design speed | \(V\) | 1.5 m/s | hydro, allocation, CoP |
| Turn radius | \(R_t\) | 6 m | hydro, allocation |
| Turn time | \(T\) | **30 s** (golden / allocation / hydro-validation); **4 s** in `verify_hydrodynamics.ipynb` | see that notebook |
| Dynamic pressure at 1.5 m/s (fresh) | \(q\) | \(\tfrac12\rho V^2 \approx 1123\,\mathrm{Pa}\) | fin sizing, CoP |

**1% relative error:**

\[
\varepsilon = \frac{|x_\mathrm{manual} - x_\mathrm{prod}|}{\max(|x_\mathrm{manual}|, 10^{-30})}
\qquad \text{PASS if } \varepsilon \le 0.01
\]

---

## File-by-file reference

### 1. `verify_vehicle_model.ipynb`

**Purpose:** Prove the hull is a **uniform circular cylinder** with closed-form area, volume, inertia, CG, and fin station.

**Cells**

| Cell | Type | What it does |
|------|------|----------------|
| 0 | Markdown | Title, module, EQ-VEH / EQ-FLUID, SRDS V1, version 0.1.0 |
| 1 | Markdown | Engineering theory: \(R, A_f, S_w, \nabla, I_x, I_y, I_z\), aft fins at \(0.92L\), CG at mid-length |
| 2 | Code | Manual formulas vs `VehicleModel(...)` for golden \(L, D, m\) |
| 3 | Markdown | Conclusion: match within 1%; V1 ignores nose/tail and uses **solid** inertia |

**Formulas recomputed by hand**

\[
\begin{aligned}
R &= D/2 \\
A_f &= \pi R^2 \\
S_w &= \pi D L \\
\nabla &= \pi R^2 L \\
I_x &= \tfrac12 m R^2 \\
I_y = I_z &= \tfrac{1}{12} m (3R^2 + L^2) \\
x_\mathrm{CG} &= 0.5 L \\
x_\mathrm{fin,LE} &= 0.92 L
\end{aligned}
\]

**Production object:** `VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water='freshwater')`

**Checks:** `radius`, `frontal_area`, `wetted_area`, `volume`, `Ix`, `Iz`, `x_cg`, `x_fin_root_le`

**Fluid:** freshwater density/viscosity are **hardcoded in the notebook** (`998.2`, `1.004e-6`) to match `configs/defaults.yaml` / `domain/constants/fluids.py`. The notebook does not currently assert fluid properties themselves (EQ-FLUID-*), even though the header mentions them.

**Limitations (intentional V1)**

- Wetted area is a **bare cylinder** (no nose cap, tail cone, or appendages).
- Inertia is a **solid cylinder of mass \(m\)**, not a thin shell or mass distribution from ballast.
- CG is **mid-length** unless you change `cg_fraction_of_length`.

**Source of truth:** `src/auv_fin_design/domain/vehicle/model.py`

---

### 2. `verify_hydrodynamics.ipynb`

**Purpose:** Recompute **hull hydrodynamic coefficients** independently and compare to `estimate_hydrodynamics()`.

This is the notebook that answers “where do \(C_f\), \(C_D\), added mass, and yaw damping come from?”

**Cells**

| Cell | Type | What it does |
|------|------|----------------|
| 0 | Markdown | Title; module Hydrodynamic Estimator; EQ-HYD-001…017; Fossen, ITTC-1957, Hoerner |
| 1 | Code | Manual Re, \(q\), \(C_f\), \(Y_{\dot v}\), \(N_{\dot r}\), \(N_{r\|r\|}\), \(N_r\) vs production |

**Mission used in this notebook (not identical to golden turn time)**

```python
VehicleModel(length=1.35, diameter=0.1685, mass=24.0, water='freshwater')
MissionModel(design_speed=1.5, turning_radius=6.0, turn_establishment_time=4.0)
```

`turn_establishment_time=4.0` **does not enter** the hydro estimator (yaw linearization uses \(r_\mathrm{op}=V/R_t\)). The 4 s value is leftover / unused for these particular checks. Golden vehicle uses **30 s** for maneuvering, not for hull coefficients.

**Manual vs production pairs**

| Name | Manual formula | Production field |
|------|----------------|------------------|
| `Re_L` | \(V L / \nu\) | `h.re_length` (EQ-HYD-001) |
| `q` | \(\tfrac12 \rho V^2\) | `h.dynamic_pressure` (EQ-HYD-004) |
| `Cf` | `ittc_1957_cf(Re_L)` | `h.cf_ittc` (EQ-HYD-005) |
| `Y_vdot` | \(\rho \pi R^2 L\) | `h.Y_vdot` (EQ-HYD-010) |
| `N_rdot` | \(\rho \pi R^2 L^3 / 12\) | `h.N_rdot` (EQ-HYD-012) |
| `N_\|r\|r` | \(-\frac{1}{32}\rho C_{D,\mathrm{cross}} D L^4\) with \(C_D=1\) | `h.N_r_abs_r` (EQ-HYD-015) |
| `N_r` | \(2 N_{r\|r\|} \|r_\mathrm{op}\|\) with \(r_\mathrm{op}=V/R_t\) | `h.N_r` (EQ-HYD-016) |

ITTC friction is **not** expanded in the notebook; it calls the same production helper `ittc_1957_cf`:

\[
C_f = \frac{0.075}{(\log_{10} Re_L - 2)^2}
\]

(with \(Re_L\) clamped to \(10^5\) if smaller — EQ-HYD-005).

**What this notebook does *not* currently print/assert**

These **are** computed in `estimate_hydrodynamics()` and registered, but this notebook does not pair them:

| ID | Quantity | Why it matters |
|----|----------|----------------|
| EQ-HYD-002 | \(Re_D = V D/\nu\) | Diameter Reynolds number |
| EQ-HYD-003 | flow regime | laminar / transitional / turbulent |
| EQ-HYD-006 | friction drag \(D_f = q C_f S_w\) | `drag_friction` |
| EQ-HYD-008 | Hoerner \(C_{D,A_f}\) | `cd_frontal` |
| EQ-HYD-009 | hull drag \(D_h = q C_{D,A_f} A_f\) | `drag_total_hull` |
| EQ-HYD-011 | surge added mass \(X_{\dot u}\) | `X_udot` |
| EQ-HYD-013 | roll added inertia \(K_{\dot p}=0\) | `K_pdot` |
| EQ-HYD-014 | \(C_{D,\mathrm{cross}}=1.0\) | default, used inside EQ-HYD-015 |
| EQ-HYD-017 | wake fraction \(w=0\) | `wake_fraction` |

So the header “EQ-HYD-001…017” is the **module scope**; the **executed checks** are the seven pairs in the table above.

**Hoerner frontal Cd (implemented, not plotted here)**

\[
C_{D,A_f} = C_f \frac{S_w}{A_f}\left(1 + 1.5\left(\frac{D}{L}\right)^{1.5} + 7\left(\frac{D}{L}\right)^3\right)
\]

**Yaw damping linearization**

Operating yaw rate for the design turn:

\[
r_\mathrm{op} = V / R_t = 1.5 / 6 = 0.25\,\mathrm{rad/s}
\]

\[
N_r = 2\, N_{r|r|}\, |r_\mathrm{op}|
\]

**Source of truth:** `src/auv_fin_design/domain/hydrodynamics/estimator.py`  
**Config knobs:** `configs/defaults.yaml` → `hydrodynamics.crossflow_cd` (1.0), `axial_added_mass_factor` (0.1)

---

### 3. `verify_control_allocation.ipynb`

**Purpose:** Verify **required yaw moment** and **X-tail lift per fin** on the golden vehicle with \(T=30\,\mathrm{s}\).

**Cells**

| Cell | Type | What it does |
|------|------|----------------|
| 0 | Markdown | Title; golden vehicle \(T=30\,\mathrm{s}\); EQ-MAN-*, EQ-ALLOC-* |
| 1 | Code | Hydro → control requirement → allocate with `root_chord=0.08`; assert \(r\) and \(\dot r\); print \(M_\mathrm{design}\), lever, lift |

**Chain called**

1. `estimate_hydrodynamics(v, m)` — hull \(N_{\dot r}\), \(N_r\), \(N_{r\|r\|}\)
2. `compute_control_requirement(v, h, m, control_margin=0.25)`
3. `allocate_x_tail_yaw(v, req, root_chord=0.08)`

**Kinematic asserts (1%)**

\[
r_\mathrm{target} = V / R_t = 1.5 / 6, \qquad
\dot r = r_\mathrm{target} / 30
\]

**Yaw moment (not expanded in the notebook, but this is what `M_design` is)**

\[
\begin{aligned}
M_I &= I_z \dot r \\
M_A &= N_{\dot r} \dot r \\
M_D &= N_r r + N_{r|r|} |r| r \\
M_\mathrm{transient} &= M_I + M_A + |M_D| \\
M_\mathrm{steady} &= |M_D| \\
M_\mathrm{design} &= \max(|M_\mathrm{transient}|, |M_\mathrm{steady}|) \times 1.25
\end{aligned}
\]

**Allocation (root ¼-chord, not yet dynamic CoP)**

\[
x_\mathrm{force} = x_\mathrm{fin,LE} + 0.25\, c_\mathrm{root}, \quad
c_\mathrm{root} = 0.08\,\mathrm{m}
\]

\[
\ell = |x_\mathrm{force} - x_\mathrm{CG}|, \qquad
L_\mathrm{fin} = \frac{M_\mathrm{design}}{4\,\ell\,\sin 45°}
\]

The **full pipeline** later replaces \(x_\mathrm{force}\) with the integrated CoP body-\(x\). This notebook does **not** do that second iteration; it is the **initial QC-station** allocation.

**Printed outputs:** `M_design`, `lever_arm`, `lift_per_fin`, then `PASS`

**Sources:**  
`domain/control/maneuvering.py`, `domain/control/allocation.py`

---

### 4. `verify_fin_sizing.ipynb`

**Purpose:** Check planform **area, span, MAC** against the closed-form sizing relations for a **synthetic** load, not the golden vehicle.

**Cells**

| Cell | Type | What it does |
|------|------|----------------|
| 0 | Markdown | Geometry EQ-GEO-* vs production sizing |
| 1 | Code | `size_fin(lift=10 N, q=1123 Pa, CL=0.2, AR=0.8, taper=0.5, t/c=0.18)` |

**Manual formulas**

\[
S = \frac{L}{q\, C_L} = \frac{10}{1123 \times 0.2}
\]

\[
b = \sqrt{S \cdot AR} = \sqrt{S \times 0.8}
\]

MAC via production helper `mean_aerodynamic_chord(c_\mathrm{root}, \lambda=0.5)` (EQ-GEO trapezoid MAC), compared to `g.mac`.

**What is asserted:** `g.area` vs \(S\), `g.span` vs \(b\), `g.mac` vs MAC helper — all 1%.

**What is not asserted here:** taper chords \(c_r, c_t\), sweep, corner points, thickness, mass, geometry constraints, shaft fit.

**Source:** `domain/geometry/sizing.py` (`size_fin`, `mean_aerodynamic_chord`)

**Why \(q=1123\):** \(\tfrac12 \times 998.2 \times 1.5^2 \approx 1123\,\mathrm{Pa}\) (freshwater cruise of the golden vehicle). Lift 10 N is a **round test load**, not the allocated golden lift.

---

### 5. `verify_hydro_validation.ipynb`

**Purpose:** Run the **full design pipeline** on the golden YAML vehicle and assert hydrodynamic validation (and overall `passed`) is OK.

This is the only notebook in the folder that calls `run_design_pipeline` / `load_golden_vehicle`. It is an **integration-style** verification, closer to `tests/integration/test_full_pipeline.py` than to a hand calculation.

**Cells**

| Cell | Type | What it does |
|------|------|----------------|
| 0 | Markdown | Chapter 3.7 hydrodynamic validation vs golden vehicle |
| 1 | Code | Pipeline with `run_sensitivity=False`, `run_optimization=False`; print margins; `assert hv.overall_ok`; `assert r.passed` |

**Printed fields** (`HydrodynamicValidationModel`)

| Field | Meaning |
|-------|---------|
| `lift_margin` | (actual lift − required) / required |
| `authority_margin` | (available yaw moment − \(M_\mathrm{design}\)) / \(M_\mathrm{design}\) |
| `stall_margin_deg` | stall \(\alpha\) − operating \(\alpha\) |
| `cavitation_number` | \(\sigma = (p_\infty - p_v)/q\) |
| `overall_ok` | lift, authority, stall, deflection, and no cavitation risk |

**Dependencies:** polar CSVs under `data/NACA00xx/`, Cp archives under `data/airfoils/`, `configs/defaults.yaml` (span/D, stall margin, servo, etc.).

If packaging is too tight (`max_span_over_diameter` too small) or CoP/deflection checks fail, **`r.passed` can be False** even when hydro validation is OK. This notebook asserts **both**.

**Source:** `domain/validation/hydro.py`, `application/pipeline.py`

---

### 6. `verify_center_of_pressure.ipynb`

**Purpose:** Visual and numerical check of **dynamic 3D CoP**: load Cp, integrate chordwise, strip-theory spanwise, compare to ¼-chord and \(C_m/C_L\), plot CoP vs \(\alpha\), speed (Re), and aspect ratio.

**This notebook needs matplotlib and `data/airfoils/` Cp CSVs.**

**Cells**

| Cell | Type | What it does |
|------|------|----------------|
| 0 | Markdown | EQ-COP-001, 002, 003, 004, 007; hinge stays at 25% chord |
| 1 | Code | Print `repo_root()` and list `data/airfoils/` |
| 2 | Markdown | “Cp(x) at design alpha” |
| 3 | Code | Load NACA0015, Re = \(2\times 10^5\), \(\alpha=5^\circ\); plot \(C_{p,\mathrm{upper}}\), \(C_{p,\mathrm{lower}}\), \(\Delta C_p\) |
| 4 | Markdown | “Strip discretization and loads” |
| 5 | Code | Build a tapered fin; `solve_center_of_pressure` with 40 strips; plot strip lift, strip \(x_{cp}/c\), bar chart QC vs Cm/CL vs integrated; print CoP in mm and deflection |
| 6 | Markdown | “CoP migration with alpha and Re” |
| 7 | Code | Sweep \(\alpha = 1\ldots 12^\circ\); sweep \(V = 0.8, 1.2, 1.5, 2.0\) m/s |
| 8 | Markdown | “Aspect-ratio sensitivity (same area)” |
| 9 | Code | Fixed \(S=0.008\,\mathrm{m^2}\), AR ∈ {0.8, 1.2, 1.8, 2.5}, taper 0.5; plot \(z_{cp}/b\) |

**Governing equations shown in the notebook**

\[
\begin{aligned}
c_n &= \int_0^1 \Delta C_p\, d(x/c) \\
x_{cp}/c &= \frac{\int_0^1 (x/c)\Delta C_p\, d(x/c)}{c_n} \\
dL &= q\, c(z)\, c_n(z)\, dz \\
z_{cp} &= \frac{\int z\, dL}{L} \\
\delta_\mathrm{req} &= C_{L,\mathrm{req}} / C_{L\alpha,3D} \quad (\alpha=\delta,\ \text{Helmbold})
\end{aligned}
\]

**Example fin in cell 5**

- Root chord 0.12 m, tip 0.06 m, span 0.09 m, \(t/c=0.15\) (NACA0015)
- \(q = 1123\,\mathrm{Pa}\), \(V=1.5\,\mathrm{m/s}\), \(\nu=1.004\times 10^{-6}\)
- \(\alpha=5^\circ\), polar \(C_m=0\), \(C_L=0.4\) (verification cross-check inputs)
- 40 strips; stall \(\alpha=12^\circ\), stall margin \(5^\circ\); required lift 2 N (for deflection check)

**Plots**

1. Section Cp vs \(x/c\) (invert y-axis, suction up — XFOIL convention)
2. Strip lift vs span \(z\)
3. Strip \(x_{cp}/c\) vs \(z\) with 0.25 reference line
4. Bar: quarter-chord vs \(C_m/C_L\) vs integrated \(x_{cp}/c\)
5. \(x_{cp}/c\) and \(z_{cp}\) vs \(\alpha\)
6. \(x_{cp}/c\) vs speed (Re via \(V\); **bootstrap Cp is Re-independent**, so this plot may be nearly flat)
7. \(z_{cp}/\mathrm{span}\) vs AR at constant area

**Critical data caveat**

Cp files under `data/airfoils/*/cp/` are **bootstrap** (`scripts/generate_cp_dataset.py`, Glauert + thickness), **not** XFOIL dumps. Integration code is what this notebook verifies; **absolute CoP accuracy is limited by that data**. Polar CSVs in `data/NACA00xx/` are real XFOIL/AirfoilTools and are **not** what cell 3 plots.

**Sources:**  
`domain/center_of_pressure/cp_solver.py`, `pressure_integrator.py`, `strip_theory.py`, `xfoil_provider.py`  
**Related automated tests:** `tests/unit/test_center_of_pressure.py`  
**Related benchmark:** `benchmarks/center_of_pressure_reference.json`

---

## Mapping: notebook → production files → tests

| Notebook | Production | Tests / other |
|----------|------------|----------------|
| `verify_vehicle_model.ipynb` | `domain/vehicle/model.py`, `domain/constants/fluids.py` | `tests/unit/test_vehicle.py` |
| `verify_hydrodynamics.ipynb` | `domain/hydrodynamics/estimator.py` | `tests/unit/test_hydrodynamics.py` |
| `verify_control_allocation.ipynb` | `domain/control/maneuvering.py`, `allocation.py` | `tests/unit/test_control.py` |
| `verify_fin_sizing.ipynb` | `domain/geometry/sizing.py` | `tests/unit/test_geometry_aero.py` |
| `verify_hydro_validation.ipynb` | `domain/validation/hydro.py`, `application/pipeline.py` | `tests/integration/test_full_pipeline.py`, `tests/benchmarks/test_golden_vehicle.py` |
| `verify_center_of_pressure.ipynb` | `domain/center_of_pressure/*` | `tests/unit/test_center_of_pressure.py` |

---

## What is *not* in this folder (and where it lives)

These engineering pieces have **no dedicated notebook here** (as of this README):

| Topic | Location |
|-------|----------|
| Finite-wing Helmbold / polar interpolation | `domain/airfoil/finite_wing.py`, `database.py` |
| Structural beam / FoS | `domain/structural/beam.py` |
| Servo / hinge / shaft stress | `domain/servo/analysis.py` |
| Shaft fit at 25% chord | `domain/geometry/shaft_fit.py` |
| Design diagnosis (violations + corrections) | `domain/validation/design_diagnosis.py` |
| Sensitivity ±10% | `domain/validation/sensitivity.py` |
| NSGA-II | `domain/optimization/nsga2.py` |
| STL / Fusion / Gazebo / ROS | `domain/manufacturing/`, `adapters/` |
| GUI | `ui/main_window.py` |

If you add a notebook, name it `verify_<module>.ipynb`, cite equation IDs in the first markdown cell, recompute by hand, compare to production, and keep the 1% rule unless physics requires a different tolerance.

---

## Recommended reading order

1. **`verify_vehicle_model.ipynb`** — hull geometry everything else sits on  
2. **`verify_hydrodynamics.ipynb`** — hull coefficients (\(C_f\), added mass, yaw damping)  
3. **`verify_control_allocation.ipynb`** — how those coefficients become **yaw moment** and fin lift  
4. **`verify_fin_sizing.ipynb`** — how lift + \(q\) + \(C_L\) become span and chords  
5. **`verify_center_of_pressure.ipynb`** — where the force acts on the fin  
6. **`verify_hydro_validation.ipynb`** — golden vehicle, full stack

That order matches the code path in `run_design_pipeline()`.

---

## Environment / troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| `ModuleNotFoundError: auv_fin_design` | Not installed editable; run `pip install -e .` from repo root |
| `Missing Cp archive` | `data/airfoils/` empty; run `python scripts/generate_cp_dataset.py` |
| CoP plots empty / interpolation error | Jupyter cwd not repo root |
| `verify_hydro_validation` AssertionError on `r.passed` | Packaging, stall, shaft, or diagnosis failure — see GUI Design Diagnosis |
| ROS `pytest` plugin errors | Unrelated to notebooks; `pytest.ini` disables `launch_testing` |
| Matplotlib not found | `pip install -e ".[dev]"` or `pip install matplotlib` |

**Python:** ≥ 3.10 (`pyproject.toml`).

---

## Engineering limitations to keep in mind while verifying

1. **Hull = cylinder.** No nose/tail, no sail, no propeller wake (wake fraction = 0).  
2. **ITTC + Hoerner** are empirical/slender-body, not CFD.  
3. **Yaw damping** is strip-theory circular-cylinder cross-flow (\(C_D=1\)), linearized at \(V/R_t\).  
4. **Allocation notebook** uses root ¼-chord, not integrated CoP.  
5. **Cp archives** are synthetic until replaced with real XFOIL Cp dumps.  
6. **Hydrodynamics notebook** does not yet assert every EQ-HYD-* ID listed in its title.  
7. **1%** is an *engineering* tolerance for floating-point and implementation match, not a statement of model accuracy vs tank tests.

---

## Equation ID cheat sheet (used by this folder)

**Vehicle / fluid:** EQ-VEH-001…006, EQ-FLUID-001…002  

**Hull hydro:** EQ-HYD-001 \(Re_L\); 002 \(Re_D\); 003 regime; 004 \(q\); 005 ITTC \(C_f\); 006 friction drag; 008 Hoerner \(C_D\); 009 hull drag; 010–013 added mass/inertia; 014–016 yaw damping; 017 wake = 0  

**Maneuver / allocation:** EQ-MAN-001 \(r=V/R\); 002 \(\dot r=r/T\); 003 \(I_z\dot r\); 004 \(N_{\dot r}\dot r\); 005 damping moment; 006 transient/steady; 007 \(M_\mathrm{design}\) with margin; EQ-ALLOC-002 lever; 003 QC station; 004 X-tail \(L = M/(4\ell\sin 45°)\)  

**Geometry:** EQ-GEO area \(S=L/(q C_L)\), span \(b=\sqrt{S\cdot AR}\), MAC of trapezoid  

**CoP:** EQ-COP-001…007 (integrals, strips, hinge moment, verification, deflection)

Full YAML entries with references (Fossen, ITTC, Hoerner, Abbott & von Doenhoff): `docs/equations/equation_register.yaml`.

---

*This README describes every file currently in `verification/` and how each file relates to production code, equations, data, and tests. Update it when a notebook is added or a cell’s purpose changes.*
