---
title: PDDL Domain (untyped STRIPS)
language: PDDL 1.2
source: IPC98GripperArchive
notes: Canonical IPC 1998 untyped formulation. Object types encoded as unary predicates (room, ball, gripper). Compatible with all PDDL 1.x planners.
instances_description: "Instances parameterised by number of balls n. Optimal plan length follows the formula 4⌈n/2⌉ + ⌊n/2⌋ − 1."
generator_note: "Instances are fully determined by n. All balls start in rooma; all must reach roomb. Robot starts in rooma with both grippers free. IPC 1998 instances: https://github.com/potassco/pddl-instances/tree/master/ipc-1998/domains/gripper-round-1-strips"
---

## State Space

A state specifies the room containing the robot, which balls are in which rooms, and which balls are carried by each gripper. For n balls and 2 grippers the state space is O(2ⁿ × n) — exponential in the number of balls.

## Objects

Two rooms, n balls, and two named grippers (left, right).

## Predicates

| name | desc |
|---|---|
| room(?r) | r is a room |
| ball(?b) | b is a ball |
| gripper(?g) | g is a gripper |
| at-robby(?r) | the robot is in room r |
| at(?b, ?r) | ball b is in room r |
| free(?g) | gripper g holds nothing |
| carry(?b, ?g) | gripper g is carrying ball b |

## Actions

#### move(from, to) — move the robot between rooms
```
preconditions: room(from) ∧ room(to) ∧ at-robby(from)
add effects:   at-robby(to)
del effects:   at-robby(from)
```

#### pick(ball, room, gripper) — pick up a ball in the current room
```
preconditions: at(ball, room) ∧ at-robby(room) ∧ free(gripper)
add effects:   carry(ball, gripper)
del effects:   at(ball, room), free(gripper)
```

#### drop(ball, room, gripper) — drop a carried ball in the current room
```
preconditions: carry(ball, gripper) ∧ at-robby(room)
add effects:   at(ball, room), free(gripper)
del effects:   carry(ball, gripper)
```

## Goal

All n balls must be at the destination room. Gripper positions are unconstrained.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| instance-01 | 2 | 5 | proven optimal | | instances/instance-01.pddl |
| instance-02 | 4 | 9 | proven optimal | | instances/instance-02.pddl |
| instance-03 | 6 | 13 | proven optimal | | instances/instance-03.pddl |
| instance-04-odd | 3 | 9 | proven optimal | | instances/instance-04-odd.pddl |
| ipc98-gripper-s1 | 2 | 5 | proven optimal | IPC98GripperArchive | |
| ipc98-gripper-s4 | 4 | 9 | proven optimal | IPC98GripperArchive | |
