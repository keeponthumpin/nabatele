# Nabatele — Winch Show-Control & Preview System

Real-time TouchDesigner control and live-preview system for **Nabatele**, a helium-inflatable kinetic art installation by **Anna Kamyshan**, presented as a Collateral Event of the 61st Venice Biennale (16 Jul – 16 Sep 2026, Arsenale Nord).

---

## What it does

A ~30 m inflatable "rock" carrying a floating shtetl synagogue is suspended above a Venetian dry-dock basin, tethered by 12 motorised winches. **The system does not animate the structure — the wind does. The winches grant a controlled amount of freedom.**

This repo is the software that (a) drives the winch rig and (b) visualises its live state in 3D.

## The rig

- **Net buoyancy:** 80 kgf (785 N) up. CFD drag ~3380 N at the 10 m/s worst case (~4:1).
- **4 main tethers** — near-vertical, set height + pitch + roll (motion-base).
- **8 side tethers** — 2 ropes per drum, 8 winches, define the lateral freedom envelope.
- **Winches sit along the dock edge, not on a circle** (near 5.9 m / far 29.4 m) → CAD lookup table maps height + wind → 12 cable lengths.
- **Max fly height:** 43 m above quay. Landed Y = −1110 mm (pontoon below quay).

## Operating modes

| Mode | Wind | Behaviour |
|------|------|-----------|
| **1 — Free float** | <5 kn | Wind sets position, winches passive. Validated pendulum regime. |
| **2 — Winch automatic** | 8–20 kn | Solver predicts pose from wind → distributes tension across 12 winches. *The hard mode.* |
| **3 — Winch manual** | 8–20 kn | Operator drives target, solver enforces geometry constraints. |
| **4 — Home** | — | Sequenced retract to land on pontoon. Process TBD; needs Aerotrope sign-off. |

**Prime failure mode:** side tethers taut while mains go slack → main winch drums foul → loss of control. Governs Mode 2 and the Mode 4 descent.

## Architecture (`DD_NETWORK`, TD 2025.32460)

Left→right data-flow chain plus cross-cutting modules:

```
INITIAL DATA → PATTERN CREATOR → PLAYER → SYSTEM FEEDBACK → OUTPUT
                                   ↑ ↓
                    SYSTEM (ingress) · UI · PREVIEW
```

- **Initial Data** — static geometry (12 winch XYZ, attach points, dock) as SOP point data.
- **Pattern Creator** — abstract motion choreography.
- **Player** — runtime solver: pattern × live wind → 12 rope lengths (pendulum/CDPR model). Purely internal.
- **System** — single external ingress (Windy API, sensors, overrides).
- **System Feedback** — egress (logging, return paths).
- **Output** — pure sink: DMX map, IPs, Art-Net/sACN. No logic.

## Core abstraction

**One state variable per winch: cable-out length.** Everything — DMX value, pose, mode logic — derives from the geometry chain:

```
structure pose + surveyed winch position → straight-line distance → cable-out length → drum value → DMX
```

Calibration is by **on-site datum capture**: tension each cable taut at a known pose, read the DMX value as the MF-zero datum — no dependence on Wahlberg dead-length specs up front.

## Math model

Cable-driven parallel robot (CDPR) — 6-DOF rigid body, static force balance `W·t = −w_ext` (6×12 wrench matrix). Redundancy (12 unknowns, 6 equations) is the designed-in freedom envelope, solved per frame as a constrained QP. Drag law `F = k·v²`, **k ≈ 33.44 N/(m/s)²**, validated against Aerotrope CFD to ~6%.

## Hardware interface

- **Winches:** Wahlberg Winch 100 (mains) / Winch 50 (candidate for sides). DMX-512, 6 ch each → 72 ch, fits one universe over Art-Net/sACN.
- **Boundary:** software-only. Interface to Wahlberg is a DMX addressing handshake — we supply universe + channel block, they return node IPs. All physical rigging is theirs.

## Stack

- **TouchDesigner 2025.32460** — control + preview
- **GLSL compute shaders** — pendulum/physics offset
- **Python** — winch dataclasses, `tdu.Dependency` reactive binding, Script SOP geometry
- **Windy meteostation API** (`PWS_VENEZIA1`) — live Venice wind via non-blocking curl subprocess
- **Art-Net / DMX-512** — winch control protocol

## Known blockers

- ★ Tether length vs winch travel (41.2 m needed vs 25 m max).
- ★ Encoder/position readback — is raw drum position exposed anywhere?
- ★ Surveyed XYZ of all 12 winch mounts + 12 attachment points.
- ★ CAD lookup table from Aerotrope.
- Mode 2 stability/control law; Mode 4 Home sequence (process TBD).

---

*Owner: Alex Mashurov. Status: scoping. Single source of truth: Notion master file.*
