"""CAD / Fusion / STEP / simulation exporters — SRDS 3.11–3.12."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from auv_fin_design.domain.airfoil.naca import generate_naca4_coordinates
from auv_fin_design.domain.manufacturing.stl_export import export_fin_stl

if TYPE_CHECKING:
    from auv_fin_design.application.pipeline import DesignResult


def _naca_code(airfoil_name: str) -> str:
    digits = "".join(ch for ch in airfoil_name if ch.isdigit())
    return digits[:4] if len(digits) >= 4 else "0018"


def export_fusion360_parameters(result: DesignResult, path: Path, *, shaft_diameter_m: float = 0.006) -> Path:
    """Fusion 360 user-parameter JSON for parametric fin rebuild."""
    g = result.geometry
    payload = {
        "units": "mm",
        "parameters": {
            "span_mm": g.span * 1000.0,
            "root_chord_mm": g.root_chord * 1000.0,
            "tip_chord_mm": g.tip_chord * 1000.0,
            "taper_ratio": g.taper_ratio,
            "aspect_ratio": g.aspect_ratio,
            "sweep_deg": g.sweep_deg,
            "thickness_ratio": g.thickness_ratio,
            "mac_mm": g.mac * 1000.0,
            "shaft_diameter_mm": shaft_diameter_m * 1000.0,
            "shaft_station_pct_mac": 25.0,
            "airfoil": result.airfoil_name,
            "material": result.material_name,
            "lever_arm_mm": result.allocation.lever_arm * 1000.0,
        },
        "notes": [
            "Import as User Parameters in Fusion 360",
            "Loft NACA root/tip sections; shaft bore at 25% MAC",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def export_step_ap203_approx(result: DesignResult, path: Path) -> Path:
    """Minimal ASCII STEP with polyline airfoil wire (not full B-rep solid).

    Full OpenCascade/CadQuery BREP is optional; this gives a valid STEP wire
    for CAD import while STL remains the manufacturable mesh.
    """
    code = _naca_code(result.airfoil_name)
    coords, _ = generate_naca4_coordinates(code, n_points=41)
    cr = result.geometry.root_chord
    points = [(x * cr, y * cr, 0.0) for x, y in coords]
    # Build simple STEP with CARTESIAN_POINT entities
    lines = [
        "ISO-10303-21;",
        "HEADER;",
        "FILE_DESCRIPTION(('AUV Fin root airfoil wire'),'2;1');",
        f"FILE_NAME('{path.name}','',('FinDesigner'),(''),'','','');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));",
        "ENDSEC;",
        "DATA;",
    ]
    eid = 1
    point_ids = []
    for x, y, z in points:
        lines.append(
            f"#{eid}=CARTESIAN_POINT('',({x:.6e},{y:.6e},{z:.6e}));"
        )
        point_ids.append(eid)
        eid += 1
    # Polyline
    refs = ",".join(f"#{i}" for i in point_ids)
    lines.append(f"#{eid}=POLYLINE('fin_root_section',({refs}));")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def export_gazebo_sdf(result: DesignResult, path: Path) -> Path:
    """Minimal Gazebo SDF link for one fin (visual mesh reference)."""
    g = result.geometry
    mass = max(g.mass_est, 1e-4)
    sdf = f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="auv_fin">
    <link name="fin_link">
      <inertial>
        <mass>{mass:.6f}</mass>
        <inertia>
          <ixx>{mass * g.span**2 / 12:.6e}</ixx>
          <iyy>{mass * g.mac**2 / 12:.6e}</iyy>
          <izz>{mass * (g.span**2 + g.mac**2) / 12:.6e}</izz>
          <ixy>0</ixy><ixz>0</ixz><iyz>0</iyz>
        </inertia>
      </inertial>
      <visual name="fin_visual">
        <geometry><mesh><uri>model://auv_fin/meshes/fin.stl</uri></mesh></geometry>
      </visual>
      <collision name="fin_collision">
        <geometry>
          <box>
            <size>{g.mac:.4f} {g.root_thickness:.4f} {g.span:.4f}</size>
          </box>
        </geometry>
      </collision>
    </link>
    <joint name="fin_hinge" type="revolute">
      <parent>base_link</parent>
      <child>fin_link</child>
      <axis><xyz>0 1 0</xyz><limit>
        <lower>{-result.aero.alpha_deg * 3.14159/180:.4f}</lower>
        <upper>{result.aero.alpha_deg * 3.14159/180:.4f}</upper>
      </limit></axis>
    </joint>
  </model>
</sdf>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sdf, encoding="utf-8")
    return path


def export_ros2_description(result: DesignResult, path: Path) -> Path:
    """URDF snippet for ROS 2 fin joint."""
    g = result.geometry
    urdf = f"""<?xml version="1.0"?>
<robot name="auv_fin">
  <link name="base_link"/>
  <link name="fin_link">
    <visual>
      <geometry><box size="{g.mac:.4f} {g.root_thickness:.4f} {g.span:.4f}"/></geometry>
    </visual>
    <inertial>
      <mass value="{g.mass_est:.6f}"/>
      <inertia ixx="1e-4" ixy="0" ixz="0" iyy="1e-4" iyz="0" izz="1e-4"/>
    </inertial>
  </link>
  <joint name="fin_hinge" type="revolute">
    <parent link="base_link"/>
    <child link="fin_link"/>
    <origin xyz="{result.allocation.lever_arm:.4f} 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.785" upper="0.785" effort="10" velocity="1.0"/>
  </joint>
</robot>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(urdf, encoding="utf-8")
    return path


def export_simulation_bundle(result: DesignResult, out_dir: Path) -> dict[str, Path]:
    """Write STL + Gazebo SDF + ROS2 URDF + hydro params JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    code = _naca_code(result.airfoil_name)
    paths = {
        "stl": export_fin_stl(result.geometry, out_dir / "fin.stl", naca_code=code),
        "gazebo_sdf": export_gazebo_sdf(result, out_dir / "fin.sdf"),
        "ros2_urdf": export_ros2_description(result, out_dir / "fin.urdf"),
        "step": export_step_ap203_approx(result, out_dir / "fin_root_wire.step"),
        "fusion360": export_fusion360_parameters(result, out_dir / "fusion360_parameters.json"),
    }
    hydro = {
        "CL": result.aero.cl,
        "CD": result.aero.cd_total,
        "Cm": result.aero.cm,
        "alpha_deg": result.aero.alpha_deg,
        "lift_N": result.allocation.lift_per_fin,
        "lever_arm_m": result.allocation.lever_arm,
        "M_design_Nm": result.control_req.M_design,
        "dynamic_pressure_Pa": result.hydro.dynamic_pressure,
    }
    hp = out_dir / "hydro_params.json"
    hp.write_text(json.dumps(hydro, indent=2), encoding="utf-8")
    paths["hydro_params"] = hp
    return paths
