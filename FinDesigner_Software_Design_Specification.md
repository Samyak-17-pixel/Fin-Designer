# Chapter 1 – Project Overview

## Your Role

You are a senior software architect, marine hydrodynamics engineer, naval architect, robotics engineer, and full-stack developer.

Your responsibility is to design and develop a professional engineering software application for automatic sizing and optimization of control fins for torpedo-shaped Autonomous Underwater Vehicles (AUVs).

This is NOT a geometry generator.

This is NOT a CAD plugin.

This is NOT a calculator.

This is a complete engineering design platform that uses marine vehicle dynamics, hydrodynamic theory, optimization, structural analysis, and airfoil performance data to automatically design the best possible control fin for an underwater vehicle.

Every engineering decision must be physics-based.

Never hardcode dimensions.

Never ask the user for fin dimensions.

The software must derive them automatically.

---

# Project Name

Torpedo AUV Fin Design & Optimization Suite

---

# Vision

The objective is to build a software platform that allows an engineer to input only the vehicle characteristics and maneuvering requirements.

The software must automatically determine

• Required control authority

• Required fin lift

• Required fin area

• Optimal fin geometry

• Best airfoil

• Required servo characteristics

• Structural adequacy

• Manufacturing feasibility

The final output should be an optimized fin that satisfies all engineering constraints while minimizing hydrodynamic drag.

The software should emulate the workflow of a professional marine vehicle design engineer.

---

# Primary Goal

The primary objective is

"Automatically design the optimal control fin for a torpedo-shaped AUV using first-principles engineering and validated empirical hydrodynamic models."

The software should require as few user inputs as possible.

Everything else must be computed.

---

# Philosophy

The software should always follow these principles.

## Physics First

Never rely on arbitrary constants if a physical equation exists.

Use governing equations whenever possible.

Only use empirical correlations where first-principles solutions are impractical.

---

## Automation

The engineer should never manually size a fin.

The software should determine

• fin area

• span

• root chord

• tip chord

• sweep

• taper

• thickness

• airfoil

• shaft location

automatically.

---

## Modularity

Every engineering calculation must exist as an independent module.

For example

Vehicle Model

Hydrodynamic Estimator

Control Solver

Geometry Generator

Structural Solver

Servo Solver

Optimization Engine

CAD Generator

Each module should operate independently.

No module should contain duplicated logic.

---

## Extensibility

The software should be written so that future improvements can be added without modifying existing code.

Future additions may include

CFD

Fossen model

Machine learning

Genetic optimization

Multi-fin optimization

Different hull shapes

Different materials

Different airfoil databases

Therefore every subsystem must be modular.

---

## Transparency

Every calculated result should be traceable.

For every output the software should explain

Which equations were used

Which assumptions were made

Which empirical correlations were used

Intermediate calculations

Final values

The engineer must never receive a "black-box" answer.

---

# Scope

The first version of the software should support

• Torpedo-shaped AUVs

• Uniform cylindrical hull approximation

• Circular cross-section

• X-fin configuration

• PLA manufactured fins

• Freshwater and seawater

• Low-speed underwater vehicles

Future versions will support

Multiple hull geometries

Blended hulls

Biomimetic fins

Hybrid control surfaces

---

# Intended Users

The software is intended for

Marine robotics researchers

Naval architects

Ocean engineers

Students

Competition teams

Research laboratories

Defense researchers

Engineers designing underwater vehicles

The software should therefore be professional enough for research while remaining easy for students to use.

---

# User Experience

The user should never feel overwhelmed.

Instead of asking for dozens of engineering parameters,

the software should ask only for meaningful design requirements.

Example

Vehicle length

Vehicle diameter

Vehicle mass

Cruise speed

Maximum speed

Desired turning radius

Desired turning time

Servo torque

Servo shaft diameter

Material

Water type

Everything else must be computed automatically.

---

# Design Philosophy

The software should answer the following engineering question.

"What is the smallest, lowest-drag fin that can safely produce the required maneuver?"

This single philosophy should drive every optimization.

---

# Optimization Objective

The optimization objective is

Minimize total hydrodynamic drag

Subject to

Required control authority

Structural safety

Servo limitations

Manufacturing constraints

Stall avoidance

Geometric constraints

No optimization should violate any engineering constraint.

---

# Engineering Workflow

The software must internally follow this sequence

Mission Requirements

↓

Vehicle Model

↓

Hydrodynamic Estimator

↓

Required Control Moment

↓

Required Fin Lift

↓

Required Fin Area

↓

Generate Candidate Geometries

↓

Automatic Airfoil Selection

↓

Hydrodynamic Validation

↓

Structural Validation

↓

Servo Validation

↓

Optimization

↓

Final Geometry

↓

CAD Export

↓

Simulation Export

↓

Engineering Report

This workflow must never be bypassed.

---

# Software Outputs

The software should produce

Optimized fin dimensions

Airfoil selection

Control authority report

Hydrodynamic analysis

Structural analysis

Servo analysis

Manufacturing recommendations

Fusion 360 parameters

STEP export

STL export

Simulation files

Engineering report

Optimization history

Sensitivity analysis

No output should be given without validation.

---

# Non-Goals

The software is NOT intended to

Replace CFD

Replace finite element analysis

Replace towing tank experiments

Replace high-fidelity dynamic simulation

Instead, it should produce an accurate first-principles engineering design suitable for prototyping and research.

---

# Development Standards

The codebase should follow

Object-oriented programming

Type hints

Comprehensive documentation

Modular architecture

Unit testing

Meaningful variable names

No duplicated code

No magic numbers

Every equation referenced.

---

# End Goal

At the completion of this project, the software should function as a professional engineering design assistant capable of generating optimized control fin designs for torpedo-shaped autonomous underwater vehicles with minimal user input while maintaining complete engineering transparency and traceability.

Every design produced by the software should be physically justifiable, structurally safe, manufacturable, and directly usable for CAD modeling, simulation, and real-world fabrication.


# Chapter 2 – Engineering Background & Design Methodology

## Your Role

Before implementing any software, you must fully understand the engineering problem that this application is solving.

This chapter explains the theoretical background, engineering decisions, assumptions, limitations, and rationale behind the software architecture.

Do not write code while processing this chapter.

The purpose of this chapter is to establish the engineering foundation upon which the entire software will be built.

Every future module must follow the philosophy established here.

---

# 2.1 Problem Statement

The objective of this software is to automatically design the optimal control fin for a torpedo-shaped Autonomous Underwater Vehicle (AUV).

Unlike aircraft wings or ship rudders, an AUV control fin must satisfy several competing requirements simultaneously:

• Generate sufficient control force for maneuvering.

• Produce minimal hydrodynamic drag.

• Avoid stall.

• Be structurally strong enough to withstand hydrodynamic loading.

• Be compatible with available servos.

• Be manufacturable using common fabrication methods (3D printing with PLA in Version 1).

Most existing fin sizing approaches either rely heavily on designer experience or require computationally expensive CFD simulations.

This software aims to bridge that gap by using validated engineering equations and empirical hydrodynamic correlations to produce a practical first-pass fin design.

---

# 2.2 Why This Software Exists

Designing AUV control fins is usually an iterative and time-consuming process.

Engineers often:

Guess fin dimensions

↓

Create CAD

↓

Run CFD

↓

Modify geometry

↓

Repeat

This process can take several days or weeks.

The purpose of this software is to automate the early-stage engineering design process.

The software should provide an optimized fin geometry that is physically justifiable and suitable for prototyping before CFD or experimental validation.

---

# 2.3 Overall Design Philosophy

The software follows one central engineering philosophy:

"The fin should be only as large as necessary to safely perform the required maneuver."

This philosophy minimizes drag while maintaining adequate maneuverability.

The software must never intentionally oversize the fin.

Likewise, it must never sacrifice maneuverability to reduce drag.

The optimization should always satisfy every engineering constraint before attempting to reduce drag.

---

# 2.4 Why Control-Authority-Based Design?

Several fin sizing approaches exist.

## Method 1 – Empirical Scaling

Example:

Fin area = 8% of hull projected area

Advantages

Simple

Very fast

Disadvantages

Not physics-based

Cannot adapt to different missions

Cannot optimize

Not suitable for automation

Not suitable for research

Rejected.

---

## Method 2 – Static Stability Based

Uses restoring moments to size the fins.

Advantages

Useful for passive stability.

Disadvantages

Does not guarantee maneuverability.

Cannot determine whether the vehicle can achieve a required turn.

Rejected.

---

## Method 3 – Control Authority Based

Determine

Required maneuver

↓

Required vehicle moment

↓

Required fin lift

↓

Required fin geometry

Advantages

Physics-based

Mission-dependent

Suitable for optimization

Widely accepted

Expandable

Chosen for this software.

---

# 2.5 Why Optimize for Minimum Drag?

Control fins continuously generate drag.

Oversized fins reduce endurance.

Increase power consumption.

Decrease efficiency.

Increase actuator loads.

Therefore the optimization objective becomes

Minimize hydrodynamic drag

Subject to

Control authority

Structural safety

Servo capability

Manufacturability

This produces the smallest fin capable of performing the required mission.

---

# 2.6 Why a Uniform Cylinder Model?

A real AUV consists of

Payload section

Electronics section

Nose

Tail cone

Propeller

Control fins

Modeling all of these accurately requires CFD or experimental coefficients.

Such information is unavailable during early-stage design.

Instead the vehicle is approximated as

A uniform circular cylinder.

Advantages

Simple

Analytical

Widely used

Reasonably accurate for preliminary design

Provides all required geometric quantities automatically.

Limitations

Does not capture local flow separation.

Does not model appendages.

Does not model nose/tail effects.

These limitations are acceptable for Version 1.

Future versions may replace this with a complete Fossen-based vehicle model.

---

# 2.7 Hydrodynamic Modeling Philosophy

Whenever possible

Use first-principles physics.

Only when analytical solutions are unavailable

Use empirical hydrodynamic correlations.

Examples

Geometry

Analytical

Moments of inertia

Analytical

Lift

Analytical

Drag

Airfoil database

Added mass

Empirical

Hydrodynamic damping

Empirical

Never invent empirical coefficients.

Every empirical equation should reference established marine hydrodynamics literature.

---

# 2.8 Airfoil Philosophy

The software uses real airfoil performance data instead of simplified lift-curve approximations.

Version 1 supports

NACA0012

NACA0015

NACA0018

Each airfoil contains

Coordinates

Lift coefficient

Drag coefficient

Moment coefficient

Transition locations

Stall information

These data are obtained from XFOIL.

The software should automatically interpolate between Reynolds numbers.

The user should never manually enter lift coefficients.

---

# 2.9 Why Use XFOIL Data?

Simple equations such as

CL = 2πα

become inaccurate

near stall

at low Reynolds numbers

for finite thickness airfoils

Instead

the software should use experimentally and numerically validated XFOIL polar data.

Advantages

Higher accuracy

Automatic stall prediction

Automatic drag estimation

Airfoil comparison

Suitable for optimization

---

# 2.10 Initial Area Estimation Philosophy

The lift equation requires CL.

However CL is unknown until

Airfoil

Reynolds number

Angle of attack

have been determined.

Therefore

Begin with a reasonable initial estimate.

Compute geometry.

Determine Reynolds number.

Select airfoil.

Obtain actual CL.

Recompute fin area.

Repeat until convergence.

This iterative process ensures consistency between geometry and hydrodynamic performance.

---

# 2.11 Structural Design Philosophy

Every fin behaves as a cantilever beam.

Hydrodynamic lift creates distributed loading.

The highest stresses occur near the root.

Therefore the structural analysis should evaluate

Root bending stress

Tip deflection

Factor of safety

Material limits

Version 1 assumes isotropic PLA.

Future versions may include

Carbon fiber

Aluminum

Composite laminates

Titanium

---

# 2.12 Servo Design Philosophy

The servo is part of the engineering design.

It is not merely a component check.

The software should determine

Hydrodynamic hinge moment

Required servo torque

Optimal shaft diameter

Optimal shaft location along the chord

Safety factor

The hinge location should minimize servo torque while maintaining adequate control authority and structural integrity.

The user provides

Servo torque

Servo shaft diameter

The software determines whether those values are adequate.

If not

recommend

Larger servo

Different shaft diameter

Different hinge location

Modified fin geometry

---

# 2.13 Optimization Philosophy

Optimization occurs only after a candidate design satisfies every engineering requirement.

Invalid designs should never participate in optimization.

Constraints include

Control authority

No stall

Servo capability

Structural safety

Printability

Geometry limits

Only feasible designs are optimized.

The optimization objective is

Minimum total drag.

---

# 2.14 Sensitivity Analysis

A good engineering design should remain functional under moderate changes in operating conditions.

Therefore every final design should be evaluated for

Speed variation

Mass variation

Water density variation

Turning radius variation

Servo tolerance

The software should report how these changes affect

Control authority

Required fin deflection

Servo torque

Factor of safety

This analysis provides confidence in the robustness of the design.

---

# 2.15 Engineering Assumptions

Version 1 assumes

• Low-speed incompressible flow.

• Constant water density.

• Constant water viscosity.

• No free-surface effects.

• No cavitation.

• No biofouling.

• No ocean currents.

• Symmetric flow.

• Uniform cylindrical hull.

• Identical fins.

• Identical servos.

• Steady maneuvering.

These assumptions significantly simplify the mathematics while remaining appropriate for preliminary engineering design.

---

# 2.16 Limitations

This software is intended for preliminary engineering design.

It should not replace

CFD

Finite Element Analysis

Towing tank experiments

Sea trials

The generated fin should be considered a highly optimized first-pass design suitable for CAD, simulation, prototyping, and further validation.

---

# 2.17 Future Expansion

The software architecture should allow future implementation of

Fossen 6-DOF dynamics

CFD coupling

Automatic OpenFOAM analysis

Finite element analysis

Genetic algorithms

Multi-objective optimization

Machine learning surrogate models

Composite material libraries

Additional hull geometries

Biomimetic fins

Adaptive control surfaces

No architectural decisions in Version 1 should prevent these future capabilities.

---

# Rules for the AI Agent

While implementing future chapters, always follow these principles:

1. Prefer first-principles physics over heuristics whenever feasible.
2. Use documented empirical correlations only when analytical solutions are unavailable.
3. Never invent coefficients or constants; cite established marine hydrodynamics references.
4. Treat optimization as a constrained engineering problem: only optimize among designs that already satisfy all safety and performance requirements.
5. Maintain complete traceability so every output can be linked back to the governing equations and assumptions.
6. Design every module to be independent, extensible, and reusable, avoiding duplicated logic or hidden dependencies.
7. Whenever an approximation is introduced, document why it is appropriate for Version 1 and identify where a higher-fidelity model could replace it in future versions.


# Chapter 3.1 – Vehicle Mathematical Model

## Objective

Develop the complete mathematical representation of the torpedo-shaped Autonomous Underwater Vehicle (AUV).

This model forms the foundation for every subsequent module in the software.

Every module that computes hydrodynamics, control forces, optimization, structural loads, and fin sizing will use this model.

Do not simplify the mathematics unless explicitly stated.

Every parameter must have

• Symbol

• SI Units

• Definition

• Physical meaning

• Valid range

• Source of calculation

---

# 3.1.1 Coordinate Systems

The software shall define four coordinate systems.

## Earth Fixed Frame (NED)

Origin

User defined.

Axes

X → North

Y → East

Z → Down

Purpose

Navigation.

Trajectory generation.

Simulator export.

---

## Body Fixed Frame

Origin

Vehicle Center of Gravity.

Axes

+x → Forward

+y → Starboard

+z → Down

This is the primary frame used by the software.

All forces and moments shall be computed in this frame.

---

## Fin Coordinate Frame

Each fin shall have its own local coordinate system.

Origin

Root leading edge.

Axes

x → Chord

y → Span

z → Normal

This frame is required for

Airfoil calculations

Pressure distribution

Lift

Drag

Servo hinge calculations

---

## Flow Coordinate Frame

Aligned with incoming water velocity.

Used for

Angle of attack

Lift coefficient

Drag coefficient

---

# 3.1.2 Vehicle Geometry

Version 1 assumes

Uniform circular cylinder.

Inputs

Vehicle Length

Symbol

L

Units

m

Constraint

L > 0

---

Vehicle Diameter

Symbol

D

Units

m

Constraint

D > 0

---

Vehicle Radius

Automatically compute

R = D / 2

---

Cross-sectional Area

A = πR²

---

Wetted Surface Area

Cylinder only

Sw = πDL

---

Frontal Area

Af = πR²

---

Vehicle Volume

V = πR²L

---

Displaced Water Mass

Mw = ρV

---

Buoyant Force

Fb = ρgV

---

Vehicle Density

ρvehicle = m / V

Automatically compare against water density.

---

# 3.1.3 Water Properties

User selects

Freshwater

or

Seawater

Software automatically assigns

Density

Dynamic viscosity

Kinematic viscosity

Gravity

Future versions should support custom fluids.

---

# 3.1.4 Vehicle Mass

User Input

m

kg

Must satisfy

m > 0

---

Weight Force

W = mg

Direction

Positive body Z

---

# 3.1.5 Center of Gravity

Version 1

Assume

CG

Located at geometric center.

Coordinates

(L/2,0,0)

Future versions

Allow arbitrary CG.

---

# 3.1.6 Center of Buoyancy

Version 1

Uniform cylinder

CB

equals

CG

Therefore

No restoring moment.

Future versions

Independent CB.

---

# 3.1.7 Moments of Inertia

Assume uniform solid cylinder.

Roll

Ix

= 1/2 mR²

Pitch

Iy

= (1/12)m(3R²+L²)

Yaw

Iz

= (1/12)m(3R²+L²)

Cross products

Zero.

---

Store

Complete inertia matrix.

Future versions

Support imported inertia tensor.

---

# 3.1.8 Fin Geometry Locations

Inputs

Number of fins

Configuration

Tail distance

Software computes

Root coordinates

Tip coordinates

Lever arm

Fin orientation

for every fin.

Supported

X

+

Future

V-tail

Custom

---

# 3.1.9 Servo Locations

Each fin possesses

Servo axis

Shaft diameter

Maximum servo torque

Servo horn length (optional)

Servo efficiency

Default

100%

Future versions

Allow efficiency losses.

---

# 3.1.10 Vehicle States

Store

Position

Velocity

Acceleration

Orientation

Angular velocity

Angular acceleration

State Vector

η

contains

x

y

z

roll

pitch

yaw

Velocity Vector

ν

contains

u

v

w

p

q

r

Acceleration

ν̇

contains

u̇

v̇

ẇ

ṗ

q̇

ṙ

---

# 3.1.11 Operating Conditions

User Inputs

Cruise speed

Maximum speed

Desired turning radius

Desired turning time

Water type

Vehicle depth

Version 1

Assume

Constant speed

Constant depth

Steady maneuver

---

# 3.1.12 Derived Quantities

Automatically compute

Dynamic pressure

q = ½ρV²

Vehicle slenderness ratio

λ = L/D

Vehicle aspect ratio

Equivalent hydraulic diameter

Reference length

Reference area

Reference volume

These quantities are reused throughout the software.

---

# 3.1.13 Engineering Assumptions

The vehicle model assumes

Rigid body

Uniform cylinder

Symmetric geometry

No appendages

No waves

No currents

No cavitation

No compressibility

No free surface

Low-speed incompressible flow

These assumptions simplify preliminary engineering design.

---

# 3.1.14 Validation Checks

Before proceeding

Software must verify

Length > 0

Diameter > 0

Mass > 0

Cruise speed > 0

Turning radius > 0

Turning time > 0

Vehicle density physically reasonable

Positive buoyancy warning

Negative buoyancy warning

Neutral buoyancy indication

Any invalid input shall prevent further calculations.

---

# 3.1.15 Outputs

Vehicle model module shall output

Radius

Cross-sectional area

Frontal area

Wetted area

Volume

Weight

Buoyant force

Net buoyancy

CG

CB

Moments of inertia

Reference dimensions

Reference areas

Dynamic pressure

Vehicle state object

All outputs shall be accessible to every subsequent module.

---

# Rules for the AI Agent

1. Never duplicate geometry calculations in downstream modules. This module is the single source of truth for all vehicle properties.

2. Store all values in SI units internally, regardless of user display preferences.

3. Validate every user input before performing calculations.

4. Keep the vehicle model independent of hydrodynamic models so that future hull geometries can replace the cylindrical approximation without affecting downstream modules.

5. Every output should be represented as a strongly typed data structure or class rather than loose variables.

6. Document every equation with its variable definitions, assumptions, and applicable range.

7. Design the implementation so that future versions can extend the vehicle model to arbitrary hull geometries without requiring changes to the control, optimization, or structural modules.


# Chapter 3.2 – Hydrodynamic Estimator

## Objective

Develop the complete hydrodynamic model of the torpedo-shaped AUV.

This module transforms the geometric VehicleModel into a HydrodynamicModel by estimating all hydrodynamic properties required for maneuvering analysis and fin sizing.

Version 1 shall use validated empirical correlations suitable for preliminary engineering design.

The module shall NOT require CFD.

The module shall be independent of the optimization engine.

It shall receive a VehicleModel object as input and produce a HydrodynamicModel object as output.

---

# Inputs

Receive

VehicleModel

containing

• Length

• Diameter

• Radius

• Volume

• Wetted Area

• Frontal Area

• Vehicle Mass

• Moments of Inertia

• Cruise Speed

• Maximum Speed

• Water Properties

No individual variables should be passed separately.

---

# Outputs

Produce a HydrodynamicModel object containing

• Reynolds Number

• Dynamic Pressure

• Added Mass Matrix

• Added Inertia Matrix

• Linear Damping Matrix

• Quadratic Damping Matrix

• Reference Areas

• Reference Lengths

• Hydrodynamic Coefficients

• Flow Regime Information

All downstream modules shall use this object.

---

# 3.2.1 Water Properties

Obtain from VehicleModel

Water Density

ρ

Dynamic Viscosity

μ

Kinematic Viscosity

ν

Gravity

g

Support

Freshwater

Seawater

Future

Custom Fluid

---

# 3.2.2 Reynolds Number

Compute Reynolds number using

Reference Length = Hull Length

Re = (V × L) / ν

Compute

Cruise Reynolds Number

Maximum Reynolds Number

Store both.

Also compute Reynolds number based on

Hull Diameter

This is useful for empirical drag correlations.

---

# 3.2.3 Flow Regime

Automatically classify

Laminar

Transitional

Turbulent

based on Reynolds number.

Store

FlowRegime

This information is later used for

Skin friction

Drag estimation

Airfoil interpolation

Warnings

---

# 3.2.4 Dynamic Pressure

Compute

q = ½ρV²

Store

Cruise Dynamic Pressure

Maximum Dynamic Pressure

This quantity will be reused throughout the software.

Never recompute elsewhere.

---

# 3.2.5 Reference Quantities

Compute

Reference Area

Hull Frontal Area

Reference Length

Hull Length

Characteristic Diameter

Hull Diameter

Reference Volume

Hull Volume

These become standard reference quantities for every later calculation.

---

# 3.2.6 Added Mass

Purpose

Estimate the apparent increase in inertia due to accelerated surrounding water.

Version 1

Estimate

Surge Added Mass

Sway Added Mass

Heave Added Mass

Roll Added Inertia

Pitch Added Inertia

Yaw Added Inertia

using empirical cylinder correlations.

The implementation must be based on published marine hydrodynamics references.

Do NOT invent coefficients.

Store

Complete 6×6 Added Mass Matrix

Even if some values are zero.

Future versions

Replace empirical estimates with

CFD

Experimental coefficients

Fossen coefficients

without changing downstream modules.

---

# 3.2.7 Linear Hydrodynamic Damping

Estimate

Surge

Sway

Heave

Roll

Pitch

Yaw

Linear damping coefficients

using slender-body approximations.

Store

6×6 Linear Damping Matrix.

---

# 3.2.8 Quadratic Hydrodynamic Damping

Estimate

Quadratic drag effects

for

Surge

Sway

Heave

Roll

Pitch

Yaw

using empirical marine vehicle correlations.

Store

6×6 Quadratic Damping Matrix.

Quadratic damping dominates underwater maneuvering.

Document this assumption.

---

# 3.2.9 Skin Friction

Estimate

Skin Friction Coefficient

using accepted turbulent flat-plate correlations.

Version 1 should support

ITTC-1957

Future versions

Allow multiple methods

Schlichting

Prandtl

Granville

Compute

Skin Friction Drag

using

Wetted Area

Dynamic Pressure

Skin Friction Coefficient

Store separately from pressure drag.

---

# 3.2.10 Form Drag

Estimate pressure drag

using

Cylinder drag correlations

based on

Reynolds Number

Slenderness Ratio

Store

Pressure Drag

Pressure Drag Coefficient

---

# 3.2.11 Total Hull Drag

Compute

Skin Friction Drag

+

Pressure Drag

=

Total Hull Drag

This drag estimate is not directly used for fin sizing.

It is included for

Mission analysis

Power estimation

Future optimization

Engineering reports.

---

# 3.2.12 Dynamic Pressure Distribution

Approximate

Local flow velocity

at

Fin location.

Version 1

Assume

Uniform inflow.

Future versions

Tail wake correction

Boundary layer correction

Propeller slipstream

---

# 3.2.13 Wake Fraction

Version 1

Assume

Wake Fraction = 0

Document

Reason

Future versions

Empirical wake models.

---

# 3.2.14 Blockage Effects

Version 1

Neglect

Hull-fin interference.

Future versions

Correction factors.

---

# 3.2.15 Cavitation Check

Estimate

Cavitation Number

If operating conditions indicate cavitation risk

Issue warning.

Version 1

Only warning.

No redesign.

---

# 3.2.16 Flow Validity

Warn if

Reynolds Number

outside

available airfoil database.

Warn if

Empirical correlations

used outside recommended ranges.

Never silently extrapolate.

---

# 3.2.17 Engineering Assumptions

Assume

Steady flow

Uniform inflow

Rigid body

No waves

No currents

No propeller effects

No free surface

No cavitation

No appendages

No hull-fin interference

Constant density

Constant viscosity

Low-speed incompressible flow

These assumptions are acceptable for preliminary fin sizing.

---

# 3.2.18 Validation

Check

Positive Reynolds Number

Positive Dynamic Pressure

Positive Added Mass

Positive Drag

Symmetric Matrices

Finite Values

Reject

NaN

Infinite

Negative physical quantities

---

# 3.2.19 Outputs

Return

HydrodynamicModel

containing

Reynolds Numbers

Dynamic Pressure

Added Mass Matrix

Added Inertia Matrix

Linear Damping Matrix

Quadratic Damping Matrix

Skin Friction

Pressure Drag

Total Hull Drag

Flow Regime

Reference Quantities

Validation Status

No downstream module shall independently compute these quantities.

---

# Rules for the AI Agent

1. Never hardcode hydrodynamic coefficients. Use published empirical correlations with documented sources.

2. Store all hydrodynamic properties in a strongly typed `HydrodynamicModel` class.

3. Keep the implementation modular so higher-fidelity models (CFD, Fossen coefficients, experiments) can replace empirical estimates without changing downstream interfaces.

4. Separate geometry from hydrodynamics. Geometry belongs only in the VehicleModel.

5. Compute every derived quantity once and reuse it throughout the application.

6. Validate every computed coefficient before passing it to later modules.

7. Record the literature source, equation number (if available), and validity range for every empirical correlation implemented.

8. If a correlation is applied outside its published validity range, issue a warning rather than silently continuing.

# Chapter 3.3 – Maneuvering Model & Required Control Authority

## Objective

This chapter computes the control moment required to achieve the maneuver specified by the user.

The user never specifies fin dimensions.

Instead, the user specifies the desired vehicle maneuver.

The software must determine the minimum control moment required to achieve that maneuver while accounting for vehicle inertia, added mass effects, and hydrodynamic damping.

The output of this chapter is the **Required Control Moment**.

This value drives the entire fin sizing process.

---

# Inputs

Receive

VehicleModel

HydrodynamicModel

Mission Requirements

containing

• Cruise Speed

• Maximum Speed

• Desired Turning Radius

• Desired Turn Establishment Time

• Vehicle Mass

• Moments of Inertia

• Added Mass Matrix

• Damping Matrices

---

# Outputs

Produce

ControlRequirementModel

containing

• Target Yaw Rate

• Angular Acceleration

• Inertial Moment

• Hydrodynamic Damping Moment

• Added Mass Moment

• Required Total Control Moment

• Safety Margin

This object becomes the input to the fin sizing module.

---

# 3.3.1 Mission Requirements

The software shall require

Cruise Speed

Vc

Desired Turning Radius

Rt

Desired Time to Establish Turn

Tturn

Optional

Maximum Roll Angle

Maximum Pitch Angle

Version 1

Only yaw maneuvering is required.

Future versions

Support

Roll

Pitch

Helical paths

3D trajectories

---

# 3.3.2 Turning Geometry

The vehicle follows a circular path.

Compute

Target Curvature

κ = 1 / Rt

Compute

Target Yaw Rate

r_target = Vc / Rt

Store

Target Yaw Rate

---

# 3.3.3 Angular Acceleration

The vehicle cannot instantaneously reach

Target Yaw Rate.

Assume

Linear ramp.

Compute

Yaw Angular Acceleration

r_dot

=

(Target Yaw Rate)

/ (Turn Establishment Time)

Store

Angular Acceleration

---

# 3.3.4 Vehicle Inertial Moment

Compute

Required inertial moment

using

Yaw Inertia

from VehicleModel.

Moment

=

Iz

×

r_dot

Store

Inertial Control Moment.

---

# 3.3.5 Added Mass Contribution

Accelerating water also requires torque.

Use

Added Yaw Inertia

from HydrodynamicModel.

Compute

Added Mass Moment

=

Added Yaw Inertia

×

r_dot

Store separately.

Never combine directly with vehicle inertia.

---

# 3.3.6 Hydrodynamic Damping Moment

At steady turning

the vehicle experiences hydrodynamic resistance.

Compute

Linear Damping Moment

using

Yaw Rate

Quadratic Damping Moment

using

Yaw Rate²

Total Damping Moment

=

Linear

+

Quadratic

Store

Hydrodynamic Resistance Moment.

---

# 3.3.7 Total Required Control Moment

The fins must overcome

Vehicle Inertia

+

Added Mass

+

Hydrodynamic Damping

Therefore

Required Control Moment

=

Inertial Moment

+

Added Mass Moment

+

Hydrodynamic Damping Moment

This is the governing design quantity.

Every later calculation depends on this value.

---

# 3.3.8 Control Margin

Real systems require reserve authority.

Introduce

Control Margin

Default

25%

User configurable

Total Required Moment

=

Required Moment

×

(1 + Margin)

Store

Design Control Moment.

This is the value used for fin sizing.

---

# 3.3.9 Maneuver Classification

Automatically classify

Gentle Turn

Moderate Turn

Aggressive Turn

based on

Turning Radius

Vehicle Length

Speed

Purpose

Engineering report

Warnings

Future optimization.

---

# 3.3.10 Dynamic Feasibility Check

Verify

Turning Radius

>

Minimum Physical Radius

Check

Yaw Rate

within practical limits.

Check

Angular Acceleration

within actuator capability.

If impossible

Generate

Engineering Warning

Do not continue optimization until user confirms.

---

# 3.3.11 Energy Estimate (Optional)

Estimate

Work required

to establish turn.

Estimate

Average control power.

These values are not used for fin sizing.

Include

Engineering Report only.

---

# 3.3.12 Sensitivity Analysis

Automatically evaluate

±10%

Vehicle Mass

±10%

Cruise Speed

±10%

Turning Radius

Determine

Change in Required Moment.

Store

Sensitivity Matrix.

Future

Spider plots.

---

# 3.3.13 Engineering Assumptions

Assume

Constant forward speed.

Planar yaw maneuver.

Small sideslip.

No current.

No waves.

No actuator delay.

Rigid vehicle.

Constant mass.

No payload shift.

Version 1

Neglect

Propeller side force.

Thruster asymmetry.

---

# 3.3.14 Validation

Verify

Cruise Speed > 0

Turning Radius > 0

Turning Time > 0

Required Moment > 0

Finite Values

No NaN

No Infinite Values

Reject invalid mission inputs.

---

# 3.3.15 Outputs

Return

ControlRequirementModel

containing

Mission Inputs

Target Curvature

Target Yaw Rate

Angular Acceleration

Vehicle Inertial Moment

Added Mass Moment

Hydrodynamic Damping Moment

Required Moment

Design Moment

Control Margin

Sensitivity Matrix

Validation Status

No later module shall independently compute the required maneuvering moment.

---

# Rules for the AI Agent

1. Never estimate fin size directly from turning radius. Always compute the required control moment first.

2. Keep inertial, added-mass, and damping contributions separate in the data model for traceability.

3. Store both the raw required moment and the design moment (with safety margin).

4. Ensure every intermediate quantity is available in the engineering report.

5. Make the maneuvering model independent of fin geometry so it can later support rudders, canards, vectored thrusters, or hybrid control systems.

6. Use SI units internally for all calculations.

7. Every equation must include variable definitions, units, assumptions, and literature references where applicable.

8. The output of this module is the engineering requirement—not a fin design.


# Chapter 3.4 – Control Allocation Module

## Objective

The purpose of this module is to translate the vehicle-level control requirements into individual fin loading requirements.

The Maneuvering Model computes the total control moment required by the vehicle.

However, the fins are the actual actuators.

This module determines

• How much lift each fin must generate

• How the control moment is distributed

• How the fin configuration affects effectiveness

• How actuator commands are mixed

This module separates vehicle dynamics from actuator geometry.

This makes the software independent of fin configuration.

---

# Inputs

Receive

VehicleModel

HydrodynamicModel

ControlRequirementModel

ConfigurationModel

ConfigurationModel contains

• Number of fins

• Fin orientation

• Fin positions

• Lever arms

• Fin mounting angles

---

# Outputs

Return

ControlAllocationModel

containing

Required Lift Per Fin

Required Normal Force

Required Lift Vector

Required Fin Moment

Control Allocation Matrix

Control Effectiveness Matrix

Fin Utilization

Available Redundancy

Validation Status

---

# 3.4.1 Supported Configurations

Version 1

Support

X Configuration

+

Configuration

Future

V Tail

Canards

Single Rudder

Twin Rudders

Custom Configuration

The software architecture shall allow adding configurations without modifying downstream modules.

---

# 3.4.2 Fin Geometry

Each fin shall contain

Root Position

Tip Position

Span Direction

Chord Direction

Normal Direction

Lever Arm

Sweep Angle

Dihedral

These values are stored inside

FinModel.

---

# 3.4.3 Control Axes

Version 1

Yaw only.

Future

Yaw

Pitch

Roll

Combined Maneuvers

The allocation matrix shall already support all three axes even if only yaw is currently active.

---

# 3.4.4 Control Allocation Matrix

Construct

Control Allocation Matrix

B

The matrix converts

Fin Lift

↓

Vehicle Moments

General form

Vehicle Moment

=

B × Fin Lift Vector

The implementation shall allow

Any number of fins.

Any fin orientation.

Future vectored thrusters.

---

# 3.4.5 X-Fin Mixing

For an X configuration

Each fin contributes simultaneously to

Yaw

Pitch

Roll

The software shall compute the contribution of each fin using

Its mounting angle

Lever arm

Lift direction

The software shall never assume

Equal contribution

unless mathematically justified.

---

# 3.4.6 Required Lift Distribution

Given

Required Vehicle Moment

Determine

Required Lift

for every fin.

Version 1

Symmetric loading.

Future

Optimization-based allocation.

---

# 3.4.7 Lever Arm Calculation

For every fin

Compute

Perpendicular distance

between

Vehicle CG

and

Center of Pressure

This becomes

Moment Arm

The software shall automatically update

Moment Arm

if fin geometry changes.

---

# 3.4.8 Center of Pressure

Initially

Assume

25%

Chord

Future

Pressure distribution from XFOIL.

The center of pressure should be recalculated after the final geometry converges.

---

# 3.4.9 Required Lift

For every fin

Compute

Lift

=

Required Moment

/

Effective Lever Arm

Adjusted

using

Allocation Matrix.

Store

Lift

Normal Force

Tangential Force

Moment Contribution

---

# 3.4.10 Control Effectiveness

Compute

Control Effectiveness

defined as

Vehicle Moment

generated

per unit lift.

Store

Control Effectiveness Matrix.

Future

Use

for controller design.

---

# 3.4.11 Actuator Utilization

Determine

Percentage utilization

of every fin.

Store

Maximum Utilization

Average Utilization

Unused Authority

Future

Fault tolerance.

---

# 3.4.12 Failure Analysis

Version 1

Optional.

Allow user to simulate

One failed fin.

Determine

Remaining control authority.

Generate warning if maneuver becomes impossible.

Future

Multiple failures.

---

# 3.4.13 Load Symmetry

Verify

Opposite fins

carry

equal

and

opposite

loads

where appropriate.

Warn if

Asymmetric loading

exists.

---

# 3.4.14 Validation

Verify

Allocation Matrix

invertible

Required Lift

positive

Finite

No NaN

No Infinite Values

No impossible actuator commands.

---

# 3.4.15 Outputs

Return

ControlAllocationModel

containing

Allocation Matrix

Required Lift Per Fin

Moment Arm

Center of Pressure

Control Effectiveness

Utilization

Validation Status

This object becomes

the direct input

to

Fin Sizing Module.

---

# Engineering Assumptions

Version 1

Assume

Rigid fins

Independent actuators

Perfect servo tracking

No backlash

No structural flexibility

Future versions

Include

Servo dynamics

Elastic fins

Hydraulic actuators

---

# Rules for the AI Agent

1. Never hardcode X-fin equations. Build the allocation matrix from fin geometry so any configuration can be supported.

2. The Control Allocation Module shall know nothing about fin size. It only distributes required forces.

3. Every fin shall be represented by a FinModel object containing geometry and orientation.

4. Keep the allocation matrix completely independent of optimization.

5. Design the module to support arbitrary actuator configurations in the future.

6. Every intermediate calculation shall be stored for reporting and debugging.

7. The output of this module is required lift and force distribution—not fin geometry.

8. Every transformation between vehicle moments and fin forces must be documented with equations, assumptions, and units.


# Chapter 3.5 – Initial Fin Sizing Module

## Objective

The objective of this module is to generate an initial fin geometry capable of producing the required lift calculated by the Control Allocation Module.

This is NOT the final fin design.

Instead, it is the first engineering estimate that will later be refined through:

• Airfoil selection
• Hydrodynamic validation
• Structural analysis
• Servo analysis
• Optimization

The output of this module is a CandidateFinGeometry.

---

# Inputs

Receive

VehicleModel

HydrodynamicModel

ControlAllocationModel

MaterialModel

ManufacturingConstraints

UserPreferences

The module shall NOT request additional user inputs.

---

# Outputs

Return

CandidateFinGeometry

containing

• Span
• Root Chord
• Tip Chord
• Mean Aerodynamic Chord
• Area
• Aspect Ratio
• Taper Ratio
• Sweep Angle
• Thickness
• Estimated Volume
• Estimated Mass
• Root Coordinates
• Tip Coordinates

---

# 3.5.1 Required Lift

Obtain

Required Lift Per Fin

from

ControlAllocationModel.

This is the design requirement.

Never modify this value.

---

# 3.5.2 Initial Lift Coefficient

The lift equation requires

CL

However

CL is unknown until

Airfoil

Reynolds Number

Angle of Attack

are known.

Therefore

Use an initial estimate.

Default

CL_initial = 0.5

The value shall be configurable.

Do not hardcode.

Document that this is only a starting point.

---

# 3.5.3 Dynamic Pressure

Obtain

Dynamic Pressure

from

HydrodynamicModel.

Never recompute.

---

# 3.5.4 Initial Fin Area

Compute

Required Planform Area

using

Lift Equation

L = ½ρV²SCL

Solve for

S

Store

Estimated Area

---

# 3.5.5 Aspect Ratio

Aspect Ratio determines

Lift efficiency

Induced drag

Structural stiffness

Version 1

Use a configurable default

Example

AR = 1.8

Do not hardcode.

Future versions

Allow optimization.

---

# 3.5.6 Span

Compute

Span

from

Area

Aspect Ratio

Span = √(Area × AR)

Store

Span

---

# 3.5.7 Mean Chord

Compute

Mean Chord

Area / Span

Store

Mean Chord

---

# 3.5.8 Taper Ratio

Version 1

Default

0.5

User configurable.

Future

Optimization Variable.

---

# 3.5.9 Root Chord

Compute

Root Chord

using

Area

Span

Taper Ratio

Store

Root Chord

---

# 3.5.10 Tip Chord

Tip Chord

=

Taper Ratio

×

Root Chord

Store

Tip Chord

---

# 3.5.11 Sweep Angle

Version 1

Default

10°

Configurable

Future

Optimization Variable.

Store

Leading Edge Sweep

Trailing Edge Sweep

Quarter Chord Sweep

---

# 3.5.12 Thickness

Version 1

Relative Thickness

20%

of Root Chord

This is only an initial estimate.

Later

airfoil selection

determines

actual thickness.

Store

Root Thickness

Tip Thickness

---

# 3.5.13 Mean Aerodynamic Chord

Compute

MAC

using standard trapezoidal wing equations.

Store

MAC

This value will later be used for

Reynolds Number

Servo Location

Center of Pressure

Structural Analysis

---

# 3.5.14 Fin Volume

Approximate

Volume

using

Planform Area

×

Average Thickness

Store

Estimated Volume

---

# 3.5.15 Fin Mass

Using

Material Density

Estimate

Mass

Store

Estimated Fin Mass

Future

Support

Internal infill estimation.

---

# 3.5.16 Center of Pressure

Temporary assumption

25%

Mean Aerodynamic Chord

This value will later be replaced

using

XFOIL pressure distribution.

---

# 3.5.17 Geometry Validation

Verify

Span > 0

Root Chord > Tip Chord

Positive Area

Positive Thickness

Aspect Ratio within limits

Generate warnings if

Extremely low AR

Extremely high AR

Excessive Sweep

Tiny Chord

Huge Span

---

# 3.5.18 Manufacturing Constraints

Verify

Minimum Printable Thickness

Minimum Root Thickness

Minimum Wall Thickness

Minimum Trailing Edge Thickness

Maximum Build Volume

Maximum Span

Maximum Chord

Version 1

PLA

Future

Different manufacturing methods.

---

# 3.5.19 Candidate Geometry

Create

CandidateFinGeometry

Object

Store

Geometry

Material

Mass

Center of Pressure

Validation Results

Unique Design ID

This object becomes the input

to

Airfoil Selection.

---

# Engineering Assumptions

Initial geometry assumes

Trapezoidal Planform

Straight Leading Edge

Straight Trailing Edge

Symmetric Airfoil

Constant Thickness Ratio

No Twist

No Washout

No Dihedral

Future versions

Support

Elliptical

Swept

Curved

Biomimetic

Winglets

---

# Rules for the AI Agent

1. This module creates only an initial candidate geometry. It must not attempt to optimize the design.

2. Never recompute lift or required moment. Those are fixed inputs from previous modules.

3. Every geometric parameter must be derived from the required lift and configurable design variables.

4. Store all geometry in a strongly typed CandidateFinGeometry object.

5. Avoid hardcoded engineering values. Defaults should be configurable and documented.

6. Validate manufacturability before passing the geometry downstream.

7. Every computed dimension shall include units and engineering meaning.

8. The output of this module is a physically reasonable starting point, not the final fin.



# Chapter 3.6 – Airfoil Selection & Hydrodynamic Performance Module

## Objective

The purpose of this module is to determine the most suitable airfoil for the candidate fin geometry and compute its true hydrodynamic performance.

Unlike conventional fin sizing methods, this software shall not rely on simplified lift-curve approximations.

Instead, it shall use a database of experimentally and numerically validated airfoil performance data generated using XFOIL.

The module shall

• Select the most appropriate airfoil

• Determine operating Reynolds number

• Interpolate lift and drag coefficients

• Compute stall margin

• Compute required angle of attack

• Iterate until the fin geometry converges

The output is an AerodynamicDesignModel.

---

# Inputs

Receive

VehicleModel

HydrodynamicModel

CandidateFinGeometry

AirfoilDatabase

DesignVariableManager

---

# Outputs

Return

AerodynamicDesignModel

containing

• Selected Airfoil

• Operating Reynolds Number

• Lift Coefficient

• Drag Coefficient

• Moment Coefficient

• Lift-to-Drag Ratio

• Required Angle of Attack

• Stall Margin

• Updated Fin Area

• Updated Geometry

• Convergence Status

---

# 3.6.1 Airfoil Database

The software shall maintain a local airfoil database.

Version 1

Support

NACA0012

NACA0015

NACA0018

Each airfoil folder contains

coordinates.dat

Re50000.csv

Re100000.csv

Re200000.csv

Re500000.csv

Re1000000.csv

Metadata shall be stored inside each file.

Never depend on filenames for engineering data.

---

# 3.6.2 Airfoil Data

Each Reynolds dataset contains

Angle of Attack

Lift Coefficient

Drag Coefficient

Pressure Drag

Moment Coefficient

Top Transition

Bottom Transition

Maximum CL/CD

Maximum Lift

Stall Angle

The parser shall automatically read all metadata.

---

# 3.6.3 Operating Reynolds Number

Compute Reynolds number

using

Mean Aerodynamic Chord

Re = V × MAC / ν

Compute

Cruise Reynolds Number

Maximum Speed Reynolds Number

Mission Reynolds Number (future)

---

# 3.6.4 Reynolds Interpolation

The operating Reynolds number will rarely exactly match a stored dataset.

The software shall interpolate

between

the two nearest Reynolds datasets.

Example

Re = 160,000

↓

Interpolate

between

100,000

and

200,000

Interpolation shall be smooth and monotonic.

Never simply choose the nearest Reynolds number.

---

# 3.6.5 Airfoil Ranking

Evaluate every available airfoil.

Metrics include

Maximum Lift

Lift-to-Drag Ratio

Operating Drag

Stall Margin

Thickness Ratio

Moment Coefficient

Manufacturing Suitability

Servo Requirements

Generate a weighted performance score.

Default weights

Lift-to-Drag Ratio

40%

Drag

25%

Stall Margin

15%

Thickness

10%

Moment

10%

Future versions shall allow user-defined weighting.

---

# 3.6.6 Initial Airfoil Selection

Select the airfoil with the highest weighted score.

Store

Selected Airfoil

Selection Score

Ranking of all candidates

Selection rationale

The engineering report shall explain why the airfoil was selected.

---

# 3.6.7 Required Lift Coefficient

Obtain

Required Lift

from

ControlAllocationModel.

Obtain

Dynamic Pressure

from

HydrodynamicModel.

Obtain

Current Area

from

CandidateFinGeometry.

Compute

Required Lift Coefficient

using

CL = L / (qS)

Store

Required CL

---

# 3.6.8 Required Angle of Attack

Using the selected airfoil polar

Determine

the angle of attack required to achieve

Required CL.

Interpolation shall occur

between angle-of-attack data points.

Never round to the nearest point.

Store

Operating Angle of Attack

---

# 3.6.9 Stall Margin

Determine

Stall Angle

from the airfoil database.

Compute

Remaining Stall Margin

Stall Margin = Stall Angle − Operating Angle

Generate warnings if

Margin < configurable threshold.

Default

5°

---

# 3.6.10 Lift and Drag

Interpolate

Lift Coefficient

Drag Coefficient

Moment Coefficient

at

Operating Angle of Attack.

Compute

Lift

Drag

Lift-to-Drag Ratio

These become the true hydrodynamic characteristics.

---

# 3.6.11 Geometry Update

The initial geometry assumed

CL_initial.

Now

Actual CL

is known.

Recompute

Required Area

using

Actual CL.

Update

Span

Root Chord

Tip Chord

Mean Aerodynamic Chord

Area

Thickness

Maintain

Aspect Ratio

Taper Ratio

unless optimization modifies them.

---

# 3.6.12 Convergence Loop

Repeat

Compute Reynolds Number

↓

Interpolate Airfoil Data

↓

Compute Actual CL

↓

Update Area

↓

Update Geometry

↓

Recompute Reynolds Number

Until

Area change < configurable tolerance.

Default

0.5%

or

Maximum iterations reached.

Store

Iteration History

---

# 3.6.13 Airfoil Suitability

Reject airfoils if

Required CL exceeds maximum CL

Stall margin insufficient

Thickness below manufacturing limit

Thickness exceeds geometric limit

Invalid Reynolds range

Generate explanation.

---

# 3.6.14 Pressure Distribution

Version 1

Approximate center of pressure

using XFOIL data if available.

Otherwise

Use

25% chord.

Store

Pressure Center

Future

Full pressure integration.

---

# 3.6.15 Flow Transition

Store

Top Transition

Bottom Transition

These values are not used in Version 1 calculations.

Include

Engineering Report.

Future

Boundary layer optimization.

---

# 3.6.16 Validation

Verify

Convergence achieved

Positive Lift

Positive Drag

Finite Coefficients

No NaN

No Infinite Values

Operating angle below stall

Airfoil database successfully loaded

Interpolation successful

---

# 3.6.17 Outputs

Return

AerodynamicDesignModel

containing

Selected Airfoil

Operating Reynolds Number

Operating Angle of Attack

Lift Coefficient

Drag Coefficient

Moment Coefficient

Lift-to-Drag Ratio

Stall Margin

Updated Geometry

Pressure Center

Convergence History

Validation Status

This object becomes the input to

Hydrodynamic Validation.

---

# Engineering Assumptions

Version 1 assumes

Steady incompressible flow

2D airfoil performance

No cavitation effects

No hull-fin interference

No dynamic stall

No hysteresis

Future versions

Support

3D correction factors

Dynamic stall

Free-surface effects

Wake correction

CFD-derived polars

---

# Rules for the AI Agent

1. Never use simplified lift-curve equations when XFOIL data are available.

2. Always interpolate Reynolds number and angle of attack.

3. Every airfoil selection shall be justified with quantitative metrics.

4. Maintain a complete convergence history for debugging and reporting.

5. Keep the AirfoilDatabase independent of the optimization engine.

6. Never silently extrapolate beyond the available Reynolds or angle-of-attack range. Warn the user or reject the design.

7. Store every interpolated value with its source Reynolds datasets and interpolation weights.

8. The output of this module is an aerodynamically consistent fin design—not yet the final optimized fin.


# Chapter 3.7 – Hydrodynamic Validation Module

## Objective

The purpose of this module is to verify that the candidate fin can actually produce the required control authority under the specified operating conditions.

This module shall compare

Required Performance

vs

Available Performance

using the selected airfoil, operating Reynolds number, actual geometry, and hydrodynamic conditions.

No optimization shall occur in this module.

Its responsibility is validation only.

If the design fails, the module shall clearly identify the reason and recommend which parameter should be modified.

---

# Inputs

Receive

VehicleModel

HydrodynamicModel

ControlRequirementModel

ControlAllocationModel

CandidateFinGeometry

AerodynamicDesignModel

---

# Outputs

Return

HydrodynamicValidationModel

containing

• Available Lift

• Available Drag

• Available Control Moment

• Required Control Moment

• Lift Margin

• Moment Margin

• Stall Margin

• Deflection Margin

• Hydrodynamic Efficiency

• Failure Reasons

• Validation Status

---

# 3.7.1 Operating Conditions

Retrieve

Vehicle Speed

Water Density

Dynamic Pressure

Operating Reynolds Number

Operating Angle of Attack

Selected Airfoil

No values shall be recomputed.

---

# 3.7.2 Actual Lift

Using

Interpolated CL

Dynamic Pressure

Current Area

Compute

Actual Lift

Store

Lift

Lift Coefficient

Lift Direction

---

# 3.7.3 Actual Drag

Using

Interpolated CD

Compute

Profile Drag

Store

Drag

Drag Coefficient

Lift-to-Drag Ratio

---

# 3.7.4 Available Control Moment

Using

Actual Lift

Lever Arm

Control Allocation Matrix

Compute

Available Vehicle Control Moment

Store

Moment about

Yaw

Pitch

Roll

Version 1

Yaw only

Future

All axes

---

# 3.7.5 Control Authority Check

Compare

Available Moment

Required Moment

Compute

Control Margin

Margin = Available / Required

Store

Control Authority Percentage

Generate warning if

Margin

< configurable threshold.

Default

1.20

(20% reserve)

---

# 3.7.6 Lift Margin

Compute

Available Lift

Required Lift

Store

Lift Margin

Generate warning if

Available Lift

< Required Lift

---

# 3.7.7 Drag Assessment

Store

Drag Force

Lift-to-Drag Ratio

Induced Drag Estimate

Future

3D correction

Hull interference

---

# 3.7.8 Stall Verification

Verify

Operating Angle

<

Stall Angle

Compute

Remaining Stall Margin

Generate

Warning

Critical Warning

Failure

depending on remaining margin.

Default

Safe Margin

≥5°

---

# 3.7.9 Deflection Check

Determine

Required Fin Deflection

using

Airfoil Polar

Compute

Remaining Servo Travel

Version 1

Assume

Maximum Deflection

±30°

User configurable

Store

Deflection Margin

Generate warning if

Required Deflection

approaches limit.

---

# 3.7.10 Flow Separation Risk

Estimate

Risk Level

Low

Moderate

High

based on

Operating Angle

Stall Margin

Lift Coefficient

Future

Boundary-layer analysis.

---

# 3.7.11 Cavitation Risk

Estimate

Pressure Coefficient

Operating Velocity

Depth

Determine

Approximate Cavitation Risk

Version 1

Warning only

No redesign.

---

# 3.7.12 Efficiency Metrics

Compute

Lift-to-Drag Ratio

Control Moment per Unit Drag

Control Moment per Unit Area

Control Moment per Unit Mass

These metrics will later be used by the optimization engine.

---

# 3.7.13 Validation Report

Generate

Hydrodynamic Pass

or

Hydrodynamic Failure

For failures

Specify

Reason

Examples

Insufficient Lift

Insufficient Moment

Near Stall

Too Much Drag

Excessive Deflection

Low Reynolds Number

Airfoil Outside Valid Range

Every failure must contain

Recommended corrective actions.

Example

Increase Area

Increase Span

Select Different Airfoil

Increase Aspect Ratio

Increase Speed

Choose Higher-Lift Airfoil

---

# 3.7.14 Validation Matrix

Store

Validation Results

Boolean

Pass

Fail

For

Lift

Moment

Drag

Stall

Deflection

Airfoil

Reynolds

Overall

---

# 3.7.15 Engineering Assumptions

Assume

Steady flow

Constant velocity

No unsteady lift

No dynamic stall

Rigid fin

Perfect actuator

No hull interference

Future

Dynamic maneuvering

Unsteady aerodynamics

Wake interaction

---

# 3.7.16 Outputs

Return

HydrodynamicValidationModel

containing

Available Lift

Available Drag

Available Moment

Lift Margin

Moment Margin

Stall Margin

Deflection Margin

Efficiency Metrics

Failure Report

Recommendations

Validation Matrix

Overall Status

This model becomes the direct input to the Structural Analysis Module.

---

# Rules for the AI Agent

1. This module shall never modify the fin geometry. It only evaluates it.

2. Compare available performance against required performance using consistent SI units.

3. Record every intermediate value used in the calculations for traceability.

4. Every failed validation shall include a clear engineering explanation and at least one suggested corrective action.

5. Store all validation metrics in a HydrodynamicValidationModel object.

6. Do not silently clamp or adjust values to make a design pass.

7. Every margin (lift, moment, stall, deflection) shall be independently reported.

8. The output of this module is a pass/fail engineering assessment, not an optimized design.


# Chapter 3.8 – Structural Analysis Module

## Objective

The objective of this module is to determine whether the candidate fin can safely withstand all hydrodynamic loads without structural failure.

Unlike CFD or FEA, this module uses analytical beam theory suitable for preliminary engineering design.

The fin shall be treated as a cantilever beam fixed at the root.

The module shall calculate

• Root bending stress

• Shear stress

• Tip deflection

• Factor of Safety

• Torsional loads

• Shaft loads

• Structural margins

The module shall not modify geometry.

It shall only evaluate it.

---

# Inputs

Receive

VehicleModel

CandidateFinGeometry

MaterialModel

HydrodynamicValidationModel

ServoModel

---

# Outputs

Return

StructuralValidationModel

containing

Maximum Stress

Maximum Shear Stress

Tip Deflection

Twist

Factor of Safety

Root Bending Moment

Root Shear Force

Root Torque

Stress Distribution

Deflection Distribution

Failure Modes

Recommendations

Validation Status

---

# 3.8.1 Material Model

Version 1

Support

PLA

Material properties shall include

Density

Young's Modulus

Poisson Ratio

Yield Strength

Ultimate Strength

Shear Modulus

Future versions

PETG

ABS

Nylon

Carbon Fiber

Aluminum

Titanium

Composite Laminates

The software shall use a Material Database.

No material constants shall be hardcoded.

---

# 3.8.2 Load Cases

The structural module shall evaluate

Cruise Load

Maximum Maneuver Load

Emergency Load

Version 1

Emergency Load

=

Maximum Hydrodynamic Load

×

Safety Factor

Future versions

Dynamic impact loading

Collision

Transportation loads

---

# 3.8.3 Hydrodynamic Loading

Obtain

Lift Force

Drag Force

Moment

from

HydrodynamicValidationModel.

Compute

Resultant Load Vector

acting on the fin.

---

# 3.8.4 Distributed Load Approximation

Approximate

Lift

as a distributed load

along the span.

Version 1

Elliptical distribution

or

Uniform distribution

(selectable)

Future

Pressure integration from XFOIL.

---

# 3.8.5 Root Shear Force

Compute

Total Shear Force

at the fin root.

Store

Maximum Root Shear.

---

# 3.8.6 Root Bending Moment

Integrate

Distributed Load

to determine

Maximum Root Bending Moment.

Store

Root Bending Moment.

This becomes the primary structural design load.

---

# 3.8.7 Section Properties

Compute

Cross-sectional Area

Second Moment of Area

Polar Moment of Inertia

Section Modulus

using

Actual airfoil geometry

or

Equivalent section approximation.

Future

Numerical integration of airfoil coordinates.

---

# 3.8.8 Bending Stress

Compute

Maximum Bending Stress

using

Beam Theory.

Store

Stress Distribution

Maximum Stress

Location

---

# 3.8.9 Shear Stress

Compute

Maximum Shear Stress

at the root.

Store

Peak Shear

Average Shear

---

# 3.8.10 Tip Deflection

Compute

Elastic Tip Deflection

using

Beam Deflection Theory.

Store

Maximum Deflection

Percentage of Span

Generate warning if

Deflection exceeds allowable limit.

---

# 3.8.11 Fin Twist

Estimate

Elastic Twist

caused by

Hydrodynamic loading.

Version 1

Simple torsional beam approximation.

Future

Full torsion analysis.

---

# 3.8.12 Combined Stress

Compute

Equivalent Stress

using

Von Mises Criterion

Version 1

Even though PLA is brittle compared to metals,

Von Mises shall be reported for consistency.

Future

Material-specific failure criteria.

---

# 3.8.13 Factor of Safety

Compute

Factor of Safety

against

Yield

Ultimate

Buckling

Version 1

Buckling only if applicable.

Store

Safety Factors separately.

---

# 3.8.14 Failure Modes

Automatically classify

Root Failure

Tip Failure

Excessive Deflection

Shear Failure

Buckling

Torsional Failure

No Failure

Store

Failure Ranking

---

# 3.8.15 Manufacturing Constraints

Verify

Minimum Wall Thickness

Minimum Root Thickness

Maximum Overhang

Printability

Internal Void Thickness

Support Requirement

Future

Injection molding

Composite layups

CNC machining

---

# 3.8.16 Fatigue (Future)

Version 1

Ignore fatigue.

Architecture shall support

High-cycle fatigue

Low-cycle fatigue

Creep

Environmental degradation.

---

# 3.8.17 Validation

Verify

Stress < Allowable

Deflection < Allowable

Safety Factor > Minimum

No invalid geometry

Finite values

Positive material properties

---

# 3.8.18 Outputs

Return

StructuralValidationModel

containing

Stress

Shear

Deflection

Twist

Root Moment

Root Shear

Failure Modes

Safety Factors

Recommendations

Validation Status

This object becomes input to the Servo Module.

---

# Engineering Assumptions

Version 1 assumes

Linear elasticity

Small deflections

Isotropic material

Uniform material properties

Rigid root attachment

No thermal effects

No creep

No fatigue

No manufacturing defects

Future versions

Orthotropic composites

Nonlinear materials

FEA coupling

Residual stresses

---

# Rules for the AI Agent

1. Never modify geometry in this module.

2. Treat the fin as a cantilever beam fixed at the root.

3. Every structural calculation shall include units and engineering assumptions.

4. Store complete stress and deflection results for reporting.

5. If any structural criterion fails, clearly identify the dominant failure mode.

6. Keep the structural solver independent of the optimization engine.

7. Material properties shall always come from the Material Database.

8. This module performs structural verification only.


# Chapter 3.9 – Servo, Shaft & Hinge Design Module

## Objective

The purpose of this module is to verify that the fin actuation system is capable of producing the required fin deflection under all operating conditions.

The module shall evaluate

• Hinge moment
• Servo torque requirement
• Shaft stresses
• Bearing loads
• Servo utilization
• Mechanical safety factors
• Actuator limits

This module shall not resize the fin.

It shall only verify the actuator system.

---

# Inputs

Receive

VehicleModel

CandidateFinGeometry

AerodynamicDesignModel

HydrodynamicValidationModel

StructuralValidationModel

ServoSpecification

MaterialModel

---

# Outputs

Return

ServoValidationModel

containing

Required Servo Torque

Available Servo Torque

Servo Utilization

Hinge Moment

Shaft Diameter

Bearing Load

Bearing Pressure

Shaft Stress

Servo Safety Factor

Maximum Deflection

Actuation Time

Mechanical Efficiency

Failure Modes

Recommendations

Validation Status

---

# 3.9.1 Servo Specification

The ServoSpecification shall contain

Manufacturer

Model

Rated Torque

Peak Torque

Rated Voltage

Maximum Speed

Maximum Rotation

Deadband

Gear Material

Gear Ratio

Output Shaft Diameter

Servo Weight

Servo Dimensions

Waterproof Rating

Temperature Range

Version 1

User enters

Rated Torque

Output Shaft Diameter

Maximum Rotation

Future

Automatic servo database.

---

# 3.9.2 Operating Conditions

Retrieve

Operating Speed

Dynamic Pressure

Lift

Drag

Angle of Attack

Moment Arm

No values shall be recomputed.

---

# 3.9.3 Hinge Moment

Compute

Hydrodynamic Hinge Moment

using

Interpolated Moment Coefficient

Dynamic Pressure

Mean Aerodynamic Chord

Planform Area

Store

Maximum Hinge Moment

Average Hinge Moment

Moment Direction

Version 1

Use analytical approximation.

Future

Pressure integration.

---

# 3.9.4 Required Servo Torque

Determine

Required Torque

using

Hinge Moment

Mechanical Linkage Ratio

Mechanical Efficiency

Safety Factor

Store

Continuous Torque

Peak Torque

---

# 3.9.5 Servo Utilization

Compute

Servo Utilization

=

Required Torque

/

Rated Torque

Store

Continuous Utilization

Peak Utilization

Generate warnings if

Utilization exceeds configurable threshold.

Default

80%

---

# 3.9.6 Servo Speed Verification

Determine

Time required

to rotate

from neutral

to maximum operating angle.

Compare

Servo Speed

with

Mission Requirement

Store

Response Time

Angular Velocity

Generate warning if

Response too slow.

---

# 3.9.7 Shaft Design

Using

Output Shaft Diameter

Compute

Torsional Stress

Shear Stress

Angular Twist

Store

Maximum Stress

Safety Factor

Future

Keyway analysis

Spline analysis

---

# 3.9.8 Shaft Location Optimization

Determine

Optimal Shaft Position

along the chord.

Version 1

Evaluate

20%

25%

30%

35%

40%

45%

50%

Chord

For each position

Compute

Hinge Moment

Required Servo Torque

Structural Thickness

Manufacturing Clearance

Select

Best Position

using weighted score.

Store

Optimal Shaft Location

Engineering Rationale

Future

Continuous optimization.

---

# 3.9.9 Bearing Loads

Compute

Radial Load

Axial Load

Resultant Bearing Load

Estimate

Bearing Pressure

Version 1

Simple cylindrical bearing model.

Future

Rolling bearings

Composite bushings

Hydrodynamic bearings.

---

# 3.9.10 Mechanical Stops

Verify

Maximum Servo Rotation

Maximum Fin Rotation

Mechanical Clearance

Store

Positive Margin

Generate warning if

Mechanical interference exists.

---

# 3.9.11 Linkage Analysis

Version 1

Assume

Direct Drive

Future

Pushrod

Bell Crank

Dual Servo

Differential Linkages

Geared Transmission

Store

Mechanical Advantage

Transmission Efficiency

---

# 3.9.12 Waterproofing Check

Version 1

Informational only.

Store

Recommended Shaft Seal Type

Recommended O-ring Size

Minimum Seal Clearance

Future

Seal friction

Pressure compensation

Leakage estimation.

---

# 3.9.13 Failure Modes

Automatically classify

Insufficient Torque

Servo Saturation

Shaft Yield

Excessive Twist

Bearing Overload

Mechanical Interference

Seal Clearance Failure

No Failure

Store

Failure Ranking

Recommendations

---

# 3.9.14 Validation

Verify

Servo Torque

within limits

Servo Speed

acceptable

Shaft Stress

acceptable

Bearing Pressure

acceptable

Mechanical Clearance

sufficient

Finite values

No NaN

No Infinite Values

---

# 3.9.15 Outputs

Return

ServoValidationModel

containing

Hinge Moment

Required Torque

Servo Utilization

Servo Speed

Optimal Shaft Position

Bearing Loads

Shaft Stress

Mechanical Stops

Recommendations

Validation Status

This object becomes input to the Optimization Module.

---

# Engineering Assumptions

Version 1 assumes

Rigid linkage

Direct-drive servo

No backlash

Constant mechanical efficiency

Perfect shaft alignment

No seal friction

No gear wear

Future versions

Flexible couplings

Backlash models

Seal friction

Gearbox efficiency

Pressure effects

---

# Rules for the AI Agent

1. Never modify fin geometry in this module.

2. Compute servo requirements using hinge moment rather than fin lift alone.

3. Optimize shaft position independently of the fin geometry.

4. Use manufacturer specifications for servo limits whenever available.

5. Store all intermediate calculations for traceability.

6. Clearly distinguish continuous torque from peak torque requirements.

7. Report every failure mode with engineering recommendations.

8. The output of this module is a validated actuation system, not an optimized fin.


# Chapter 3.10 – Multi-Objective Optimization Engine

## Objective

The purpose of this module is to automatically determine the optimal fin design that satisfies all engineering constraints while minimizing performance penalties.

Unlike traditional fin sizing methods, the optimizer shall simultaneously consider

• Hydrodynamic performance

• Structural integrity

• Servo capability

• Manufacturing constraints

• Mission requirements

The optimizer shall never optimize a single objective in isolation.

Instead it shall solve a constrained multi-objective engineering optimization problem.

---

# Inputs

Receive

VehicleModel

MissionModel

HydrodynamicModel

ControlRequirementModel

CandidateFinGeometry

AerodynamicDesignModel

HydrodynamicValidationModel

StructuralValidationModel

ServoValidationModel

DesignVariableManager

ManufacturingConstraints

MaterialModel

---

# Outputs

Return

OptimizationModel

containing

Optimal Geometry

Optimal Airfoil

Objective Values

Constraint Values

Optimization History

Convergence History

Pareto Front

Sensitivity Results

Validation Status

---

# 3.10.1 Design Variables

The optimizer shall obtain all variables from

DesignVariableManager.

Version 1

Optimizable variables include

Span

Root Chord

Tip Chord

Aspect Ratio

Taper Ratio

Sweep Angle

Airfoil Selection

Thickness Ratio

Shaft Position

Future versions

Twist

Washout

Winglets

Curved Leading Edge

Variable Thickness

Internal Reinforcement

---

# 3.10.2 Fixed Parameters

The optimizer shall never modify

Vehicle Dimensions

Mission Requirements

Required Control Moment

Material

Water Properties

Servo Specifications

Manufacturing Method

unless explicitly permitted.

---

# 3.10.3 Objective Functions

Version 1

Primary Objective

Minimize

Total Drag

Secondary Objectives

Minimize

Fin Mass

Servo Utilization

Root Stress

Tip Deflection

Control Surface Area

Future versions

Manufacturing Cost

Noise

Cavitation Risk

Energy Consumption

---

# 3.10.4 Constraints

Every candidate design shall satisfy

Required Lift

Required Control Moment

Minimum Stall Margin

Minimum Safety Factor

Maximum Servo Utilization

Maximum Shaft Stress

Maximum Deflection

Manufacturing Limits

Airfoil Reynolds Range

Finite Geometry

Valid Material Properties

If any constraint fails

The design is infeasible.

---

# 3.10.5 Optimization Algorithm

Version 1

Support

Genetic Algorithm

Particle Swarm Optimization

Differential Evolution

Grid Search

The optimization algorithm shall be modular.

Future versions

Bayesian Optimization

NSGA-II

NSGA-III

CMA-ES

Surrogate Optimization

Gradient-Based Methods

---

# 3.10.6 Candidate Generation

Generate

Candidate Design

↓

Run

Initial Fin Sizing

↓

Airfoil Selection

↓

Hydrodynamic Validation

↓

Structural Validation

↓

Servo Validation

↓

Evaluate Objectives

↓

Evaluate Constraints

↓

Store Results

Repeat until convergence.

---

# 3.10.7 Constraint Handling

Version 1

Use

Penalty Functions

or

Constraint Ranking

Infeasible designs shall not automatically be discarded.

Their failure reasons shall be stored.

---

# 3.10.8 Pareto Front

For multi-objective optimization

Store

Pareto Optimal Designs

Version 1

Display

Top 20 Designs

For each design

Store

Geometry

Objectives

Constraints

Airfoil

Mass

Drag

Servo Margin

Safety Factor

---

# 3.10.9 Convergence Criteria

Stop optimization when

Maximum Iterations reached

or

Objective Improvement

falls below

configurable tolerance.

Store

Iteration History

Best Objective

Best Design

Elapsed Time

---

# 3.10.10 Sensitivity Analysis

After convergence

Perturb each optimized variable

individually

Determine

Objective sensitivity

Constraint sensitivity

Rank variables by influence.

Store

Sensitivity Matrix.

---

# 3.10.11 Robustness Analysis

Evaluate the optimal design under

±10% speed

±5% density

±10% mass

±5% lift coefficient

Version 1

Deterministic analysis.

Future

Monte Carlo simulation

Probabilistic optimization

---

# 3.10.12 Design Ranking

Rank candidate designs using

Weighted Objective Score

Constraint Satisfaction

Engineering Robustness

Manufacturability

Mission Suitability

Store

Complete ranking.

---

# 3.10.13 Optimization Report

Generate

Optimization Summary

including

Best Design

Objective Values

Constraint Margins

Optimization History

Pareto Front

Sensitivity Results

Failure Statistics

Recommended Design

Alternative Designs

---

# 3.10.14 Validation

Verify

Convergence achieved

No invalid geometry

Finite objective values

Finite constraints

Successful downstream module execution

Consistent units

Repeatability using identical random seed

---

# 3.10.15 Outputs

Return

OptimizationModel

containing

Optimal Geometry

Optimal Airfoil

Objective Values

Constraint Values

Pareto Front

Optimization History

Sensitivity Matrix

Robustness Results

Recommended Design

Validation Status

This model becomes the input to the CAD Generation Module.

---

# Engineering Assumptions

Version 1 assumes

Deterministic optimization

Steady operating conditions

Independent objective evaluations

Perfect convergence of downstream modules

Future versions

Robust optimization

Reliability-based optimization

Real-time adaptive optimization

Digital twin integration

---

# Rules for the AI Agent

1. Never evaluate objectives before all validation modules have completed.

2. Every candidate design must pass through the complete engineering pipeline.

3. Maintain a complete optimization history for reproducibility.

4. Keep optimization algorithms modular and interchangeable.

5. Store all infeasible designs with their failure reasons for later analysis.

6. Never modify fixed parameters unless explicitly authorized.

7. Support both single-objective and multi-objective optimization.

8. Every recommended design shall include quantitative justification and comparison with at least the next three best alternatives.


# Chapter 3.11 – CAD Generation & Manufacturing Module

## Objective

The purpose of this module is to convert the optimized fin design into manufacturing-ready CAD models and fabrication files.

The module shall automatically generate

• 3D CAD models

• 2D engineering drawings

• Manufacturing dimensions

• Assembly interfaces

• Export files

The generated CAD shall exactly match the optimized engineering design.

No design optimization shall occur in this module.

---

# Inputs

Receive

OptimizationModel

MaterialModel

ManufacturingConstraints

ServoValidationModel

VehicleModel

---

# Outputs

Return

CADModel

containing

3D Geometry

2D Drawings

Manufacturing Features

Assembly Interfaces

Export Files

Drawing Sheets

Manufacturing Report

Validation Status

---

# 3.11.1 Geometry Import

Import

Optimized Geometry

including

Span

Root Chord

Tip Chord

Sweep

Thickness Distribution

Airfoil Coordinates

Root Position

Tip Position

Shaft Location

No geometry shall be modified.

---

# 3.11.2 Airfoil Construction

Generate

Airfoil Sketches

at

Root

Tip

Intermediate Sections

using

Original DAT coordinates.

Apply

Scaling

Rotation

Sweep

Taper

Automatically.

---

# 3.11.3 Loft Generation

Generate

Solid Fin

using

Loft

between

Airfoil Sections.

Version 1

Linear Loft

Future

Guide Curves

Curvature Continuity

Variable Thickness

---

# 3.11.4 Root Interface

Generate

Root Hub

including

Servo Shaft Hole

Bearing Seat

Mounting Boss

Fillets

Root Reinforcement

Dimensions shall be configurable.

---

# 3.11.5 Shaft Features

Automatically create

Shaft Bore

Keyway (future)

Spline (future)

Retaining Screw Hole

Flat Section

Tolerance Class

Store

Assembly Dimensions.

---

# 3.11.6 Edge Treatment

Generate

Leading Edge Radius

Trailing Edge Thickness

Root Fillets

Tip Radius

Version 1

Use configurable defaults.

Future

Optimization-driven shaping.

---

# 3.11.7 Internal Structure

Version 1

Solid Model

Future

Generate

Internal Ribs

Honeycomb

Lattice

Variable Infill

Carbon Rod Channels

Cable Routing

Weight Reduction Pockets

---

# 3.11.8 Manufacturing Checks

Verify

Minimum Wall Thickness

Minimum Trailing Edge

Minimum Hole Diameter

Feature Clearance

Self-intersections

Open Surfaces

Non-manifold Geometry

Generate warnings for

Unprintable features.

---

# 3.11.9 Drawing Generation

Automatically create

Engineering Drawings

including

Front View

Side View

Top View

Section Views

Dimension Tables

Hole Tables

Mass Properties

Center of Gravity

Scale

Drawing Revision

Version 1

ISO standard dimensions.

Future

ANSI support.

---

# 3.11.10 Export Formats

Support

STEP (.step)

IGES (.igs)

STL (.stl)

3MF (.3mf)

OBJ (.obj)

DXF (.dxf)

SVG (.svg)

Future

Native Fusion 360

SolidWorks

Onshape

FreeCAD

CATIA

Creo

---

# 3.11.11 Manufacturing Metadata

Embed

Material

Mass

Part Number

Revision

Designer

Creation Date

Optimization ID

Airfoil Name

Units

into exported files where supported.

---

# 3.11.12 3D Printing Preparation

Generate recommended

Print Orientation

Layer Height

Wall Count

Top/Bottom Layers

Infill Percentage

Infill Pattern

Support Requirement

Brim/Raft Recommendation

Estimated Print Time

Estimated Material Usage

Version 1

FDM printing with PLA.

Future

SLA

SLS

CNC

Injection Molding

Composite Layup

---

# 3.11.13 Assembly Verification

Verify

Fin fits within

Hull

Servo

Shaft

Bearing

Mounting Interface

Detect

Interference

Collision

Insufficient Clearance

Store

Assembly Report.

---

# 3.11.14 CAD Validation

Verify

Closed Solid

No Invalid Faces

No Self-intersections

No Open Edges

Positive Volume

Correct Units

Successful Export

---

# 3.11.15 Outputs

Return

CADModel

containing

Solid Geometry

Drawing Package

Export Files

Manufacturing Report

Assembly Report

Print Recommendations

Validation Status

This model becomes the input to the Simulation Export Module.

---

# Engineering Assumptions

Version 1 assumes

Single-piece fin

FDM manufacturing

PLA material

No inserts

No overmolding

No embedded hardware

Future versions

Multi-material printing

Metal inserts

Composite layups

Machined aluminum

Modular fin assemblies

---

# Rules for the AI Agent

1. Never alter optimized geometry during CAD generation.

2. Use the original airfoil coordinates to construct the geometry rather than approximating the profile.

3. Generate watertight solid models suitable for manufacturing.

4. Automatically validate every exported model before release.

5. Keep CAD generation independent of the optimization engine.

6. Include all manufacturing metadata and revision information in generated outputs.

7. Every exported model shall be traceable to its optimization and validation results.

8. The output of this module shall be directly manufacturable without requiring manual CAD reconstruction.


# Chapter 3.12 – Simulation Export & Digital Twin Integration

## Objective

The purpose of this module is to automatically generate simulation-ready models from the optimized fin and vehicle design.

The exported models shall be directly usable in marine robotics simulation environments without requiring manual parameter entry.

The module shall generate

• Geometry files

• Hydrodynamic parameters

• Mass properties

• Joint definitions

• Actuator definitions

• Vehicle configuration

• Environment configuration

The software shall also provide an architecture for future Digital Twin integration.

No optimization shall occur in this module.

---

# Inputs

Receive

VehicleModel

OptimizationModel

CADModel

HydrodynamicModel

AerodynamicDesignModel

StructuralValidationModel

ServoValidationModel

MaterialModel

MissionModel

---

# Outputs

Return

SimulationModel

containing

Simulation Geometry

Vehicle Parameters

Fin Parameters

Hydrodynamic Parameters

Mass Properties

Joint Configuration

Actuator Configuration

Environment Parameters

Export Files

Validation Status

---

# 3.12.1 Supported Simulators

Version 1

Support

Stonefish

Gazebo Harmonic

Gazebo Garden

Future

UUV Simulator

Unity

NVIDIA Isaac Sim

Webots

MATLAB/Simulink

Custom Physics Engine

The exporter architecture shall be simulator-independent.

---

# 3.12.2 Geometry Export

Export

Hull

Fins

Mounts

Shafts

Assembly

using

STL

or

DAE

depending on simulator requirements.

Maintain

Correct Coordinate Frames

Correct Units

Correct Scaling

---

# 3.12.3 Mass Properties

Export

Mass

Center of Gravity

Moments of Inertia

Material Density

Buoyancy Properties

Volume

Store

Complete Mass Matrix.

---

# 3.12.4 Hydrodynamic Parameters

Export

Added Mass

Linear Damping

Quadratic Damping

Control Derivatives

Lift Coefficients

Drag Coefficients

Moment Coefficients

Reference Areas

Reference Lengths

Future

Lookup tables

Dynamic derivatives.

---

# 3.12.5 Fin Configuration

Export

Number of Fins

Fin Positions

Fin Orientation

Control Axes

Maximum Deflection

Servo Limits

Airfoil Name

Geometry Parameters

---

# 3.12.6 Joint Definitions

Create

Revolute Joints

for

Every Control Fin.

Specify

Joint Axis

Joint Limits

Reference Position

Maximum Velocity

Maximum Acceleration

Damping

Friction

Version 1

Position-controlled joints.

Future

Torque-controlled joints.

---

# 3.12.7 Actuator Model

Export

Servo Limits

Maximum Torque

Maximum Speed

Maximum Rotation

Control Frequency

Deadband

Version 1

Ideal Servo

Future

Motor Dynamics

Gearbox Dynamics

Backlash

Transmission Compliance

---

# 3.12.8 Sensor Configuration

Version 1

Support

IMU

Depth Sensor

Camera

Future

DVL

USBL

Acoustic Modem

Multibeam Sonar

Forward Looking Sonar

GNSS

Pressure Array

Automatically generate

Sensor Positions

Reference Frames.

---

# 3.12.9 Environment Configuration

Export

Water Density

Gravity

Fluid Viscosity

Simulation Step Size

Current Velocity

Current Direction

Water Depth

Version 1

Static environment.

Future

Waves

Currents

Turbulence

Marine Growth

---

# 3.12.10 Controller Interface

Generate

Control Topics

Joint Interfaces

Servo Commands

State Outputs

Vehicle Pose

Velocity

Acceleration

Version 1

ROS 2 compatible.

Future

DDS

LCM

Custom middleware.

---

# 3.12.11 Mission Definition

Generate

Mission Configuration

including

Cruise Speed

Target Depth

Waypoint List

Turning Radius

Mission Duration

Version 1

Simple mission file.

Future

Mission scripting.

---

# 3.12.12 Validation

Verify

Geometry loaded

Mass properties valid

Joint limits valid

Hydrodynamic parameters complete

Coordinate frames consistent

Units correct

Simulation package generated successfully

---

# 3.12.13 Digital Twin Architecture

Provide interfaces for

Simulation Results

Experimental Data

Vehicle Logs

Parameter Updates

Calibration Results

Future

Automatic model calibration

Parameter estimation

Online system identification

Predictive maintenance

---

# 3.12.14 Export Package

Generate

Simulation Package

containing

Geometry

Configuration Files

Vehicle Parameters

Mission File

Launch Files

Documentation

Version 1

Simulator-specific folder structure.

---

# 3.12.15 Outputs

Return

SimulationModel

containing

Export Files

Vehicle Configuration

Joint Configuration

Sensor Configuration

Hydrodynamic Parameters

Mission Configuration

Validation Status

This model becomes the input to the Reporting Module.

---

# Engineering Assumptions

Version 1 assumes

Rigid body dynamics

Ideal actuators

Ideal sensors

Constant environmental conditions

Steady hydrodynamics

Future versions

Flexible structures

Sensor noise

Current disturbances

Wave interaction

Hardware-in-the-loop

Real-time synchronization

---

# Rules for the AI Agent

1. Never modify the optimized engineering design during export.

2. Maintain consistent coordinate frames and SI units across all exported files.

3. Keep simulator-specific code isolated from the core engineering models.

4. Validate every generated simulation package before export.

5. Export all physical parameters required for reproducible simulations.

6. Ensure ROS 2 compatibility for supported simulators.

7. Record simulator version and export settings for traceability.

8. The output of this module shall allow immediate simulation without manual parameter editing.


# Chapter 3.13 – Reporting, Visualization & Traceability Module

## Objective

The purpose of this module is to generate comprehensive engineering documentation for the optimized fin design.

The software shall automatically produce

• Engineering reports

• Design summaries

• Optimization history

• Performance plots

• Validation results

• Manufacturing summaries

• Simulation summaries

• Complete traceability records

The report shall document every engineering decision made throughout the design process.

No engineering calculations shall be performed in this module.

---

# Inputs

Receive

VehicleModel

MissionModel

HydrodynamicModel

ControlRequirementModel

ControlAllocationModel

CandidateFinGeometry

AerodynamicDesignModel

HydrodynamicValidationModel

StructuralValidationModel

ServoValidationModel

OptimizationModel

CADModel

SimulationModel

---

# Outputs

Return

EngineeringReport

containing

PDF Report

HTML Report

Markdown Report

JSON Design Archive

CSV Tables

Figures

Revision Information

Validation Status

---

# 3.13.1 Executive Summary

Generate

One-page summary

including

Project Name

Date

Version

Vehicle Overview

Mission Requirements

Selected Airfoil

Final Geometry

Optimization Objectives

Overall Validation Status

Final Recommendation

---

# 3.13.2 Input Summary

Document all user-defined inputs

Vehicle Geometry

Mission Requirements

Material

Servo Specifications

Manufacturing Constraints

Water Properties

Design Variables

Clearly distinguish

User Inputs

Calculated Values

Default Assumptions

---

# 3.13.3 Geometry Summary

Report

Span

Root Chord

Tip Chord

Area

Aspect Ratio

Taper Ratio

Sweep

Thickness

Mass

Center of Pressure

Center of Gravity

Include

Dimensioned diagrams

---

# 3.13.4 Airfoil Summary

Document

Selected Airfoil

Selection Score

Ranking of Alternatives

Operating Reynolds Number

Lift Coefficient

Drag Coefficient

Moment Coefficient

Lift-to-Drag Ratio

Operating Angle of Attack

Stall Margin

Include

Airfoil profile

Polar plots

---

# 3.13.5 Hydrodynamic Results

Summarize

Required Lift

Available Lift

Required Moment

Available Moment

Drag

Control Authority

Efficiency Metrics

Hydrodynamic Validation

Pass/Fail

---

# 3.13.6 Structural Results

Document

Root Bending Moment

Maximum Stress

Shear Stress

Tip Deflection

Twist

Safety Factors

Failure Modes

Recommendations

Pass/Fail

---

# 3.13.7 Servo Results

Document

Hinge Moment

Required Torque

Servo Utilization

Shaft Stress

Bearing Load

Optimal Shaft Position

Mechanical Margins

Pass/Fail

---

# 3.13.8 Optimization Results

Document

Optimization Algorithm

Number of Iterations

Number of Designs Evaluated

Best Objective Values

Constraint Satisfaction

Optimization Time

Convergence Status

Include

Convergence plots

Objective history

Pareto front

---

# 3.13.9 Manufacturing Summary

Report

Material

Estimated Print Time

Estimated Material Usage

Printing Orientation

Layer Height

Wall Count

Infill

Support Requirement

Exported CAD Formats

---

# 3.13.10 Simulation Summary

Document

Supported Simulator

Generated Files

Mass Properties

Hydrodynamic Parameters

Joint Configuration

Sensor Configuration

Mission Configuration

Export Validation

---

# 3.13.11 Sensitivity Analysis

Include

Sensitivity Matrix

Variable Ranking

Spider Charts

Tornado Charts

Future

Monte Carlo plots

---

# 3.13.12 Design Advisor Report

Summarize

Design Strengths

Potential Weaknesses

Performance Bottlenecks

Future Improvements

Engineering Recommendations

Alternative Designs

This section shall use the Design Advisor Engine.

---

# 3.13.13 Figures and Tables

Automatically generate

Geometry drawings

Airfoil profile

Lift curve

Drag curve

Stress distribution

Deflection plot

Optimization convergence

Pareto front

Manufacturing drawing

Simulation architecture

Number every figure and table.

---

# 3.13.14 Traceability

Every reported value shall include

Source Module

Calculation Step

Units

Timestamp

Software Version

Design Revision

Unique Design ID

The software shall maintain a complete audit trail.

---

# 3.13.15 Design Archive

Export

Machine-readable archive

including

All engineering models

Optimization history

Validation results

Configuration

Metadata

Version information

Future

Digital Twin synchronization.

---

# 3.13.16 Report Validation

Verify

All sections generated

Figures available

Tables complete

Units consistent

No missing values

Report reproducible

Hyperlinks valid

---

# 3.13.17 Export Formats

Support

PDF

HTML

Markdown

JSON

CSV

PNG

SVG

Future

DOCX

LaTeX

Jupyter Notebook

---

# Engineering Assumptions

Version 1 assumes

Static report generation

Deterministic results

Single optimization run

Future versions

Interactive dashboards

Live reports

Cloud collaboration

Continuous documentation

---

# Rules for the AI Agent

1. Never perform new engineering calculations in this module.

2. Every reported value must reference its source model.

3. Clearly distinguish user inputs, calculated values, and assumptions.

4. Generate publication-quality figures and tables.

5. Maintain complete traceability from user input to final design.

6. Store all reports with revision history and unique design identifiers.

7. Ensure reports are reproducible using the archived design data.

8. The output of this module shall serve as the official engineering record of the design.


# Chapter 4.1 – Overall Software Architecture

## Objective

The objective of this chapter is to define the complete software architecture for the AUV Fin Design Platform.

The software shall be designed as a modular, scalable, maintainable, and extensible Computer-Aided Engineering (CAE) application.

The architecture shall separate

• Engineering calculations

• Data models

• Optimization

• CAD generation

• Simulation export

• User interface

• Reporting

Every module shall communicate through strongly typed engineering models rather than direct function calls or shared global variables.

---

# Software Design Philosophy

The software shall follow the principles of

• Separation of Concerns

• Single Responsibility

• Open/Closed Principle

• Dependency Injection

• Immutable Engineering Models

• Plugin-based Extensions

• Reproducibility

• Traceability

The architecture shall support both desktop and future cloud deployment.

---

# Overall Architecture

The application shall consist of the following layers.

--------------------------------------------------

Presentation Layer

↓

Application Layer

↓

Engineering Core

↓

Optimization Engine

↓

Export Layer

↓

Persistence Layer

--------------------------------------------------

No module shall bypass these layers.

---

# 4.1.1 Presentation Layer

Responsible for

GUI

Visualization

User Input

Project Management

Progress Monitoring

Notifications

Help System

Dark/Light Themes

No engineering calculations shall occur in this layer.

---

# 4.1.2 Application Layer

Responsible for

Workflow Control

Project Lifecycle

Module Execution

Undo/Redo

Error Handling

Logging

Task Scheduling

This layer coordinates all engineering modules.

---

# 4.1.3 Engineering Core

Contains

Vehicle Module

Mission Module

Hydrodynamics

Control Allocation

Fin Sizing

Airfoil Engine

Structural Solver

Servo Solver

Validation

This is the heart of the software.

Modules communicate only through engineering models.

---

# 4.1.4 Optimization Layer

Contains

Optimization Pipeline

Objective Functions

Constraint Evaluation

Optimization Algorithms

Sensitivity Analysis

Robustness Analysis

This layer shall never directly access GUI objects.

---

# 4.1.5 Export Layer

Responsible for

CAD Export

Simulation Export

Reports

Images

CSV

JSON

STEP

STL

Every exporter shall be independent.

---

# 4.1.6 Persistence Layer

Responsible for

Saving Projects

Loading Projects

Version History

Design Archive

Preferences

Logs

Future

Cloud Storage

Database Support

---

# Data Flow

The software shall execute

Project

↓

Vehicle

↓

Mission

↓

Engineering Pipeline

↓

Optimization

↓

CAD

↓

Simulation

↓

Report

Every stage shall produce immutable outputs.

---

# Core Engineering Models

The architecture shall define

VehicleModel

MissionModel

HydrodynamicModel

ControlRequirementModel

ControlAllocationModel

CandidateFinGeometry

AerodynamicDesignModel

HydrodynamicValidationModel

StructuralValidationModel

ServoValidationModel

OptimizationModel

CADModel

SimulationModel

EngineeringReport

DesignProject

Every module shall consume and produce these models.

---

# Plugin Architecture

Future engineering modules shall be added through plugins.

Examples

CFD Plugin

FEA Plugin

AI Design Advisor

Experimental Database

Material Database

Mission Planner

Digital Twin

Plugins shall register themselves without modifying the core application.

---

# Dependency Rules

Presentation Layer

↓

Application Layer

↓

Engineering Core

↓

Optimization

↓

Export

↓

Persistence

Reverse dependencies are prohibited.

Circular dependencies are prohibited.

---

# Error Handling

Every module shall return

Success

Warning

Failure

Diagnostic Messages

Suggested Fixes

Execution Time

Exception Details

No module shall terminate the application unexpectedly.

---

# Logging

Every engineering step shall be logged.

Log entries include

Timestamp

Module

Input

Output

Execution Time

Warnings

Errors

Project Version

---

# Configuration

All configurable values shall be stored centrally.

Examples

Material Properties

Optimization Settings

GUI Preferences

Manufacturing Defaults

Safety Factors

Tolerance Values

Never hardcode configurable engineering values.

---

# Testing

Every module shall support

Unit Tests

Integration Tests

Regression Tests

Validation Tests

Benchmark Problems

Continuous Integration

---

# Performance

The software shall support

Parallel Optimization

Lazy Loading

Caching

Incremental Recalculation

Asynchronous GUI

Future GPU acceleration.

---

# Security

Projects shall be protected from corruption.

Support

Automatic Backup

Crash Recovery

Autosave

Version Recovery

Future

Digital Signatures

Encrypted Projects

---

# Future Expansion

Architecture shall support

Cloud Computing

Distributed Optimization

Remote Solvers

Collaborative Design

AI Co-Designer

Real-time Digital Twin

Without redesigning existing modules.

---

# Rules for the AI Agent

1. Never allow engineering modules to depend on GUI code.

2. Every engineering module shall expose a clean public interface.

3. Use immutable engineering models whenever practical.

4. Keep module dependencies acyclic.

5. Make every subsystem independently testable.

6. Prefer composition over inheritance.

7. Every module shall be replaceable without affecting unrelated modules.

8. The architecture shall prioritize long-term maintainability over short-term convenience.


# Chapter 4.2 – Project Structure & Folder Organization

## Objective

The objective of this chapter is to define the complete directory structure, package organization, naming conventions, and code ownership for the AUV Fin Design Platform.

The project structure shall prioritize

• Maintainability

• Readability

• Scalability

• Testability

• Separation of Concerns

Every source file shall have a clearly defined responsibility.

No engineering algorithm shall depend on the project layout.

---

# Top-Level Directory Structure

The project shall use the following layout.

auv-fin-design/

├── src/
├── tests/
├── docs/
├── examples/
├── assets/
├── data/
├── plugins/
├── configs/
├── reports/
├── exports/
├── logs/
├── cache/
├── scripts/
├── tools/
├── benchmarks/
└── .github/

---

# src/

Contains all production source code.

Subdirectories

src/

├── application/
├── domain/
├── infrastructure/
├── adapters/
├── ui/
├── visualization/
├── utilities/

No test code shall exist inside src.

---

# application/

Contains

Workflow orchestration

Project lifecycle

Execution pipeline

Command handlers

Undo/Redo

Task scheduling

Project manager

Application services

No engineering mathematics.

---

# domain/

Contains the complete engineering core.

Subdirectories

domain/

├── vehicle/
├── mission/
├── hydrodynamics/
├── control/
├── geometry/
├── airfoil/
├── structural/
├── servo/
├── optimization/
├── manufacturing/
├── simulation/
├── reporting/
├── validation/
├── advisor/

This directory contains all engineering logic.

---

# infrastructure/

Contains external integrations

Database

Filesystem

Configuration

Logging

Caching

Serialization

Autosave

Preferences

No engineering algorithms.

---

# adapters/

Contains

CAD exporters

Simulation exporters

Report exporters

Plugin adapters

REST API

CLI

Future cloud adapters

Every external system shall be isolated here.

---

# ui/

Contains

Windows

Dialogs

Panels

Widgets

Toolbar

Ribbon

Settings

Themes

Icons

No engineering calculations.

---

# visualization/

Contains

Charts

3D Viewer

Geometry Viewer

Optimization Plots

Pareto Viewer

Stress Visualization

Simulation Preview

Only visualization logic.

---

# utilities/

Contains

Math Helpers

Geometry Utilities

Interpolation

Units

Validation Helpers

File Utilities

Reusable algorithms only.

---

# tests/

Organized identically to src.

tests/

├── application/
├── domain/
├── infrastructure/
├── adapters/
├── ui/

Support

Unit Tests

Integration Tests

Regression Tests

Performance Tests

---

# docs/

Contains

Software Specification

User Manual

Developer Guide

API Documentation

Mathematical Models

Architecture

Release Notes

Research References

---

# examples/

Contains

Tutorial Projects

Example Vehicles

Example Missions

Optimization Examples

Educational Demonstrations

---

# assets/

Contains

Icons

Themes

Fonts

Images

Splash Screens

Logos

---

# data/

Contains

Airfoil Database

Material Database

Servo Database

Hydrodynamic Correlations

Manufacturing Defaults

Mission Templates

Simulation Templates

Version-controlled datasets.

---

# plugins/

Each plugin shall exist in its own directory.

Example

plugins/

CFD/

FEA/

Stonefish/

Fusion360/

NSGAII/

AIAdvisor/

MaterialLibrary/

Plugins shall not modify core code.

---

# configs/

Contains

Application Configuration

Optimization Defaults

Logging Configuration

Theme Settings

Material Defaults

Engineering Constants

Configuration shall use

YAML

or

JSON

---

# reports/

Contains

Generated Reports

Figures

Tables

PDF

HTML

Markdown

Each report shall reside in a project-specific folder.

---

# exports/

Contains

CAD

Simulation

CSV

JSON

STEP

STL

DXF

SVG

Generated export files only.

---

# logs/

Contains

Execution Logs

Crash Reports

Performance Logs

Optimization Logs

Debug Logs

Automatically rotated.

---

# cache/

Contains

Temporary Geometry

Airfoil Cache

Optimization Cache

Simulation Cache

Automatically cleaned.

---

# scripts/

Contains

Developer utilities

Database generation

Migration

Benchmark execution

Automation

No production code.

---

# tools/

Contains

Standalone engineering utilities

Mesh converters

Airfoil importers

Coordinate converters

Diagnostic utilities

---

# benchmarks/

Contains

Reference engineering cases

Validation datasets

Performance benchmarks

Regression baselines

Used for scientific validation.

---

# .github/

Contains

CI/CD workflows

Issue templates

Pull request templates

Contribution guidelines

Code owners

---

# Naming Conventions

Packages

snake_case

Classes

PascalCase

Interfaces

Prefix

I

Enumerations

PascalCase

Constants

UPPER_CASE

Variables

snake_case

Functions

snake_case

Private members

_leading_underscore

---

# Module Boundaries

Each module

Owns

Its models

Its calculations

Its validation

Its tests

No module may modify another module's internal state.

Communication occurs through immutable models.

---

# Dependency Rules

Allowed

Application

↓

Domain

↓

Utilities

Infrastructure

↓

Utilities

Adapters

↓

Domain

Prohibited

Domain

→

UI

Domain

→

Infrastructure

Domain

→

Adapters

Circular dependencies

---

# Versioning

Every engineering model shall include

Version

Creation Time

Author

Unique Identifier

Project Identifier

Software Version

---

# Build System

Support

Python Packaging

Virtual Environment

Dependency Lock File

Pre-commit Hooks

Static Analysis

Automatic Formatting

---

# Documentation

Every public class

Every public function

Every engineering equation

Every data model

shall be documented.

---

# Rules for the AI Agent

1. Organize the project by engineering responsibility rather than technology.

2. Keep engineering algorithms inside the domain layer only.

3. Ensure every module has corresponding tests.

4. Separate generated files from source code.

5. Never mix UI code with engineering calculations.

6. Design every directory to remain manageable as the project grows.

7. Every plugin shall be installable without modifying the core application.

8. The folder structure shall support both desktop and future cloud deployments.


# Chapter 4.3 – Data Models & Class Architecture

## Objective

The objective of this chapter is to define every core engineering data model used throughout the AUV Fin Design Platform.

These models shall provide a strongly typed interface between all engineering modules.

Every module shall receive engineering models as input and return new engineering models as output.

No module shall exchange raw dictionaries, untyped JSON objects, or loosely structured data.

---

# Design Philosophy

Separate models into three categories

1. Configuration Models
   User-editable
   Mutable

2. Engineering Models
   Calculated
   Immutable

3. Result Models
   Generated outputs
   Immutable

Only Configuration Models may be modified after creation.

---

# Model Hierarchy

DesignProject

├── ProjectMetadata
├── VehicleModel
├── MissionModel
├── ConfigurationModel
├── MaterialModel
├── ManufacturingModel
├── ServoSpecification
├── HydrodynamicModel
├── ControlRequirementModel
├── ControlAllocationModel
├── CandidateFinGeometry
├── AerodynamicDesignModel
├── HydrodynamicValidationModel
├── StructuralValidationModel
├── ServoValidationModel
├── OptimizationModel
├── CADModel
├── SimulationModel
├── EngineeringReport
└── AuditTrail

---

# BaseModel

Every model shall inherit from

BaseModel

containing

Unique ID

Creation Timestamp

Model Version

Software Version

Project ID

Status

Validation State

Revision Number

Metadata

---

# ProjectMetadata

Contains

Project Name

Author

Organization

Description

Creation Date

Last Modified

Units

Coordinate System

Target Simulator

Target CAD

---

# VehicleModel

Contains

Hull Length

Hull Diameter

Hull Mass

Center of Gravity

Center of Buoyancy

Moments of Inertia

Volume

Reference Areas

Fin Positions

Servo Positions

Water Type

Derived Properties

---

# MissionModel

Contains

Cruise Speed

Maximum Speed

Operating Depth

Turning Radius

Turn Establishment Time

Mission Profile

Safety Margins

Operating Conditions

Future

Waypoint List

Mission Timeline

---

# MaterialModel

Contains

Material Name

Density

Young's Modulus

Shear Modulus

Poisson Ratio

Yield Strength

Ultimate Strength

Thermal Expansion

Maximum Service Temperature

Print Parameters

---

# ServoSpecification

Contains

Manufacturer

Model

Rated Torque

Peak Torque

Voltage

Speed

Maximum Rotation

Output Shaft Diameter

Gear Material

Weight

Dimensions

Efficiency

---

# HydrodynamicModel

Contains

Reynolds Number

Dynamic Pressure

Added Mass

Added Inertia

Linear Damping

Quadratic Damping

Drag Coefficients

Reference Lengths

Reference Areas

---

# ControlRequirementModel

Contains

Required Moment

Required Lift

Yaw Rate

Angular Acceleration

Control Margin

Design Moment

---

# ControlAllocationModel

Contains

Allocation Matrix

Lever Arms

Lift Per Fin

Control Effectiveness

Utilization

Redundancy

---

# CandidateFinGeometry

Contains

Span

Root Chord

Tip Chord

Area

Aspect Ratio

Taper Ratio

Sweep

Thickness

Mean Aerodynamic Chord

Center of Pressure

Mass Estimate

---

# AerodynamicDesignModel

Contains

Selected Airfoil

Operating Reynolds Number

Lift Coefficient

Drag Coefficient

Moment Coefficient

Lift-to-Drag Ratio

Angle of Attack

Stall Margin

Convergence History

---

# HydrodynamicValidationModel

Contains

Available Lift

Available Drag

Available Moment

Lift Margin

Moment Margin

Stall Margin

Efficiency Metrics

Validation Status

Recommendations

---

# StructuralValidationModel

Contains

Stress

Shear Stress

Tip Deflection

Twist

Root Moment

Safety Factors

Failure Modes

Validation Status

---

# ServoValidationModel

Contains

Hinge Moment

Required Torque

Servo Utilization

Bearing Load

Shaft Stress

Optimal Shaft Position

Validation Status

Recommendations

---

# OptimizationModel

Contains

Optimal Geometry

Objectives

Constraints

Pareto Front

Optimization History

Sensitivity Matrix

Robustness Results

Recommended Design

---

# CADModel

Contains

Solid Geometry

Drawing Package

Export Files

Manufacturing Metadata

Validation Status

---

# SimulationModel

Contains

Simulator

Geometry

Dynamics

Joint Definitions

Sensor Definitions

Mission File

Export Files

Validation Status

---

# EngineeringReport

Contains

Executive Summary

Figures

Tables

PDF

HTML

Markdown

JSON Archive

Revision History

---

# AuditTrail

Contains

Execution History

Module History

Warnings

Errors

Timing Information

Design Changes

User Actions

Software Version

---

# Relationships

VehicleModel

↓

HydrodynamicModel

↓

ControlRequirementModel

↓

ControlAllocationModel

↓

CandidateFinGeometry

↓

AerodynamicDesignModel

↓

Validation Models

↓

OptimizationModel

↓

CADModel

↓

SimulationModel

↓

EngineeringReport

The dependency graph shall remain acyclic.

---

# Serialization

Every model shall support

JSON

YAML

Binary

Version Migration

Backward Compatibility

Future

Database persistence

Cloud synchronization

---

# Validation

Every model shall implement

validate()

returning

Errors

Warnings

Validation Status

No invalid model shall enter the engineering pipeline.

---

# Equality

Engineering models shall be value-based.

Two models are equal if

All engineering fields are equal.

Ignore

Object identity

Memory location

---

# Immutability

Engineering models

Immutable

Configuration models

Mutable

Optimization creates

new models

rather than modifying existing ones.

---

# Units

Every engineering field shall carry explicit SI units.

Examples

Length

m

Mass

kg

Stress

Pa

Torque

N·m

Velocity

m/s

Angles

rad internally

degrees for display

---

# Rules for the AI Agent

1. Never exchange untyped data between modules.

2. Every engineering model shall be immutable after validation.

3. Every model shall support serialization and versioning.

4. Validation shall occur immediately after model creation.

5. Use composition rather than deep inheritance between engineering models.

6. Maintain strict separation between configuration data and calculated results.

7. Every model shall include metadata for traceability.

8. Every model shall be independently testable and documented.


# Chapter 4.4 – Engineering Pipeline & Execution Engine

## Objective

The objective of this chapter is to define the runtime execution model for the AUV Fin Design Platform.

The Execution Engine shall

• Coordinate all engineering modules

• Resolve dependencies automatically

• Execute modules in the correct order

• Support incremental recalculation

• Cache reusable results

• Execute independent modules in parallel

• Track execution progress

• Recover gracefully from failures

The Execution Engine shall remain independent of the GUI.

---

# Design Philosophy

The execution model shall be

Deterministic

Reproducible

Parallelizable

Restartable

Observable

Extensible

Every engineering result shall be reproducible using identical project inputs.

---

# Overall Pipeline

Project

↓

Configuration Validation

↓

Vehicle Model

↓

Mission Model

↓

Hydrodynamic Model

↓

Control Requirement

↓

Control Allocation

↓

Initial Fin Sizing

↓

Airfoil Engine

↓

Hydrodynamic Validation

↓

Structural Validation

↓

Servo Validation

↓

Optimization

↓

CAD Generation

↓

Simulation Export

↓

Report Generation

↓

Project Save

---

# Execution Graph

The execution engine shall construct

a Directed Acyclic Graph (DAG)

from module dependencies.

Each module shall declare

Inputs

Outputs

Dependencies

Execution Priority

Estimated Cost

The engine shall determine execution order automatically.

---

# Module Interface

Every engineering module shall expose

initialize()

validate_inputs()

execute()

validate_outputs()

cleanup()

Execution shall never bypass these stages.

---

# Execution Context

Each execution receives

ExecutionContext

containing

Project

Configuration

Logger

Cache

Progress Reporter

Cancellation Token

Random Seed

Temporary Workspace

System Resources

---

# Dependency Resolution

Modules shall execute only after

all required inputs

have been validated.

Circular dependencies are prohibited.

Missing dependencies shall generate

clear diagnostics.

---

# Incremental Recalculation

When user modifies

Vehicle Diameter

Only affected modules

shall be recomputed.

Previously valid results

shall remain cached.

Example

Vehicle

↓

Hydrodynamics

↓

Control

↓

Geometry

↓

Optimization

CAD

Simulation

Reports

GUI settings shall not trigger engineering recalculation.

---

# Caching

Cache

Engineering Models

Interpolation Results

Airfoil Lookups

Optimization Evaluations

Geometry Calculations

Simulation Exports

Every cache entry shall include

Version

Timestamp

Hash

Dependencies

Cache shall invalidate automatically when upstream inputs change.

---

# Parallel Execution

Independent modules may execute simultaneously.

Examples

Structural Validation

Servo Validation

Manufacturing Validation

can execute after

Hydrodynamic Validation.

Optimization candidate evaluations

shall execute in parallel whenever possible.

---

# Progress Tracking

Report

Current Module

Current Step

Elapsed Time

Estimated Remaining Time

Completed Percentage

Warnings

Current Candidate

Optimization Iteration

The GUI shall receive progress updates asynchronously.

---

# Cancellation

User may cancel execution.

Every module shall periodically check

Cancellation Token.

Cancelled execution shall

Safely stop

Release resources

Preserve completed results

Avoid data corruption.

---

# Error Recovery

Module failures shall generate

Error

Warning

Information

Suggested Fix

Recovery Strategy

The engine shall continue executing

independent modules

whenever possible.

Fatal failures

shall terminate only the current pipeline.

---

# Retry Policy

Transient failures

may automatically retry

configurable number of times.

Permanent failures

shall never retry automatically.

Every retry shall be logged.

---

# Logging

Execution Log

contains

Module

Start Time

End Time

Duration

Inputs

Outputs

Warnings

Errors

Memory Usage

CPU Time

Cache Hits

Cache Misses

---

# Randomness

Optimization algorithms requiring randomness

shall use

ExecutionContext Random Seed.

Identical seed

must produce identical optimization history.

---

# Resource Management

Monitor

CPU

Memory

Disk Usage

Thread Count

Temporary Files

Automatically clean

temporary resources

after successful execution.

---

# Undo / Redo

Every completed execution

creates

Project Revision.

Undo

restores

previous immutable models.

Redo

reapplies

subsequent revisions.

---

# Background Execution

Long-running tasks

shall execute in background threads.

GUI shall remain responsive.

Progress updates

shall be thread-safe.

---

# Plugin Integration

Plugins shall register

Execution Nodes

Dependencies

Inputs

Outputs

The engine shall automatically insert

plugin nodes

into the execution graph.

Core code shall not require modification.

---

# Validation

Before execution

Validate

Project

Configuration

Models

Dependencies

Resources

After execution

Validate

Outputs

Consistency

Traceability

Cache Integrity

---

# Performance Metrics

Collect

Execution Time

CPU Time

Memory Usage

Parallel Efficiency

Cache Efficiency

Optimization Throughput

Export Time

Generate

Performance Report.

---

# Engineering Assumptions

Version 1 assumes

Single user

Single project

Local execution

CPU computation

Future versions

Distributed execution

Cloud workers

GPU acceleration

Remote optimization servers

Collaborative execution

---

# Rules for the AI Agent

1. Execute modules only through the Execution Engine.

2. Never allow direct module-to-module execution outside the dependency graph.

3. Keep every execution deterministic given identical inputs and random seeds.

4. Support incremental recalculation to avoid unnecessary computation.

5. Every execution step shall be observable through logs and progress updates.

6. Preserve completed results whenever execution is interrupted.

7. Cache only validated engineering models.

8. The Execution Engine shall remain independent of the GUI and external applications.


# Chapter 4.5 – Plugin & Extension Framework

## Objective

The objective of this chapter is to define a plugin architecture that allows new engineering capabilities to be added without modifying the core application.

The plugin framework shall support

• New engineering solvers

• Optimization algorithms

• Airfoil databases

• Material databases

• CAD exporters

• Simulation exporters

• Report generators

• AI assistants

• Custom validators

• Future third-party extensions

The engineering core shall remain unchanged regardless of the number of installed plugins.

---

# Design Philosophy

Plugins shall be

Independent

Versioned

Sandboxed

Discoverable

Replaceable

Backward Compatible

Every plugin shall interact only through public APIs.

---

# Plugin Categories

Support

Engineering Solver

Optimization

Database

CAD

Simulation

Visualization

Reporting

Manufacturing

AI Assistant

Utility

Each plugin category shall expose a standardized interface.

---

# Plugin Discovery

The application shall automatically discover plugins

from

plugins/

or

user-installed plugin directories.

Plugins shall register themselves during application startup.

No manual registration shall be required.

---

# Plugin Metadata

Each plugin shall provide

Plugin Name

Author

Version

Description

Supported Software Version

Dependencies

License

Website

Unique Identifier

Minimum API Version

Maximum API Version

---

# Plugin Lifecycle

Every plugin shall implement

initialize()

register()

execute()

shutdown()

cleanup()

The application shall manage lifecycle automatically.

---

# Plugin Interfaces

Examples

OptimizationPlugin

CADExporterPlugin

SimulationExporterPlugin

MaterialDatabasePlugin

AirfoilDatabasePlugin

ValidationPlugin

VisualizationPlugin

AIAdvisorPlugin

Future interfaces may be added without affecting existing plugins.

---

# Extension Points

Plugins may extend

Engineering Pipeline

Optimization Pipeline

GUI

Menus

Toolbars

Reports

Simulation Export

Project Templates

Context Menus

Settings

Visualization

---

# Dependency Management

Plugins may declare

Required Plugins

Optional Plugins

Minimum Version

Maximum Version

The application shall validate compatibility before loading.

---

# Isolation

Plugin failures

shall never crash

the application.

Each plugin shall execute within a protected boundary.

Errors shall be isolated.

---

# Security

Plugins shall not receive unrestricted filesystem access.

Permissions include

Read Project

Write Project

Network Access

Simulation Export

CAD Export

Cloud Access

AI Services

Users shall approve requested permissions.

---

# Configuration

Each plugin may expose

Configuration Pages

Preferences

Runtime Settings

Default Values

Settings shall be stored independently.

---

# Version Compatibility

The application shall support

Plugin API Versioning

Automatic compatibility checks

Deprecation warnings

Migration tools

---

# Plugin Repository

Future

Support

Official Plugin Repository

Version Updates

Plugin Search

Installation

Removal

Ratings

Digital Signatures

---

# Testing

Every plugin shall support

Self-test

Compatibility Test

Dependency Check

Performance Benchmark

Validation Test

---

# Logging

Plugin execution shall be logged

including

Execution Time

Warnings

Errors

Memory Usage

Plugin Version

API Version

---

# Validation

Verify

API compatibility

Dependency resolution

Permission approval

Configuration validity

Successful initialization

---

# Rules for the AI Agent

1. Never allow plugins to bypass the Engineering Core.

2. Keep plugin interfaces stable and versioned.

3. Isolate plugin failures from the main application.

4. Expose only public APIs to plugins.

5. Every plugin shall declare metadata and compatibility information.

6. Prevent plugins from modifying immutable engineering models directly.

7. Ensure plugins are discoverable without code changes.

8. Design the framework to support long-term extensibility.


# Chapter 4.6 – Public API & SDK Design

## Objective

The objective of this chapter is to define the official public programming interface (API) and Software Development Kit (SDK) for the AUV Fin Design Platform.

The API shall provide a stable, versioned interface for

• GUI

• Command Line Interface

• Python scripting

• Batch processing

• Automation

• External applications

• Future web services

The Engineering Core shall only be accessible through the public API.

---

# Design Philosophy

The API shall be

Stable

Versioned

Well documented

Strongly typed

Deterministic

Language agnostic

Every API call shall produce reproducible engineering results.

---

# API Layers

The SDK shall expose

Project API

Engineering API

Optimization API

Visualization API

Export API

Simulation API

Report API

Plugin API

No internal implementation details shall be exposed.

---

# Project API

Support

Create Project

Load Project

Save Project

Clone Project

Archive Project

Validate Project

List Revisions

Undo

Redo

Project Metadata

---

# Engineering API

Support

Vehicle Definition

Mission Definition

Material Definition

Servo Definition

Hydrodynamic Analysis

Control Allocation

Fin Sizing

Airfoil Analysis

Structural Analysis

Servo Analysis

Validation

Every analysis returns immutable engineering models.

---

# Optimization API

Support

Single Design Evaluation

Optimization Run

Resume Optimization

Pause

Cancel

Sensitivity Analysis

Robustness Analysis

Retrieve Pareto Front

Retrieve Candidate Designs

---

# CAD API

Support

Generate CAD

Export STEP

Export STL

Export DXF

Generate Drawings

Retrieve Geometry

Retrieve Mass Properties

---

# Simulation API

Support

Generate Simulation Package

Export Stonefish

Export Gazebo

Export ROS2 Configuration

Export Mission Files

Retrieve Simulation Parameters

---

# Report API

Support

Generate PDF

Generate HTML

Generate Markdown

Export CSV

Export JSON Archive

Retrieve Figures

Retrieve Tables

---

# Visualization API

Support

Geometry Preview

Airfoil Viewer

Optimization History

Stress Visualization

Pareto Viewer

Sensitivity Charts

3D Scene Export

---

# Batch Processing API

Support

Execute Multiple Projects

Parameter Sweep

Monte Carlo Study

Design Space Exploration

Automatic Report Generation

Parallel Execution

---

# Python SDK

Expose

Project

Vehicle

Mission

Optimizer

CADExporter

SimulationExporter

ReportGenerator

DesignAdvisor

Every object shall provide intuitive methods.

---

# Command Line Interface

Support

Create Project

Run Analysis

Run Optimization

Generate CAD

Generate Reports

Export Simulation

Batch Processing

Example

auvfin optimize project.afp

---

# API Versioning

Every public API shall include

Major Version

Minor Version

Patch Version

Breaking changes

shall only occur

during major releases.

---

# Error Handling

Every API call returns

Status

Warnings

Errors

Diagnostic Information

Execution Time

Recovery Suggestions

No raw exceptions shall cross the public API boundary.

---

# Thread Safety

API calls shall support

Concurrent read access

Independent project execution

Parallel optimization

Thread-safe caching

Future

Distributed execution.

---

# Authentication (Future)

Support

Local Mode

API Keys

OAuth

Role-based permissions

Cloud deployment

Version 1

Local execution only.

---

# Documentation

Automatically generate

Python Documentation

REST Documentation (future)

CLI Help

Examples

Tutorials

API Reference

---

# SDK Examples

Provide examples for

Creating a vehicle

Running optimization

Exporting CAD

Generating reports

Batch optimization

Plugin development

Every public function shall include example usage.

---

# Validation

Verify

Arguments

Units

Required fields

Model consistency

Version compatibility

Return informative diagnostics for invalid usage.

---

# Rules for the AI Agent

1. Keep the public API independent of the GUI implementation.

2. Never expose internal classes that are not part of the supported SDK.

3. Ensure all API functions are deterministic and versioned.

4. Every API method shall validate inputs before execution.

5. Return immutable engineering models from analysis functions.

6. Provide consistent naming across Python, CLI, and future REST interfaces.

7. Maintain backward compatibility wherever possible.

8. Treat the public API as a long-term contract with users and external developers.


# Chapter 5.1 – GUI Architecture & User Experience Design

## Objective

The objective of this chapter is to define the complete graphical user interface (GUI) architecture for the AUV Fin Design Platform.

The GUI shall provide an intuitive, responsive, and professional environment for engineering design while remaining independent of the Engineering Core.

The GUI shall never perform engineering calculations directly. All calculations shall be executed through the Public API and Execution Engine.

---

# Design Philosophy

The GUI shall be

Professional

Responsive

Minimalistic

Customizable

Dockable

Accessible

Cross-platform

Every interface element shall have a clear engineering purpose.

---

# Architectural Pattern

The GUI shall follow the Model-View-ViewModel (MVVM) architecture.

Model

↓

ViewModel

↓

View

The View shall never communicate directly with the Engineering Core.

---

# Main Window Layout

The default workspace shall consist of

----------------------------------------------------------

Menu Bar

Toolbar

----------------------------------------------------------

Project Explorer | 3D Viewport | Properties Panel

----------------------------------------------------------

Output Console

Progress Panel

Status Bar

----------------------------------------------------------

Every panel shall be dockable, resizable, hideable, and restorable.

---

# Menu Bar

Provide

File

Edit

View

Project

Engineering

Optimization

Simulation

CAD

Reports

Plugins

Window

Help

Each menu shall contain logically grouped actions.

---

# Toolbar

Provide quick access to

New Project

Open

Save

Undo

Redo

Run Analysis

Run Optimization

Generate CAD

Export Simulation

Generate Report

Settings

Help

Icons shall include descriptive tooltips.

---

# Project Explorer

Display the complete project hierarchy.

Example

Project

Vehicle

Mission

Materials

Servo

Hydrodynamics

Control

Geometry

Airfoil

Validation

Optimization

CAD

Simulation

Reports

Audit Trail

Nodes shall display validation status.

---

# 3D Viewport

Display

Vehicle Geometry

Fin Geometry

Coordinate Frames

CG

CB

Control Axes

Measurement Tools

Grid

Lighting

Camera Controls

Future

CFD visualization

Stress contours

Animation

---

# Properties Panel

Display editable properties for the selected object.

Support

Vehicle parameters

Mission parameters

Material properties

Servo specifications

Optimization settings

Simulation settings

Report options

Only configuration models shall be editable.

---

# Output Console

Display

Execution logs

Warnings

Errors

Diagnostic messages

Optimization progress

Plugin messages

Support filtering and search.

---

# Progress Panel

Display

Current task

Execution graph

Optimization iteration

Estimated completion time

CPU usage

Memory usage

Cancellation button

---

# Status Bar

Display

Current project

Units

Coordinate system

Execution state

Autosave status

Software version

---

# Dialogs

Provide

Project Wizard

Preferences

Optimization Setup

Material Editor

Servo Library

Plugin Manager

Export Wizard

About

All dialogs shall be non-blocking where practical.

---

# Themes

Support

Light

Dark

High Contrast

Future

Custom themes

---

# User Preferences

Store

Window layout

Recent projects

Units

Theme

Default folders

Preferred simulator

Preferred CAD

Autosave interval

---

# Notifications

Support

Information

Warning

Error

Success

Long-running task completion

Notifications shall not interrupt workflow.

---

# Keyboard Shortcuts

Support standard shortcuts

Ctrl+N

Ctrl+O

Ctrl+S

Ctrl+Z

Ctrl+Y

Ctrl+R

Ctrl+P

F1

Allow user customization.

---

# Drag and Drop

Support

Project files

Airfoil files

Material libraries

Mission templates

Plugin packages

---

# Accessibility

Support

Keyboard navigation

Screen readers

High DPI displays

Large fonts

High contrast mode

Scalable icons

---

# Internationalization

Prepare for

Multiple languages

Localized units

Date formats

Number formats

Version 1

English only

---

# Error Presentation

Errors shall display

Summary

Technical details

Suggested solution

Reference documentation

Copy-to-clipboard

Error ID

---

# Performance

The GUI shall remain responsive during

Optimization

Simulation export

CAD generation

Report generation

All long-running operations shall execute in background threads.

---

# Validation Indicators

Use visual indicators

Green

Validated

Yellow

Warning

Red

Error

Gray

Not executed

Display status consistently throughout the application.

---

# Rules for the AI Agent

1. Keep the GUI independent of engineering calculations.

2. Use MVVM architecture.

3. Support dockable and customizable workspaces.

4. Provide immediate visual feedback for validation states.

5. Never block the GUI during long-running engineering operations.

6. Expose all engineering functionality through intuitive workflows.

7. Maintain a clean, professional appearance suitable for engineering software.

8. Design the interface to remain scalable as new modules are added.


# Chapter 5.2 – Project Wizard & Guided Design Workflow

## Objective

The objective of this chapter is to define the Project Wizard and guided workflow used to create and configure new AUV fin design projects.

The Project Wizard shall provide a structured, step-by-step process that collects all required engineering inputs, validates them, and generates a complete project ready for analysis.

The wizard shall reduce user errors while remaining efficient for experienced users.

---

# Design Philosophy

The Project Wizard shall be

Guided

Progressive

Validated

Interruptible

Resumable

Template-driven

Suitable for both beginners and experienced engineers.

---

# Wizard Workflow

The default workflow shall be

Welcome

↓

Project Information

↓

Vehicle Definition

↓

Mission Definition

↓

Material Selection

↓

Servo Selection

↓

Optimization Settings

↓

Simulation & CAD Preferences

↓

Review

↓

Project Creation

---

# Step 1 – Welcome

Display

Application overview

Recent projects

Available templates

Example projects

Option to import an existing project.

---

# Step 2 – Project Information

Collect

Project Name

Author

Organization

Description

Units

Coordinate System

Target Simulator

Target CAD Software

Autosave preferences

Validate required fields before proceeding.

---

# Step 3 – Vehicle Definition

Collect

Hull Length

Hull Diameter

Hull Mass

Center of Gravity

Center of Buoyancy

Fin Configuration

Number of Fins

Fin Location

Water Type

Display a live schematic preview as values are entered.

---

# Step 4 – Mission Definition

Collect

Cruise Speed

Maximum Speed

Operating Depth

Desired Turning Radius

Turn Establishment Time

Mission Profile

Safety Margin

Operating Environment

Validate engineering feasibility.

---

# Step 5 – Material Selection

Allow users to

Choose from the material library

View mechanical properties

Compare materials

Create custom materials

Set manufacturing method

Display estimated structural suitability.

---

# Step 6 – Servo Selection

Allow users to

Browse servo library

Compare specifications

Select custom servo

View torque utilization estimate

Display compatibility warnings.

---

# Step 7 – Optimization Settings

Configure

Objectives

Constraints

Optimization Algorithm

Maximum Iterations

Stopping Criteria

Parallel Execution

Sensitivity Analysis

Advanced settings shall remain collapsed by default.

---

# Step 8 – Simulation & CAD Preferences

Configure

Preferred CAD format

Preferred simulator

Export directory

Drawing options

Mesh quality

Simulation package options

Future

Cloud simulation settings.

---

# Step 9 – Review

Display a complete summary

Project Information

Vehicle

Mission

Materials

Servo

Optimization

Export Settings

Highlight

Missing inputs

Warnings

Potential issues

Allow editing by returning to previous steps.

---

# Step 10 – Project Creation

Generate

Project Structure

Configuration Models

Engineering Models

Initial Validation

Execution Plan

DesignProject

Open the main workspace upon successful creation.

---

# Templates

Support predefined templates

Small Torpedo AUV

Medium Survey AUV

Large Inspection AUV

Research Prototype

Competition Vehicle

Blank Project

Users may create and save custom templates.

---

# Validation

Validate inputs continuously.

Examples

Positive dimensions

Reasonable operating speeds

Servo compatibility

Material completeness

Geometry consistency

Display errors immediately.

---

# Live Preview

Update

Vehicle schematic

Fin placement

Mission summary

Estimated project complexity

As user edits values.

---

# Navigation

Support

Next

Back

Cancel

Save Draft

Resume Later

Jump to completed steps

Do not allow skipping required sections.

---

# Help System

Each page shall include

Context-sensitive help

Engineering explanation

Recommended values

Reference equations

Links to documentation

---

# Import & Export

Support

Import configuration

Export wizard settings

Reuse previous projects

Share templates

---

# Accessibility

Support

Keyboard navigation

Screen readers

High DPI

Resizable dialogs

Large fonts

---

# Performance

Wizard startup

< 2 seconds

Step transitions

< 100 ms

Validation

Real-time

---

# Rules for the AI Agent

1. Guide users through a logical engineering workflow.

2. Validate inputs continuously rather than only at the end.

3. Provide live previews wherever possible.

4. Keep advanced settings hidden until requested.

5. Allow users to save and resume incomplete projects.

6. Support reusable templates for common vehicle types.

7. Present engineering guidance without overwhelming the user.

8. Generate a fully validated DesignProject before entering the main workspace.


# Chapter 5.3 – Main Workspace & Engineering Workflow

## Objective

The objective of this chapter is to define the primary engineering workspace used for designing, analyzing, optimizing, and validating AUV fin designs.

The workspace shall integrate all engineering tools into a cohesive, responsive environment while maintaining separation between the GUI and the Engineering Core.

---

# Design Philosophy

The workspace shall be

Engineering-focused

Workflow-oriented

Customizable

Responsive

Non-blocking

Scalable

Suitable for both single-monitor and multi-monitor environments.

---

# Workspace Layout

Default layout

--------------------------------------------------------------

Menu Bar

Toolbar

Workspace Selector

--------------------------------------------------------------

Project Explorer

↓

--------------------------------------------------------------

Properties Panel

↓

--------------------------------------------------------------

Central Engineering Workspace

↓

--------------------------------------------------------------

Output Console

↓

--------------------------------------------------------------

Status Bar

--------------------------------------------------------------

All panels shall be

Dockable

Resizable

Hideable

Restorable

---

# Workspace Modes

Support dedicated workspaces

Vehicle

Mission

Fin Design

Hydrodynamic Analysis

Structural Analysis

Servo Analysis

Optimization

Manufacturing

Simulation

Reports

Project Review

Users may switch between workspaces without losing state.

---

# Project Explorer

Display

Project hierarchy

Validation state

Execution state

Revision history

Generated outputs

Context menu

Rename

Duplicate

Delete

Export

Open

Compare

Search support

Collapse / Expand

---

# Properties Panel

Display editable configuration for

Vehicle

Mission

Material

Servo

Optimization

Simulation

Manufacturing

Read-only calculated engineering models shall be displayed separately.

---

# Engineering Dashboard

Display

Current project status

Validation summary

Analysis status

Optimization status

Recommended next action

Recent changes

System health

---

# Analysis Controls

Provide

Run Analysis

Run Selected Module

Revalidate

Cancel

Resume

Pause

Clear Cache

View Execution Graph

---

# Optimization Controls

Support

Start

Pause

Resume

Cancel

View Pareto Front

Candidate Browser

Sensitivity Analysis

Robustness Analysis

Export Results

---

# Design Comparison

Allow users to

Compare two or more candidate designs

Highlight differences

Display objective improvements

Compare stress

Compare drag

Compare servo utilization

Compare manufacturability

Generate comparison reports.

---

# History Manager

Display

Project revisions

Optimization history

Undo

Redo

Restore revision

Branch project

Merge future support

---

# Context Menus

Support

Right-click actions

Relevant to selected object only.

Examples

Vehicle

Run Hydrodynamics

Export Geometry

Duplicate

Reports

Generate PDF

Open HTML

Optimization

Export Pareto

---

# Search

Provide

Global search

Project search

Command search

Recent commands

Keyboard shortcut

---

# Filtering

Support filtering

Warnings

Errors

Completed analyses

Optimization candidates

Reports

Plugins

---

# Multi-document Support

Allow

Multiple projects

Side-by-side comparison

Tabbed interface

Independent execution

Independent autosave

---

# Workspace Customization

Allow users to

Move panels

Create layouts

Save layouts

Restore defaults

Export layouts

Import layouts

---

# Autosave

Automatically save

Project

Workspace layout

Panel positions

Open tabs

Selections

Console history

Recover after crash.

---

# Notifications

Display

Analysis complete

Optimization complete

Export complete

Warnings

Plugin updates

Background task completion

Notifications shall be non-intrusive.

---

# Background Tasks

Display

Task queue

Current task

Remaining tasks

Execution progress

Estimated completion

Cancellation

---

# Validation Status

Each engineering module shall display

Not Executed

Running

Validated

Warning

Error

Outdated

Validation state shall propagate through dependent modules.

---

# Collaboration (Future)

Prepare for

Shared projects

Comments

Review mode

Design approval

Change requests

Version comparison

Version 1

Single-user only.

---

# Keyboard Shortcuts

Support

Run Analysis

Ctrl+R

Optimize

Ctrl+Shift+R

Search

Ctrl+K

Save

Ctrl+S

Undo

Ctrl+Z

Redo

Ctrl+Y

Customize shortcuts.

---

# Performance

Workspace startup

< 3 seconds

Panel switching

< 100 ms

Property editing

Instant

Background execution

Always enabled

---

# Rules for the AI Agent

1. Keep engineering calculations outside the GUI.

2. Organize the workspace around engineering tasks rather than software modules.

3. Allow full customization without breaking workflows.

4. Keep calculated models read-only within the workspace.

5. Display validation status consistently across all panels.

6. Support simultaneous execution of multiple long-running tasks where practical.

7. Preserve workspace state across sessions.

8. Ensure the interface scales as future engineering modules are added.


# Chapter 5.4 – Visualization & Engineering Results System

## Objective

The objective of this chapter is to define the complete visualization system for the AUV Fin Design Platform.

The visualization system shall present engineering results in a clear, interactive, and scientifically accurate manner.

Visualization shall never modify engineering models. It is a read-only representation of validated engineering data.

---

# Design Philosophy

The visualization system shall be

Interactive

Responsive

Engineering-focused

Publication-quality

Extensible

Consistent

Every visualization shall be generated from immutable engineering models.

---

# Visualization Categories

Support

3D Geometry

Engineering Graphs

Validation Dashboards

Optimization Results

Simulation Preview

Manufacturing Preview

Report Figures

Comparison Views

---

# 3D Geometry Viewer

Display

Vehicle hull

Fins

Coordinate axes

Center of Gravity (CG)

Center of Buoyancy (CB)

Servo locations

Reference planes

Bounding box

Scale ruler

Grid

Users shall support

Rotate

Pan

Zoom

Section views

Exploded view

Orthographic view

Perspective view

Reset camera

Saved viewpoints

---

# Geometry Display Modes

Support

Solid

Wireframe

Transparent

Hidden-line

Shaded

Material-colored

Manufacturing view

Simulation view

---

# Measurement Tools

Allow measurement of

Length

Angle

Distance

Area

Chord

Span

Sweep angle

Thickness

Clearance

Display values in project units.

---

# Airfoil Viewer

Display

Airfoil geometry

Camber line

Thickness distribution

Pressure center

Control shaft location

Leading edge

Trailing edge

Mean aerodynamic chord

Compare multiple airfoils simultaneously.

---

# Hydrodynamic Graphs

Display

CL vs Angle of Attack

CD vs Angle of Attack

CM vs Angle of Attack

Lift-to-Drag Ratio

Reynolds effects

Polar curves

Operating point

Stall region

Multiple airfoils may be compared.

---

# Structural Visualization

Display

Stress distribution

Safety factor

Deflection

Twist

Root bending

Failure locations

Version 1

Analytical diagrams

Future

FEA contour visualization

---

# Servo Visualization

Display

Hinge moment

Servo utilization

Torque margin

Bearing loads

Shaft stress

Mechanical limits

Recommended operating range

---

# Optimization Visualization

Display

Objective history

Constraint violations

Pareto front

Candidate ranking

Convergence history

Parameter evolution

Design evolution

Optimization timeline

---

# Sensitivity Analysis

Display

Spider charts

Tornado charts

Heat maps

Correlation matrix

Parameter importance

Confidence intervals

---

# Validation Dashboard

Display

Overall project health

Hydrodynamic validation

Structural validation

Servo validation

Manufacturing validation

Simulation readiness

Traffic-light indicators

Green

Yellow

Red

Gray

---

# Manufacturing Preview

Display

Print orientation

Support regions

Estimated print volume

Estimated print time

Estimated material usage

Wall thickness

Minimum feature size

Overhang warning

Future

Toolpath preview

---

# Simulation Preview

Display

Joint locations

Reference frames

Thruster directions

Control axes

Sensor positions

Collision geometry

Mission path

Environment preview

---

# Comparison View

Compare

Two or more candidate designs

Geometry

Lift

Drag

Stress

Servo utilization

Manufacturing metrics

Objective values

Graphs shall synchronize automatically.

---

# Interactive Charts

Support

Zoom

Pan

Legend selection

Data cursor

Export

Filtering

Logarithmic scale

Linear scale

Multiple datasets

---

# Figure Export

Support export

PNG

SVG

PDF

High-resolution

Transparent background

Vector graphics

Publication-ready figures

---

# Report Integration

Every visualization shall support

Automatic inclusion in reports

Consistent numbering

Captions

Metadata

Traceability

---

# Performance

Viewport

60 FPS target

Chart updates

< 100 ms

Large optimization datasets

Lazy rendering

Progressive loading

GPU acceleration (future)

---

# Accessibility

Support

High contrast

Scalable fonts

Colorblind-safe palettes

Keyboard navigation

Screen readers where practical

---

# Plugin Support

Plugins may register

Custom charts

Custom viewers

Custom dashboards

Custom overlays

Custom report figures

Without modifying the visualization core.

---

# Rules for the AI Agent

1. Visualization shall remain read-only.

2. Every chart shall be generated from validated engineering models.

3. Support synchronized comparison between multiple designs.

4. Generate publication-quality figures.

5. Use consistent colors, labels, units, and terminology.

6. Optimize rendering for large datasets.

7. Allow plugins to extend the visualization framework.

8. Ensure every visualization is traceable to its source engineering model.


# Chapter 5.5 – Settings, Preferences & Workspace Personalization

## Objective

The objective of this chapter is to define the complete settings, preferences, and workspace personalization system for the AUV Fin Design Platform.

The settings system shall allow users to configure application behavior, engineering defaults, visualization preferences, and workspace layouts while preserving reproducibility of engineering calculations.

User preferences shall never modify validated engineering results.

---

# Design Philosophy

The settings system shall be

Centralized

Consistent

Persistent

Versioned

User-friendly

Non-destructive

Engineering settings shall be separated from user interface preferences.

---

# Settings Categories

Support

General

Appearance

Units

Engineering

Optimization

Visualization

Simulation

Manufacturing

Performance

Plugins

Keyboard Shortcuts

Workspace

Updates

Privacy

Advanced

---

# General Settings

Allow configuration of

Default project location

Recent projects limit

Language

Startup behavior

Autosave interval

Backup retention

Crash recovery

Confirmation dialogs

Notification preferences

---

# Appearance Settings

Support

Light theme

Dark theme

System theme

Accent colors

Icon size

Font size

High contrast mode

UI scaling

Window animations

---

# Units Management

Configure default units

Length

Mass

Force

Torque

Pressure

Stress

Velocity

Angle

Density

Temperature

Internally

SI units only.

Display units may vary.

---

# Engineering Defaults

Allow configuration of

Default safety factors

Material defaults

Manufacturing tolerances

Optimization defaults

Hydrodynamic correlation options

Numerical solver settings

Default airfoil

Default fin configuration

---

# Optimization Settings

Configure

Optimization algorithm

Population size

Maximum generations

Convergence tolerance

Parallel execution

Random seed

Constraint handling

Stopping criteria

Advanced settings shall remain hidden unless enabled.

---

# Visualization Settings

Configure

Default chart style

Color palette

3D rendering quality

Grid visibility

Axis visibility

Lighting

Default camera

Animation speed

Figure export resolution

Colorblind-safe mode

---

# Simulation Settings

Configure

Preferred simulator

Export directory

Mesh quality

Coordinate system

Joint naming

ROS 2 options

Environment defaults

Mission template

---

# Manufacturing Settings

Configure

Preferred CAD format

Preferred slicer profile

Print orientation defaults

Support generation

Layer height

Infill defaults

Material profiles

Tolerance compensation

---

# Performance Settings

Configure

Maximum CPU usage

Memory limits

Number of worker threads

Cache size

GPU acceleration (future)

Lazy loading

Background task priority

Automatic cache cleanup

---

# Plugin Settings

Provide

Installed plugins

Enabled plugins

Disabled plugins

Plugin updates

Plugin permissions

Plugin diagnostics

Plugin configuration

---

# Keyboard Shortcuts

Allow users to

View

Edit

Import

Export

Reset

Search

Keyboard mappings

Support conflict detection.

---

# Workspace Personalization

Allow users to

Move panels

Resize panels

Create layouts

Save layouts

Rename layouts

Export layouts

Import layouts

Restore default layout

Assign layouts to tasks

---

# User Profiles

Support multiple profiles

Each profile stores

Preferences

Workspace layouts

Themes

Recent projects

Shortcuts

Plugin settings

Version 1

Local profiles only.

---

# Import & Export

Support export/import of

Settings

Workspace layouts

Keyboard shortcuts

Engineering defaults

Plugin configurations

Profiles

Use JSON or YAML.

---

# Validation

Validate

Numerical ranges

File paths

Plugin compatibility

Shortcut conflicts

Unit consistency

Theme compatibility

Display meaningful warnings.

---

# Reset Options

Support

Reset individual category

Reset selected settings

Factory reset

Reset workspace only

Reset shortcuts only

Confirmation required for destructive actions.

---

# Security & Privacy

Allow users to configure

Telemetry (future)

Crash report submission

Automatic update checks

Plugin permissions

Cloud synchronization (future)

Version 1

No telemetry by default.

---

# Accessibility

Support

High contrast

Large fonts

Keyboard navigation

Screen readers

Scalable icons

Reduced motion

---

# Performance Requirements

Settings dialog startup

< 1 second

Preference application

Instant where possible

Workspace switching

< 200 ms

Autosave

Background operation

---

# Rules for the AI Agent

1. Separate engineering defaults from interface preferences.

2. Never allow user preferences to modify validated engineering results.

3. Persist settings across sessions.

4. Support import/export of all configuration categories.

5. Validate all user-configurable values.

6. Provide sensible defaults while allowing advanced customization.

7. Ensure settings changes are reversible.

8. Keep the settings system extensible for future features.


# Chapter 6.1 – Airfoil Database Management System

## Objective

The objective of this chapter is to define the complete Airfoil Database Management System (ADMS) for the AUV Fin Design Platform.

The database shall provide validated airfoil geometry and aerodynamic performance data for engineering analysis, optimization, visualization, CAD generation, and simulation.

The system shall support both built-in and user-defined airfoils.

---

# Design Philosophy

The Airfoil Database shall be

Versioned

Extensible

Searchable

Validated

Cached

Traceable

Independent of the Engineering Core.

Engineering modules shall access airfoils only through the Airfoil Database API.

---

# Supported Airfoil Types

Support

Symmetric

Cambered

NACA 4-digit

NACA 5-digit

NACA 6-series

User-defined

Imported airfoils

Future

Hydrofoils

Custom optimized profiles

---

# Airfoil Record Structure

Each airfoil shall contain

Unique Identifier

Name

Family

Description

Author

Source

Version

Date Added

License

Tags

Geometry

Performance Data

Validation Status

---

# Geometry Data

Store

Upper surface coordinates

Lower surface coordinates

Leading edge radius

Trailing edge thickness

Maximum thickness

Thickness location

Maximum camber

Camber location

Chord normalization

Geometry shall use normalized coordinates.

---

# Performance Data

Store

Lift coefficient (CL)

Drag coefficient (CD)

Moment coefficient (CM)

Lift-to-drag ratio

Stall angle

Maximum lift coefficient

Pressure center

Transition point

Performance shall be indexed by

Reynolds number

Angle of attack

Mach number (future)

Surface roughness (future)

---

# Reynolds Number Support

Support multiple Reynolds datasets

Example

50,000

100,000

200,000

500,000

1,000,000

Interpolation between Reynolds numbers shall be supported.

---

# XFOIL Integration

Support importing

XFOIL polar files

Automatically detect

Headers

Units

Ncrit

Reynolds number

Data columns

Validate imported data.

---

# Supported File Formats

Import

DAT

CSV

TXT

JSON

Future

UIUC database

OpenVSP

XML

Export

JSON

CSV

DAT

---

# Database Organization

Organize by

Family

Thickness

Camber

Symmetry

Reynolds availability

Source

Tags

Manufacturer (future)

---

# Search

Support search by

Name

Family

Thickness

Camber

Maximum CL

Minimum Drag

Lift-to-drag ratio

Stall angle

Tags

Text search

Partial matches

---

# Filtering

Support filtering by

Symmetric

Cambered

Thickness range

Reynolds coverage

Validated only

Favorites

Recently used

User-defined

---

# Airfoil Comparison

Allow comparison of multiple airfoils

Display

Geometry

Thickness

Camber

Polar curves

Lift

Drag

Moment

Stall behavior

Operating point

Comparison shall synchronize across visualizations.

---

# Validation

Validate

Geometry continuity

Closed trailing edge

Coordinate ordering

Duplicate points

Polar consistency

Missing Reynolds datasets

Incomplete metadata

Generate validation reports.

---

# Caching

Cache

Geometry

Interpolated polars

Search results

Frequently used airfoils

Invalidate cache automatically after updates.

---

# User Airfoils

Allow users to

Import

Edit metadata

Validate

Store locally

Organize

Delete

Export

User airfoils shall remain separate from built-in data.

---

# Versioning

Track

Database version

Airfoil version

Import source

Modification history

Validation history

Migration history

---

# Plugin Support

Plugins may contribute

Airfoil databases

Polar generators

Geometry repair tools

Importers

Exporters

Visualization extensions

Without modifying the database core.

---

# Performance

Database startup

< 1 second

Search

< 100 ms

Interpolation

< 20 ms

Geometry retrieval

Instant

Support thousands of airfoils.

---

# Engineering Assumptions

Version 1 assumes

Low-speed incompressible flow

2D airfoil polars

XFOIL-generated data

Future

CFD-derived polars

Experimental databases

Compressibility corrections

3D finite-wing databases

---

# Rules for the AI Agent

1. Never access airfoil files directly from engineering modules.

2. Route all airfoil requests through the Airfoil Database API.

3. Validate every imported airfoil before making it available.

4. Preserve original imported data alongside processed data.

5. Keep user airfoils separate from built-in airfoils.

6. Cache interpolation results for performance.

7. Maintain complete version history for traceability.

8. Design the database to scale from hundreds to tens of thousands of airfoils.


# Chapter 6.2 – Material Database Management System

## Objective

The objective of this chapter is to define the complete Material Database Management System (MDMS) for the AUV Fin Design Platform.

The Material Database shall provide validated engineering properties for structural analysis, manufacturing planning, optimization, CAD generation, and reporting.

The database shall support both built-in engineering materials and user-defined custom materials.

---

# Design Philosophy

The Material Database shall be

Versioned

Validated

Extensible

Searchable

Traceable

Independent

Engineering modules shall access material data only through the Material Database API.

---

# Supported Material Categories

Support

PLA

PLA+

PETG

ABS

ASA

Nylon

Carbon Fiber Reinforced Nylon

Glass Fiber Reinforced Nylon

Polycarbonate

Aluminum

Titanium

Stainless Steel

Composite (future)

Custom materials

---

# Material Record Structure

Each material shall contain

Unique Identifier

Material Name

Category

Manufacturer (optional)

Grade

Description

Source

Version

Date Added

License

Tags

Mechanical Properties

Thermal Properties

Physical Properties

Manufacturing Properties

Validation Status

---

# Mechanical Properties

Store

Density

Young's Modulus

Shear Modulus

Bulk Modulus

Poisson's Ratio

Yield Strength

Ultimate Tensile Strength

Ultimate Compressive Strength

Ultimate Shear Strength

Fatigue Strength (optional)

Fracture Toughness (optional)

Hardness (optional)

---

# Physical Properties

Store

Density

Water Absorption

Moisture Expansion

Specific Heat

Thermal Conductivity

Electrical Conductivity

Magnetic Properties

Corrosion Resistance

UV Resistance

Chemical Resistance

---

# Thermal Properties

Store

Glass Transition Temperature

Melting Temperature

Heat Deflection Temperature

Maximum Continuous Service Temperature

Thermal Expansion Coefficient

Thermal Conductivity

---

# Manufacturing Properties

Store

Manufacturing Method

Recommended Layer Height

Recommended Nozzle Temperature

Recommended Bed Temperature

Print Speed

Cooling Recommendation

Shrinkage

Minimum Wall Thickness

Minimum Feature Size

Recommended Infill

Recommended Perimeters

Support Requirement

---

# Structural Design Parameters

Store

Recommended Safety Factor

Maximum Recommended Stress

Elastic Limit

Recommended Design Stress

Allowable Deflection

Allowable Strain

---

# Environmental Limits

Store

Maximum Water Depth

Saltwater Compatibility

Freshwater Compatibility

Temperature Range

UV Exposure Rating

Outdoor Suitability

---

# Search

Support search by

Material Name

Category

Density

Strength

Stiffness

Manufacturing Method

Temperature Range

Tags

Manufacturer

Partial text search

---

# Filtering

Support filtering by

Printable

Metal

Polymer

Composite

Water-resistant

High-strength

Lightweight

Validated

Favorites

Recently used

User-defined

---

# Material Comparison

Allow comparison of multiple materials

Display

Mechanical properties

Density

Strength

Stiffness

Thermal limits

Manufacturing recommendations

Radar charts

Tables

Engineering suitability

---

# User Materials

Allow users to

Create

Import

Edit metadata

Edit engineering properties

Validate

Store

Delete

Export

Custom materials shall remain separate from built-in materials.

---

# Import Formats

Support

JSON

CSV

YAML

Future

MaterialX

Engineering databases

Manufacturer catalogs

---

# Export Formats

Support

JSON

CSV

Engineering reports

Material summaries

---

# Validation

Validate

Required fields

Positive numerical values

Reasonable engineering ranges

Unit consistency

Duplicate materials

Missing metadata

Generate validation reports.

---

# Versioning

Track

Material version

Database version

Modification history

Validation history

Import history

Migration history

---

# Caching

Cache

Frequently used materials

Search results

Comparison results

Derived engineering properties

Invalidate automatically after updates.

---

# Plugin Support

Plugins may contribute

Material libraries

Manufacturer catalogs

Validation rules

Importers

Exporters

Material property estimators

Without modifying the database core.

---

# Engineering Assumptions

Version 1 assumes

Homogeneous materials

Isotropic behavior

Room-temperature properties

Static loading

Future

Anisotropic materials

Composite layups

Temperature-dependent properties

Moisture-dependent properties

Fatigue databases

Creep behavior

---

# Performance

Database startup

< 1 second

Material search

< 100 ms

Property retrieval

Instant

Comparison

< 100 ms

Support thousands of materials.

---

# Rules for the AI Agent

1. Never hardcode material properties inside engineering modules.

2. Route all material requests through the Material Database API.

3. Validate every imported material before use.

4. Preserve original imported records alongside processed data.

5. Keep user-defined materials separate from built-in materials.

6. Cache frequently accessed materials for performance.

7. Maintain complete version history for traceability.

8. Design the database for future support of advanced material models.


# Chapter 6.3 – Servo & Manufacturing Database Management System

## Objective

The objective of this chapter is to define the complete Servo & Manufacturing Database Management System (SMDMS) for the AUV Fin Design Platform.

The database shall provide validated engineering information for

• Servo selection

• Shaft sizing

• Bearings

• Linkages

• Manufacturing methods

• 3D printing

• CAD generation

• Structural analysis

• Manufacturing validation

The database shall support both built-in components and user-defined libraries.

---

# Design Philosophy

The database shall be

Versioned

Validated

Extensible

Searchable

Traceable

Plugin-ready

Independent of engineering modules.

All engineering modules shall retrieve manufacturing and actuator data exclusively through the Database API.

---

# Database Organization

The system consists of

Servo Library

↓

Transmission Library

↓

Bearing Library

↓

Manufacturing Library

↓

Machine Library

↓

Slicer Profile Library

↓

Tolerance Library

Each library shall be independently versioned.

---

# Servo Library

Each servo record shall contain

Unique Identifier

Manufacturer

Model

Description

Category

Version

Tags

---

# Servo Mechanical Properties

Store

Rated Torque

Peak Torque

Rated Voltage

Maximum Voltage

Speed

Maximum Rotation

Gear Material

Output Shaft Diameter

Weight

Dimensions

IP Rating

Operating Temperature

Efficiency

Backlash

Recommended Duty Cycle

Expected Lifetime

---

# Servo Electrical Properties

Store

Nominal Voltage

Maximum Current

Idle Current

Stall Current

PWM Range

Update Frequency

Signal Type

Connector Type

Cable Length

---

# Transmission Library

Store

Direct Drive

Gear Reduction

Belt Drive

Pushrod

Bell Crank

Rack and Pinion

Custom Linkage

For each

Efficiency

Backlash

Mechanical Advantage

Maximum Torque

Maximum Angle

Weight

Geometry Parameters

---

# Bearing Library

Store

Bearing Type

Inner Diameter

Outer Diameter

Width

Load Rating

Maximum RPM

Corrosion Resistance

Seal Type

Weight

Material

---

# Shaft Library

Store

Material

Diameter

Length

Yield Strength

Shear Strength

Density

Corrosion Resistance

Recommended Fit

Surface Finish

---

# Manufacturing Library

Support

FDM Printing

SLA Printing

SLS Printing

CNC Machining

Injection Molding

Composite Layup (future)

Each process stores

Capabilities

Limitations

Surface Finish

Tolerance

Minimum Feature Size

Maximum Build Volume

Recommended Materials

Cost Estimate

---

# Slicer Profile Library

Support

PrusaSlicer

OrcaSlicer

Bambu Studio

Cura

Simplify3D

Each profile stores

Layer Height

Perimeters

Top Layers

Bottom Layers

Infill

Pattern

Speed

Acceleration

Supports

Cooling

Nozzle Temperature

Bed Temperature

Brim

Raft

Adaptive Layers

Ironing

Pressure Advance

---

# Machine Library

Support

Common FDM Printers

Store

Manufacturer

Model

Build Volume

Maximum Temperature

Nozzle Sizes

Supported Materials

Maximum Speed

Acceleration

Firmware

Calibration Notes

---

# Tolerance Library

Store

Press Fit

Slip Fit

Running Fit

Bearing Fit

Servo Mount Fit

Shaft Fit

Hole Compensation

Shrinkage Compensation

Recommended Manufacturing Tolerances

---

# Search

Support

Manufacturer

Model

Torque

Weight

Voltage

Manufacturing Method

Printer

Material

Tolerance

Tags

Partial search

---

# Filtering

Support

Waterproof

High Torque

Metal Gear

Digital

Brushless

Printable

Validated

Favorites

Recently Used

User-defined

---

# Comparison

Allow comparison of

Servos

Printers

Manufacturing methods

Bearings

Transmissions

Shafts

Display

Tables

Radar Charts

Engineering Suitability

Compatibility

Estimated Cost

Estimated Weight

---

# Compatibility Engine

Automatically verify

Servo ↔ Shaft

Servo ↔ Linkage

Material ↔ Manufacturing

Printer ↔ Material

Bearing ↔ Shaft

Tolerance ↔ Manufacturing

Generate compatibility warnings.

---

# User Libraries

Allow users to

Create

Import

Edit

Delete

Export

Validate

User components remain separate from built-in libraries.

---

# Import Formats

Support

JSON

CSV

YAML

Manufacturer catalogs

Future

Online databases

---

# Export Formats

Support

JSON

CSV

Engineering reports

Manufacturing summaries

---

# Validation

Validate

Required fields

Positive dimensions

Reasonable engineering values

Duplicate entries

Metadata completeness

Compatibility rules

Generate validation reports.

---

# Versioning

Track

Component Version

Database Version

Modification History

Validation History

Migration History

Import Source

---

# Caching

Cache

Frequently used components

Compatibility checks

Search results

Comparison data

Automatically invalidate after updates.

---

# Plugin Support

Plugins may contribute

Servo libraries

Printer libraries

Machine profiles

Slicer profiles

Tolerance standards

Manufacturer catalogs

Compatibility rules

Without modifying the core database.

---

# Engineering Assumptions

Version 1 assumes

Commercial hobby servos

Metric hardware

FDM manufacturing

Standard bearings

Static tolerances

Future

Industrial actuators

Custom gearboxes

Smart servos

Composite manufacturing

Adaptive tolerances

---

# Performance

Database startup

< 1 second

Search

< 100 ms

Compatibility check

< 20 ms

Comparison

< 100 ms

Support tens of thousands of components.

---

# Rules for the AI Agent

1. Never hardcode actuator or manufacturing data inside engineering modules.

2. Route all requests through the Database API.

3. Validate every imported component before use.

4. Keep user libraries separate from built-in libraries.

5. Preserve original manufacturer specifications.

6. Cache compatibility results for performance.

7. Maintain complete version history.

8. Design the database for future industrial-scale expansion.


# Chapter 7.1 – Testing, Verification & Validation Strategy

## Objective

The objective of this chapter is to define the complete testing, verification, and validation (V&V) strategy for the AUV Fin Design Platform.

The testing framework shall ensure

• Engineering correctness

• Numerical stability

• Software reliability

• Reproducibility

• Regression protection

• Long-term maintainability

Every engineering calculation shall be independently verifiable.

---

# Design Philosophy

Testing shall follow

Verification

"Did we build the software correctly?"

Validation

"Did we build the correct engineering software?"

Testing shall be automated whenever practical.

---

# Testing Pyramid

The software shall implement

Unit Tests

↓

Integration Tests

↓

System Tests

↓

Engineering Validation Tests

↓

Acceptance Tests

Every layer shall execute independently.

---

# Unit Testing

Test every

Function

Method

Class

Utility

Validator

Serializer

Each test shall verify

Expected outputs

Boundary conditions

Invalid inputs

Numerical accuracy

Exception handling

Unit tests shall not require the GUI.

---

# Integration Testing

Verify interaction between

Vehicle Model

Mission Model

Hydrodynamics

Control Allocation

Airfoil Engine

Structural Solver

Servo Solver

Optimization

CAD

Simulation

Reporting

Ensure correct data flow.

---

# System Testing

Test complete engineering workflows

Example

Create Project

↓

Run Analysis

↓

Optimize

↓

Generate CAD

↓

Generate Report

↓

Export Simulation

Verify expected outputs.

---

# Engineering Validation

Validate against

Analytical solutions

Published literature

Reference calculations

Experimental data (future)

Benchmark problems

Known engineering examples

Document every benchmark.

---

# Numerical Verification

Verify

Interpolation accuracy

Optimization convergence

Finite precision

Unit conversions

Geometry calculations

Hydrodynamic equations

Structural equations

Servo equations

---

# Regression Testing

Every bug fix shall include

Regression test

Future software versions shall never reintroduce known failures.

---

# Performance Testing

Measure

Execution time

Memory usage

CPU utilization

Cache efficiency

Parallel scaling

Database performance

Generate benchmark reports.

---

# Stress Testing

Test

Large projects

Thousands of optimization candidates

Large airfoil databases

Long-running optimization

Memory exhaustion

Interrupted execution

Plugin failures

---

# Compatibility Testing

Verify

Operating systems

Python versions

Plugin API versions

CAD exporters

Simulation exporters

Database versions

---

# GUI Testing

Verify

Navigation

Dialogs

Workspace

Docking

Validation indicators

Accessibility

Keyboard shortcuts

Thread safety

Engineering calculations shall be mocked.

---

# Database Testing

Verify

Search

Filtering

Import

Export

Validation

Caching

Version migration

Performance

---

# Plugin Testing

Verify

Discovery

Loading

Execution

Compatibility

Permissions

Isolation

Failure recovery

---

# Serialization Testing

Verify

Save

Load

Migration

Backward compatibility

Project integrity

Corruption recovery

---

# Error Recovery Testing

Verify

Crash recovery

Autosave

Cancellation

Undo

Redo

Cache recovery

Project restoration

---

# Security Testing

Verify

Permission enforcement

Plugin isolation

Corrupted project handling

Invalid imports

Resource exhaustion

Future

Cloud authentication

---

# Continuous Validation

Every commit shall automatically execute

Unit Tests

Integration Tests

Regression Tests

Static Analysis

Formatting

Documentation checks

Performance smoke tests

---

# Test Data

Maintain

Reference projects

Reference airfoils

Reference materials

Reference servos

Reference optimization cases

Known analytical solutions

Benchmark reports

---

# Coverage

Target

Unit Test Coverage

>95%

Integration Coverage

Critical workflows

100%

Engineering validation

Every engineering module

---

# Test Reporting

Generate

Passed

Failed

Skipped

Coverage

Execution time

Memory usage

Regression summary

Validation summary

Store reports automatically.

---

# Engineering Assumptions

Version 1 validates against

Analytical equations

Published airfoil data

Reference optimization cases

Future

Experimental validation

CFD comparison

FEA comparison

Hardware-in-the-loop

Sea trials

---

# Rules for the AI Agent

1. Every engineering equation shall have at least one validation test.

2. Every discovered bug shall result in a regression test.

3. Keep GUI tests independent from engineering calculations.

4. Use deterministic inputs for reproducible testing.

5. Maintain a permanent benchmark suite.

6. Test every public API.

7. Automate all practical testing.

8. Treat engineering validation as equally important as software testing.


# Chapter 7.2 – Performance Engineering & Profiling

## Objective

The objective of this chapter is to define the complete performance engineering, profiling, and optimization strategy for the AUV Fin Design Platform.

The software shall provide responsive interaction while efficiently utilizing system resources during computationally intensive engineering tasks.

Performance optimization shall never compromise engineering correctness or numerical reproducibility.

---

# Design Philosophy

Performance engineering shall prioritize

Correctness

↓

Scalability

↓

Responsiveness

↓

Efficiency

↓

Optimization

Premature optimization shall be avoided.

---

# Performance Goals

Target

Application startup

< 3 seconds

Project loading

< 2 seconds

Database search

< 100 ms

Property editing

Instant

Chart updates

< 100 ms

3D viewport

60 FPS target

Engineering analysis

As fast as practical

Optimization

Parallel by default

---

# Profiling Strategy

Measure

CPU time

Wall-clock time

Memory usage

Disk I/O

Cache utilization

Thread utilization

GPU usage (future)

Database latency

Plugin execution time

Profiling shall be available in both development and release builds.

---

# Performance Metrics

Collect

Module execution time

Pipeline execution time

Optimization throughput

Candidate evaluations per second

Memory allocation

Peak memory

Cache hit ratio

Serialization time

Export time

Report generation time

---

# Engineering Pipeline Optimization

Optimize

Dependency resolution

Incremental recalculation

Parallel execution

Cache reuse

Lazy evaluation

Batch execution

Avoid unnecessary recomputation.

---

# Caching Strategy

Cache

Validated engineering models

Interpolated airfoil data

Optimization evaluations

Geometry calculations

Database queries

Visualization assets

Simulation exports

Cache invalidation shall be dependency-aware.

---

# Parallel Computing

Support parallel execution for

Optimization candidate evaluation

Sensitivity analysis

Monte Carlo studies

Batch processing

Database indexing

Report generation where applicable

Parallel execution shall preserve deterministic results.

---

# Memory Management

Monitor

Current memory usage

Peak memory usage

Large object allocation

Temporary buffers

Cache size

Automatically release unused resources.

Avoid memory leaks.

---

# Disk Performance

Optimize

Project save

Project load

Database access

Export generation

Cache storage

Autosave

Use asynchronous I/O where practical.

---

# Database Performance

Optimize

Search indexing

Filtering

Sorting

Interpolation lookup

Metadata retrieval

Version migration

Support datasets containing tens of thousands of records.

---

# Visualization Performance

Optimize

Geometry rendering

Chart rendering

Large optimization datasets

Animation

Selection updates

Level-of-detail rendering (future)

Progressive loading

GPU acceleration (future)

---

# Optimization Engine Performance

Measure

Candidate evaluations

Population throughput

Constraint evaluation time

Objective evaluation time

Convergence speed

Parallel efficiency

Stopping efficiency

---

# Plugin Performance

Measure

Startup time

Memory usage

Execution time

Initialization cost

Communication overhead

Plugins shall not significantly degrade application startup.

---

# Background Tasks

Execute

Optimization

Report generation

Simulation export

Large imports

Database indexing

without blocking the GUI.

---

# Resource Limits

Allow configuration of

Maximum CPU usage

Maximum memory

Worker thread count

Cache size

Disk cache limit

Background priority

Provide sensible defaults.

---

# Scalability

Design for

Small projects

Medium projects

Large optimization studies

Large databases

Multiple open projects

Future distributed computing

---

# Benchmark Suite

Maintain benchmark projects

Small torpedo AUV

Medium survey AUV

Large inspection AUV

Stress test projects

Database benchmarks

Optimization benchmarks

Benchmark results shall be version-controlled.

---

# Performance Regression

Automatically detect

Slower execution

Higher memory usage

Reduced cache efficiency

Longer startup

Larger binaries

Every release shall compare against previous benchmark results.

---

# Diagnostics

Provide developers with

Execution timeline

Memory timeline

Thread activity

Cache statistics

Database statistics

Plugin statistics

Export profiling

Visualization profiling

---

# Engineering Assumptions

Version 1 assumes

Single workstation

CPU computation

Local databases

Future

GPU acceleration

Distributed optimization

Cloud execution

Remote databases

---

# Rules for the AI Agent

1. Prioritize engineering correctness over execution speed.

2. Profile before optimizing.

3. Optimize complete workflows rather than isolated functions.

4. Cache only validated engineering results.

5. Preserve deterministic behavior during parallel execution.

6. Continuously benchmark critical engineering workflows.

7. Detect and report performance regressions automatically.

8. Design the software to scale gracefully as project complexity increases.


# Chapter 7.3 – Documentation Standards & Knowledge Management

## Objective

The objective of this chapter is to define the documentation strategy, standards, and knowledge management system for the AUV Fin Design Platform.

Documentation shall ensure that the software remains understandable, maintainable, reproducible, and extensible throughout its lifecycle.

Documentation shall be treated as a first-class engineering artifact.

---

# Design Philosophy

Documentation shall be

Complete

Accurate

Version-controlled

Traceable

Searchable

Automatically generated where practical

Every engineering decision shall be documented.

---

# Documentation Categories

Maintain

User Documentation

Developer Documentation

Engineering Documentation

API Documentation

Mathematical Documentation

Architecture Documentation

Database Documentation

Plugin Documentation

Testing Documentation

Release Documentation

---

# User Documentation

Provide

Installation Guide

Quick Start Guide

Tutorials

User Manual

Frequently Asked Questions

Troubleshooting Guide

Example Projects

Engineering Workflow Guide

Beginner and Advanced sections.

---

# Developer Documentation

Provide

Project Architecture

Folder Structure

Coding Standards

Contribution Guide

Development Setup

Build Instructions

Debugging Guide

Testing Guide

Performance Guide

Plugin Development Guide

---

# Engineering Documentation

Document

Design philosophy

Engineering assumptions

Model limitations

Validation approach

Applicable standards

References

Units

Coordinate systems

Safety factors

Every engineering module shall include theory documentation.

---

# Mathematical Documentation

For every engineering model provide

Equation

Variable definitions

Units

Assumptions

Derivation reference

Numerical method

Validation reference

Applicable operating range

Known limitations

Cite textbooks or papers where appropriate.

---

# API Documentation

Automatically generate

Public classes

Public methods

Parameters

Return types

Exceptions

Usage examples

Version history

Deprecation notices

Documentation shall remain synchronized with the codebase.

---

# Architecture Documentation

Maintain

System architecture

Module relationships

Execution pipeline

Dependency graph

Database architecture

Plugin architecture

Runtime architecture

Sequence diagrams

Data flow diagrams

Update after architectural changes.

---

# Database Documentation

Document

Schema

Field definitions

Validation rules

Version history

Migration strategy

Import/export formats

Supported datasets

---

# Plugin Documentation

Document

Plugin API

Lifecycle

Permissions

Extension points

Examples

Compatibility requirements

Migration guidance

---

# Testing Documentation

Document

Testing strategy

Benchmark projects

Validation datasets

Coverage reports

Regression history

Performance benchmarks

Known issues

---

# Release Documentation

Maintain

Release notes

Change log

Migration guide

Breaking changes

Deprecated features

Known issues

Upgrade instructions

Version compatibility

---

# Inline Documentation

Every public class shall include

Purpose

Responsibilities

Usage example

Dependencies

Related classes

Every public function shall include

Description

Parameters

Returns

Raises

Example

Engineering notes where appropriate.

---

# Code Comments

Use comments only for

Engineering reasoning

Algorithmic decisions

Non-obvious implementation details

Avoid comments that merely restate the code.

---

# Diagram Standards

Maintain

Class diagrams

Sequence diagrams

State diagrams

Execution graphs

Database diagrams

Deployment diagrams

Architecture diagrams

Use consistent notation.

---

# Knowledge Base

Maintain searchable knowledge base

Engineering FAQs

Common errors

Design recommendations

Validation references

Performance tuning

Plugin examples

Best practices

Future roadmap

---

# Documentation Generation

Automatically generate

API reference

Architecture overview

Coverage reports

Benchmark reports

Database reference

Plugin catalog

Engineering summaries

Use documentation generation tools integrated into the build process.

---

# Search

Support full-text search across

Documentation

Examples

API

Tutorials

Knowledge base

Release notes

Plugin documentation

---

# Versioning

Version

Documentation

API reference

Examples

Tutorials

Architecture

Synchronize documentation with software releases.

---

# Review Process

Documentation updates shall accompany

New features

Bug fixes

Architecture changes

Database changes

API changes

Engineering model updates

Documentation review is mandatory before release.

---

# Engineering Assumptions

Version 1

English documentation

Markdown source

HTML generation

PDF export

Future

Interactive documentation

Video tutorials

Multilingual documentation

Context-sensitive AI assistant

---

# Rules for the AI Agent

1. Treat documentation as part of the software, not an optional artifact.

2. Keep engineering theory synchronized with implementation.

3. Generate API documentation automatically whenever possible.

4. Document every public interface.

5. Include references for engineering equations and models.

6. Avoid duplicate documentation by generating reusable sources.

7. Version documentation alongside the codebase.

8. Ensure every engineering decision is traceable through documentation.


# Chapter 7.4 – Build System, CI/CD & Deployment

## Objective

The objective of this chapter is to define the complete build, continuous integration (CI), continuous deployment (CD), packaging, release, and deployment strategy for the AUV Fin Design Platform.

The software shall provide reproducible builds, automated quality assurance, reliable releases, and cross-platform deployment.

---

# Design Philosophy

The build and deployment system shall be

Automated

Reproducible

Deterministic

Versioned

Secure

Cross-platform

Every released version shall be reproducible from source.

---

# Build System

The project shall use

Python

Poetry (or uv)

PyProject.toml

Virtual environments

Dependency locking

Semantic versioning

Support

Development builds

Release builds

Debug builds

Nightly builds

---

# Dependency Management

Maintain

Core dependencies

Development dependencies

Testing dependencies

Documentation dependencies

Plugin SDK dependencies

Lock dependency versions for official releases.

---

# Continuous Integration

Every commit shall automatically execute

Static analysis

Formatting checks

Unit tests

Integration tests

Regression tests

Engineering validation

Documentation generation

Coverage reports

Package build

No code shall be merged if CI fails.

---

# Continuous Deployment

Automatically generate

Development builds

Nightly builds

Release candidates

Stable releases

Tag releases using semantic versioning.

---

# Static Analysis

Run

Type checking

Linting

Security scanning

Dependency vulnerability checks

Complexity analysis

Dead code detection

Duplicate code detection

Treat critical findings as build failures.

---

# Code Formatting

Automatically enforce

Formatting

Import ordering

Whitespace

Line length

Naming conventions

Formatting shall be deterministic.

---

# Testing Pipeline

Execute

Unit tests

Integration tests

System tests

Engineering validation

Performance smoke tests

Plugin compatibility tests

Database migration tests

Collect

Coverage

Execution time

Artifacts

---

# Documentation Pipeline

Automatically generate

API reference

Architecture documentation

Coverage reports

Benchmark reports

Plugin catalog

User documentation

Publish with every release.

---

# Packaging

Generate

Python package

Standalone desktop installer

Portable version

Wheel package

Source distribution

Support

Windows

Linux

macOS

---

# Installer

The installer shall support

Dependency validation

Desktop shortcuts

File associations

Optional sample projects

Optional documentation

Plugin installation

Safe uninstallation

---

# Release Management

Maintain

Release notes

Version history

Migration guides

Breaking changes

Known issues

Checksums

Digital signatures

---

# Artifact Management

Store

Installers

Packages

Documentation

Benchmark reports

Coverage reports

Reference datasets

Build logs

Artifacts shall be versioned and archived.

---

# Configuration Management

Version

Engineering defaults

Database schemas

Plugin API

Configuration files

Migration scripts

---

# Deployment Targets

Support

Local workstation

Laboratory workstation

Research cluster (future)

Cloud deployment (future)

Container deployment (future)

---

# Containerization

Prepare

Docker

Dev containers

Reproducible development environments

Version 1

Development support only.

---

# Plugin Deployment

Support

Plugin packaging

Plugin validation

Plugin signing

Plugin repository

Version compatibility

Safe updates

---

# Rollback

Support rollback of

Application version

Database schema

Plugins

Configuration

Project migration

Rollback shall preserve user projects.

---

# Security

Verify

Dependency integrity

Digital signatures

Checksums

Plugin authenticity

Secure downloads

Future

Signed releases

SBOM generation

---

# Telemetry

Version 1

Disabled by default

Future

Opt-in anonymous diagnostics

Crash reporting

Usage analytics

Users shall always control telemetry.

---

# Monitoring

Collect

Build success

Build duration

Test success

Coverage trends

Performance trends

Release metrics

No personal user data shall be collected without consent.

---

# Backup & Recovery

Support

Project backup

Autosave recovery

Configuration backup

Workspace backup

Version recovery

Installer recovery

---

# Engineering Assumptions

Version 1 assumes

Desktop application

Local execution

Manual installation

Future

Automatic updates

Cloud deployment

Enterprise deployment

Package repositories

---

# Rules for the AI Agent

1. Every commit shall pass automated quality checks.

2. Every release shall be reproducible from source.

3. Lock dependency versions for official releases.

4. Automate documentation, testing, and packaging.

5. Preserve backward compatibility where practical.

6. Version all engineering databases and configuration files.

7. Ensure rollback paths exist for releases and migrations.

8. Treat the build pipeline as part of the engineering process.


# Chapter 8.1 – Implementation Roadmap

## Objective

The objective of this chapter is to define the complete implementation roadmap for the AUV Fin Design Platform.

The roadmap shall guide development from an empty repository to a production-ready engineering application while minimizing technical debt and architectural rework.

Development shall be incremental, test-driven, and milestone-based.

---

# Design Philosophy

Development shall prioritize

Architecture

↓

Engineering correctness

↓

Core functionality

↓

User interface

↓

Optimization

↓

Advanced features

The architecture shall be stabilized before implementing engineering modules.

---

# Development Principles

Follow

Modular development

Domain-Driven Design

SOLID principles

Test-Driven Development where practical

Continuous Integration

Incremental delivery

Small, verifiable milestones

---

# Technology Stack

Programming Language

Python 3.12+

GUI

PySide6 (Qt)

Visualization

PyVista

VTK

Matplotlib

Plotly

Numerical Computing

NumPy

SciPy

Pandas

Optimization

pymoo

scikit-optimize

Geometry

CadQuery

OpenCascade

Data Validation

Pydantic v2

Serialization

JSON

SQLite

YAML

Documentation

MkDocs

Sphinx

Testing

pytest

pytest-qt

Coverage.py

Build System

Poetry (or uv)

CI/CD

GitHub Actions

Version Control

Git

---

# Phase 1 – Project Foundation

Objectives

Initialize repository

Configure build system

Configure dependency management

Establish coding standards

Create folder structure

Implement logging

Implement configuration system

Implement dependency injection

Deliverables

Clean repository

Passing CI

Developer documentation

---

# Phase 2 – Core Domain Models

Implement

DesignProject

VehicleModel

MissionModel

MaterialModel

ServoSpecification

GeometryModel

Validation framework

Serialization

Deliverables

Immutable engineering models

Save/load projects

Schema validation

---

# Phase 3 – Engineering Databases

Implement

Airfoil Database

Material Database

Servo Database

Manufacturing Database

Database API

Caching

Validation

Deliverables

Searchable databases

Import/export

Versioning

---

# Phase 4 – Engineering Core

Implement

Hydrodynamic estimator

Control allocation

Fin sizing

Airfoil engine

Hydrodynamic validation

Structural solver

Servo solver

Deliverables

Complete engineering pipeline

Validated benchmark cases

---

# Phase 5 – Optimization Engine

Implement

Objective functions

Constraints

Multi-objective optimization

Sensitivity analysis

Parallel execution

Optimization history

Deliverables

Optimization dashboard

Benchmark suite

---

# Phase 6 – CAD & Simulation

Implement

CAD generation

STEP export

STL export

Simulation export

Gazebo export

ROS 2 export

Future simulator adapters

Deliverables

Manufacturable CAD

Simulation-ready models

---

# Phase 7 – User Interface

Implement

Project wizard

Main workspace

Property editor

Visualization panels

Optimization dashboard

Reporting interface

Settings

Deliverables

Fully functional desktop application

---

# Phase 8 – Reporting

Implement

Engineering report generation

PDF export

HTML export

CSV summaries

Traceability

Validation summaries

Deliverables

Professional engineering reports

---

# Phase 9 – Plugin Ecosystem

Implement

Plugin loader

Plugin API

Plugin validation

Plugin marketplace structure

Developer SDK

Deliverables

Extensible architecture

Sample plugins

---

# Phase 10 – Quality Assurance

Complete

System testing

Engineering validation

Performance benchmarking

Documentation

Regression testing

Security review

Release preparation

Deliverables

Release candidate

---

# Milestones

M1

Project skeleton complete

M2

Core models complete

M3

Databases operational

M4

Engineering pipeline operational

M5

Optimization operational

M6

CAD generation operational

M7

GUI operational

M8

Reporting operational

M9

Plugin ecosystem operational

M10

Version 1.0 release candidate

---

# Coding Standards

Require

Type hints

Immutable models

Dependency injection

Small functions

Pure engineering calculations

No circular dependencies

No hardcoded engineering constants

---

# Risk Management

Identify

Architecture drift

Numerical instability

Performance degradation

Database inconsistency

Plugin incompatibility

Scope creep

Mitigate each risk with regular design reviews and automated testing.

---

# Deliverables

Each phase shall produce

Working software

Updated documentation

Passing tests

Updated benchmarks

Migration notes

Release notes

No phase is complete until all deliverables are satisfied.

---

# Success Criteria

The project is complete when

All SRDS requirements are implemented

Engineering validation passes

Performance targets are met

Documentation is complete

CI/CD is operational

Cross-platform builds succeed

Version 1.0 is releasable

---

# Future Roadmap

Version 1.1

GPU acceleration

Composite materials

Advanced optimization

Additional simulators

Version 2.0

CFD integration

FEA integration

Cloud collaboration

Distributed optimization

Digital twin support

AI-assisted engineering

---

# Rules for the AI Agent

1. Implement the software in the defined phase order.

2. Do not skip foundational architecture to build user-facing features.

3. Every completed phase shall have passing tests and documentation.

4. Validate engineering modules against benchmark problems before integration.

5. Avoid introducing technical debt to accelerate milestones.

6. Maintain backward compatibility wherever practical.

7. Update documentation, benchmarks, and tests alongside implementation.

8. Treat each milestone as a releasable, stable increment.


# Master AI Coding Prompt
## AUV Fin Design Platform

You are the lead software engineer responsible for implementing a professional Computer-Aided Engineering (CAE) application for designing, analyzing, optimizing, validating, and manufacturing fins for Autonomous Underwater Vehicles (AUVs).

Your objective is to produce production-quality software that strictly follows the Software Requirements & Design Specification (SRDS).

---

# Primary Objectives

Develop software that is

Engineering correct

Scientifically reproducible

Modular

Maintainable

Extensible

Well-tested

Well-documented

Production ready

Do not prioritize speed of implementation over engineering quality.

---

# Development Philosophy

Follow

Domain-Driven Design

SOLID Principles

Clean Architecture

Hexagonal Architecture

Immutable Engineering Models

Dependency Injection

Composition over Inheritance

Explicit Interfaces

High Cohesion

Low Coupling

---

# Engineering Principles

Never hardcode engineering constants.

Never duplicate engineering equations.

Every engineering equation must be traceable to a documented source.

Every engineering assumption must be documented.

Preserve numerical stability.

Maintain SI units internally.

Convert units only at the user interface.

Avoid hidden assumptions.

---

# Required Architecture

Implement

Presentation Layer

↓

Application Layer

↓

Engineering Core

↓

Optimization Engine

↓

Export Layer

↓

Persistence Layer

Use ports and adapters.

No GUI code may directly access engineering modules.

---

# Domain Models

Implement immutable models for

Project

Vehicle

Mission

Material

Servo

Hydrodynamics

Control Allocation

Candidate Fin

Airfoil

Validation

Optimization

CAD

Simulation

Reporting

Audit Trail

Validate all models using Pydantic.

---

# Engineering Pipeline

Implement

Vehicle estimation

↓

Hydrodynamic estimation

↓

Control requirement

↓

Control allocation

↓

Initial fin sizing

↓

Airfoil selection

↓

Lift iteration

↓

Hydrodynamic validation

↓

Structural validation

↓

Servo validation

↓

Optimization

↓

CAD generation

↓

Simulation export

↓

Engineering report

Each stage shall be independently testable.

---

# Coding Standards

Use

Python 3.12+

Type hints

Dataclasses or Pydantic

Meaningful naming

Pure functions where practical

Small methods

Single responsibility

No global state

No circular dependencies

Avoid magic numbers.

---

# Error Handling

Fail gracefully.

Provide meaningful engineering error messages.

Validate all inputs.

Preserve project integrity.

Recover safely whenever possible.

---

# Testing Requirements

Implement

Unit tests

Integration tests

System tests

Engineering validation

Regression tests

Performance benchmarks

No module is complete without tests.

---

# Documentation Requirements

Generate

API documentation

Engineering documentation

Architecture documentation

Developer documentation

User documentation

Synchronize documentation with implementation.

---

# Performance Requirements

Support

Parallel optimization

Incremental recalculation

Caching

Lazy evaluation

Background execution

Large databases

Multiple open projects

Never sacrifice correctness for speed.

---

# Database Rules

Use dedicated databases for

Airfoils

Materials

Servos

Manufacturing

Never embed engineering data inside source code.

Support import, export, versioning, validation, and search.

---

# Plugin Rules

Support plugins for

Engineering modules

Optimization algorithms

CAD exporters

Simulation exporters

Visualization

Databases

Plugins shall communicate only through public interfaces.

---

# User Interface

Use

PySide6

Dockable windows

MVVM architecture

Professional engineering workflow

Command palette

Workspace layouts

Interactive visualization

Never place engineering calculations inside GUI code.

---

# Optimization

Implement

Multi-objective optimization

Constraint handling

Sensitivity analysis

Pareto visualization

Optimization history

Parallel evaluation

Support future optimization algorithms.

---

# Visualization

Support

3D geometry

Airfoils

Hydrodynamic plots

Stress plots

Optimization plots

Sensitivity plots

Manufacturing preview

Simulation preview

Maintain responsive interaction.

---

# Reporting

Generate professional engineering reports containing

Inputs

Assumptions

Engineering calculations

Validation

Optimization

Manufacturing

CAD

Simulation

References

Traceability

Version information

---

# Quality Assurance

Every commit shall satisfy

Formatting

Static analysis

Type checking

Unit tests

Integration tests

Regression tests

Engineering validation

Documentation generation

Performance smoke tests

---

# CI/CD

Automate

Testing

Documentation

Packaging

Versioning

Release generation

Coverage reporting

Benchmark generation

---

# Security

Validate imports.

Protect project integrity.

Sandbox plugins.

Reject invalid engineering data.

---

# Future Compatibility

Design extension points for

CFD

FEA

GPU computing

Cloud execution

Distributed optimization

Digital twins

AI-assisted engineering

Composite materials

Additional simulators

---

# AI Development Rules

Before writing code

Understand the SRDS section being implemented.

Never skip architectural layers.

Prefer readability over cleverness.

When uncertain

Choose maintainability.

When multiple solutions exist

Choose the one that minimizes future technical debt.

Never introduce hidden engineering assumptions.

Always update

Tests

Documentation

Benchmarks

Migration notes

with every architectural change.

---

# Completion Criteria

A feature is complete only when

Implementation finished

Tests pass

Validation passes

Documentation updated

Benchmarks updated

CI passes

Code reviewed

No TODO placeholders remain.

---

# Deliverables

Produce

Production-quality source code

Comprehensive unit tests

Integration tests

Documentation

Engineering validation suite

Benchmark suite

Example projects

Developer guide

User guide

Release-ready artifacts

The resulting software shall be suitable for professional engineering use, research, academic publication support, and future industrial expansion.


