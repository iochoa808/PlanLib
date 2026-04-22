---
title: PDDL Domain (3-operator)
language: PDDL 2.1
notes: Merges pick-up/unstack into move(b, from) and put-down/stack into place(b, to), where from/to range over a shared location type covering both blocks and the table. Requires :typing and :equality. Semantics are equivalent to the 4-operator domain.
---

## State Space

Identical to the 4-op domain. The reduced operator set does not change reachability, only branching factor at each state.

## Types

Two types: `block` and `location`. The table constant and all blocks share the `location` type, allowing a single pair of operators to handle both pick-up/unstack and put-down/stack uniformly.

## Objects

All blocks as type `block`; the table constant as type `location`. Every `block` is also a `location`.

## Predicates

| name | desc |
|---|---|
| on(b, x) | block b is directly on top of location x |
| clear(x) | nothing is stacked on top of location x |
| holding(b) | the arm is currently holding block b |
| handempty | the arm holds no block |

## Actions

#### move(b - block, from - location) — pick up a block from any location
```
preconditions: clear(b) ∧ on(b, from) ∧ handempty
add effects:   holding(b), clear(from)
del effects:   on(b, from), handempty
```

#### place(b - block, to - location) — place a held block onto any location
```
preconditions: holding(b) ∧ clear(to)
add effects:   on(b, to), handempty
del effects:   holding(b), clear(to)
```

## Goal

A conjunction of on(·,·) literals.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| sussman-3op | 3 | 6 | proven optimal | Sussman73 | instances/sussman_3op.pddl |
