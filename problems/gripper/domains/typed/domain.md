---
title: PDDL Domain (typed STRIPS)
language: PDDL 2.1
source: McDermott98
notes: Typed formulation with explicit room, ball, and gripper types. Semantics identical to the base domain.
---

## State Space

Identical to the base domain.

## Types

Three flat types with no subtype hierarchy: `room`, `ball`, `gripper`. Typing replaces the unary category predicates with PDDL parameter declarations.

## Objects

Objects of types `room` (two rooms), `ball` (n balls), and `gripper` (two grippers: left, right).

## Predicates

| name | desc |
|---|---|
| at-robby(?r - room) | the robot is in room r |
| at(?b - ball, ?r - room) | ball b is in room r |
| free(?g - gripper) | gripper g holds nothing |
| carry(?b - ball, ?g - gripper) | gripper g is carrying ball b |

## Actions

#### move(from - room, to - room) — move the robot between rooms
```
preconditions: at-robby(from)
add effects:   at-robby(to)
del effects:   at-robby(from)
```

#### pick(ball - ball, room - room, gripper - gripper) — pick up a ball
```
preconditions: at(ball, room) ∧ at-robby(room) ∧ free(gripper)
add effects:   carry(ball, gripper)
del effects:   at(ball, room), free(gripper)
```

#### drop(ball - ball, room - room, gripper - gripper) — drop a carried ball
```
preconditions: carry(ball, gripper) ∧ at-robby(room)
add effects:   at(ball, room), free(gripper)
del effects:   carry(ball, gripper)
```

## Goal

All n balls at the destination room.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
