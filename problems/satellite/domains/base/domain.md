---
title: "Base formulation (IPC 2002)"
language: PDDL 2.1
source: Long03
notes: "Typed STRIPS-like formulation from IPC 2002. Power management is encoded with boolean predicates; no numeric fluents. All requirements are met through action sequencing alone."
instances_description: "Parameterised by number of satellites (s), instruments per satellite (i), imaging modes (m), and observation directions (d). Instance size is typically reported as the total number of observations required."
generator_note: "Original IPC 2002 instances are archived at https://github.com/potassco/pddl-instances/tree/master/ipc-2002/domains/satellite-strips-typed"
---

## State Space

A state records: the pointing direction of each satellite (`pointing`), the power state of each instrument (`power_on`, `power_avail`), the calibration state of each instrument (`calibrated`), and the set of observations already captured (`have_image`). Static predicates (`on_board`, `supports`, `calibration_target`) describe the hardware configuration and never change. The dynamic state space grows exponentially in the number of instruments and observation targets.

## Types

| name | parent |
|---|---|
| satellite | object |
| direction | object |
| instrument | object |
| mode | object |

## Predicates

| name | desc |
|---|---|
| on_board(?i - instrument, ?s - satellite) | instrument ?i is physically mounted on satellite ?s (static) |
| supports(?i - instrument, ?m - mode) | instrument ?i can capture images in mode ?m (static) |
| pointing(?s - satellite, ?d - direction) | satellite ?s is currently pointing at direction ?d |
| power_avail(?s - satellite) | satellite ?s has free power capacity (no instrument currently on) |
| power_on(?i - instrument) | instrument ?i is currently powered on |
| calibrated(?i - instrument) | instrument ?i has been calibrated since its last power-on |
| calibration_target(?i - instrument, ?d - direction) | instrument ?i must face direction ?d to be calibrated (static) |
| have_image(?d - direction, ?m - mode) | an image of direction ?d in mode ?m has been acquired |

## Actions

#### turn_to(?s - satellite, ?d_new - direction, ?d_prev - direction) — Slew satellite to a new pointing direction
```
preconditions: (pointing ?s ?d_prev)
add effects:   (pointing ?s ?d_new)
del effects:   (pointing ?s ?d_prev)
```

#### switch_on(?i - instrument, ?s - satellite) — Power on an instrument; consumes the satellite's power budget
```
preconditions: (on_board ?i ?s) ∧ (power_avail ?s)
add effects:   (power_on ?i)
del effects:   (power_avail ?s) (calibrated ?i)
```

#### switch_off(?i - instrument, ?s - satellite) — Power off an instrument; frees the power budget
```
preconditions: (on_board ?i ?s) ∧ (power_on ?i)
add effects:   (power_avail ?s)
del effects:   (power_on ?i)
```

#### calibrate(?s - satellite, ?i - instrument, ?d - direction) — Calibrate a powered instrument by pointing at its calibration target
```
preconditions: (on_board ?i ?s) ∧ (calibration_target ?i ?d) ∧ (pointing ?s ?d) ∧ (power_on ?i)
add effects:   (calibrated ?i)
del effects:   -
```

#### take_image(?s - satellite, ?d - direction, ?i - instrument, ?m - mode) — Capture a scientific image
```
preconditions: (calibrated ?i) ∧ (on_board ?i ?s) ∧ (supports ?i ?m) ∧ (power_on ?i) ∧ (pointing ?s ?d)
add effects:   (have_image ?d ?m)
del effects:   -
```

## Goal

Achieve a specified set of (direction, mode) image pairs. All required observations must be captured; `have_image` facts are never deleted so any order of acquisition is valid.

## Instances

| name | n | k* | status | source | file | description |
|---|---|---|---|---|---|---|
| instance-01 | 3 | 5 | proven optimal | Long03 | instances/instance-01.pddl | 1 satellite, 1 instrument, 2 directions, 1 mode; single observation required |
