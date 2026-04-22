---
title: PDDL Domain (4-operator, typed)
language: PDDL 2.1
source: IPC00Archive
notes: IPC 2000 style. Adds :types block and uses ?b - block throughout, enabling type-based grounding pruning. Semantics are identical to the untyped domain.
---

## State Space

Identical to the untyped domain. Typed grounding reduces the search space by excluding ill-typed groundings at no semantic cost.

## Types

A single type `block` covers all stackable objects. The table constant remains untyped — it is a special surface, not a block, so it cannot appear as the subject of on(·,·).

## Objects

One object of type `block` per block. The table constant is shared across all instances.

## Predicates

| name | desc |
|---|---|
| on(b, x) | block b is directly on top of block x |
| ontable(b) | block b rests directly on the table |
| clear(b) | nothing is stacked on top of block b |
| holding(b) | the arm is currently holding block b |
| handempty | the arm holds no block |

## Actions

#### pick-up(b - block) — take a block from the table
```
preconditions: clear(b) ∧ ontable(b) ∧ handempty
add effects:   holding(b)
del effects:   clear(b), ontable(b), handempty
```

#### put-down(b - block) — place held block on the table
```
preconditions: holding(b)
add effects:   clear(b), ontable(b), handempty
del effects:   holding(b)
```

#### stack(b - block, x - block) — place held block on another block
```
preconditions: holding(b) ∧ clear(x)
add effects:   on(b,x), clear(b), handempty
del effects:   holding(b), clear(x)
```

#### unstack(b - block, x - block) — pick up a stacked block
```
preconditions: on(b,x) ∧ clear(b) ∧ handempty
add effects:   holding(b), clear(x)
del effects:   on(b,x), clear(b), handempty
```

## Goal

A conjunction of on(·,·) and/or ontable(·) literals.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| ipc00-typed-small | 5 | 8 | proven optimal | IPC00Archive | instances/ipc00_typed_small.pddl |
