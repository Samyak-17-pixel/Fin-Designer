# Equation Register — Review Status

Source: `docs/equations/equation_register.yaml`

## Implementation status (re-verified)

The V1 product now covers the Chapter 1 workflow end-to-end:

- All Ch.1 user inputs (including **Material** and **Maximum speed**)
- Hydrodynamic validation module (3.7)
- Structure with shear/torsion/von Mises
- Servo with shaft FoS / bearing / actuation time
- Sensitivity ±10%
- Optional NSGA-II
- Manufacturing recommendations
- STL + STEP wire + Fusion 360 params + Gazebo SDF + ROS 2 URDF
- JSON / TXT / HTML engineering reports
- **Dynamic 3D CoP** (strip Cp integration, EQ-COP-*) with QC/Cm–CL verification
- **Max fin deflection** for specified maneuver (α=δ)

## Known packaging note

Default `max_span_over_diameter` is **0.55** so the golden vehicle (T=30 s) passes.
At 0.45×D the solver correctly reports a packaging violation.
