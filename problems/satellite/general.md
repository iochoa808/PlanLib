---
id: prob007
slug: satellite
title: Satellite
subtitle: "Multiple orbiting satellites, each with calibrated instruments, must point to specified directions and capture images in required observation modes. A flagship benchmark from IPC 2002."
proposers: ["Maria Fox", "Derek Long"]
origin: "IPC 2002 (3rd International Planning Competition)"
origin_year: 2002
last_updated: "2026-04-27"
category: Classical
tags: ["Classical", "Fully Observable", "Deterministic", "Single Agent", "Typed PDDL"]
languages: ["PDDL 2.1"]
ipc_editions: ["IPC 2002", "IPC 2004", "IPC 2006"]
complexity_summary: {existence: PSPACE-complete, optimal: PSPACE-complete}
---

## Description

A fleet of satellites orbits in space; each satellite carries one or more scientific instruments. Every instrument supports a subset of imaging modes and has a designated calibration-target direction. To capture an image of a direction in a given mode, the hosting satellite must be pointing at that direction and the relevant instrument must be both powered on and calibrated since its last power cycle. Each satellite's power bus can only supply one instrument at a time: switching an instrument on uses all available power until it is switched off.

The goal specifies a set of (direction, mode) observations that must be acquired. The planner must sequence pointing manoeuvres, power management operations, calibration steps, and image-capture actions to satisfy all requirements while respecting the single-power-bus and calibration-dependency constraints.

## History

The Satellite domain was designed by Maria Fox and Derek Long for the 3rd International Planning Competition (IPC 2002), held in conjunction with AIPS 2002 [Long03]. It was conceived to stress typed PDDL, action-ordering constraints, and resource management beyond the simple boolean scheduling of earlier IPC domains. Satellite was one of the most challenging domains at IPC 2002 and required planners to reason about sequential dependencies among switch_on, calibrate, and take_image.

The domain reappeared at IPC 2004 in a numeric extension adding fuel consumption and data-storage capacity as numeric fluents [Fox03], and at IPC 2006 in a temporal version with durative slewing and observation actions.

## Variants

- [Base formulation (IPC 2002)](#domain-base)
- Numeric Satellite (fuel and data-capacity fluents, IPC 2004)
- Temporal Satellite (durative slewing and observation actions, IPC 2006)
- Hard Constraints (antenna exclusion zones, observation windows)

The numeric variant from IPC 2004 adds `fuel`, `fuel-use`, `slew-time`, `data`, and `data-capacity` numeric functions. The temporal variant uses durative actions and timed initial literals to model observation windows.

## Complexity

| Problem | Qualifier | Result | Class |
|---|---|---|---|
| Plan existence | classical typed formulation | PSPACE-complete | hard |
| Optimal plan length | | PSPACE-complete | hard |
| Satisficing plan | ignoring calibration dependencies | P | easy |
