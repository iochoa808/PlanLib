---
title: PDDL Domain (4-operator, untyped)
language: PDDL 1.2
source: FikesNilsson71
notes: Core STRIPS domain. Object types are not declared; predicates use untyped variables. Compatible with all PDDL 1.x and 2.x planners.
instances_description: "Benchmark instances of varying size. n is the number of blocks; k* is the proven optimal plan length unless marked otherwise."
generator_note: "Random instances are parameterised by n (number of blocks) and the number of target stacks. The official IPC 2000 instances are archived at https://github.com/potassco/pddl-instances/tree/master/ipc-2000/domains/blocks-strips-untyped"
---

## State Space

A state is a complete description of block positions. Each block is either on the table or on top of exactly one other block; at most one block may be held by the arm at any time. The state space size for n blocks grows as the n-th ordered Bell number — faster than exponential.

## Objects

A finite set of blocks B = {b₁, b₂, …, bₙ}, plus a special constant table and the robot arm.

## Predicates

| name | desc |
|---|---|
| on(b, x) | block b is directly on top of block x |
| ontable(b) | block b rests directly on the table |
| clear(b) | nothing is stacked on top of block b |
| holding(b) | the arm is currently holding block b |
| handempty | the arm holds no block |

## Actions

#### pick-up(b) — take a block from the table
```
preconditions: clear(b) ∧ ontable(b) ∧ handempty
add effects:   holding(b)
del effects:   clear(b), ontable(b), handempty
```

#### put-down(b) — place held block on the table
```
preconditions: holding(b)
add effects:   clear(b), ontable(b), handempty
del effects:   holding(b)
```

#### stack(b, x) — place held block on another block
```
preconditions: holding(b) ∧ clear(x)
add effects:   on(b,x), clear(b), handempty
del effects:   holding(b), clear(x)
```

#### unstack(b, x) — pick up a stacked block
```
preconditions: on(b,x) ∧ clear(b) ∧ handempty
add effects:   holding(b), clear(x)
del effects:   on(b,x), clear(b), handempty
```

## Goal

A partial state: a conjunction of on(·,·) and/or ontable(·) literals that must all hold simultaneously. Goals need not constrain every block.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| Sussman anomaly | 3 | 6 | proven optimal | Sussman73 | instances/sussman_anomaly.pddl |
| bw-prob-4-1 | 4 | 8 | proven optimal | | instances/bw_prob_4_1.pddl |
| bw-prob-5-1 | 5 | 12 | proven optimal | | instances/bw_prob_5_1.pddl |
| bw_large.a | 9 | 12 | proven optimal | KautzSelman96 | instances/bw_large_a.pddl |
| bw_large.b | 11 | 18 | proven optimal | KautzSelman96 | instances/bw_large_b.pddl |
| bw_large.c | 15 | 24 | proven optimal | KautzSelman96 | instances/bw_large_c.pddl |
| bw_large.d | 19 | 56 | proven optimal | KautzSelman96 | instances/bw_large_d.pddl |
| ipc00-blocks-35 | 35 | - | best-known only | IPC00Archive | |
