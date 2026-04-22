---
title: PDDL Domain (typed STRIPS)
language: PDDL 2.1
source: IPC02DepotsArchive
notes: Typed STRIPS formulation from IPC 2002. Combines Blocksworld stacking with Logistics transportation in a single domain.
instances_description: "Instances of increasing complexity combining transportation and stacking. IPC 2002 used 22 instances in the STRIPS track."
generator_note: "Instances are parameterised by number of depots, distributors, trucks, hoists, crates, and pallets. Official IPC 2002 STRIPS instances: https://github.com/potassco/pddl-instances/tree/master/ipc-2002/domains/depots-strips-automatic"
---

## State Space

A state specifies the location of every truck and crate (at a place or in a truck), the stacking configuration of crates on surfaces at each place, and whether each hoist is available or lifting. The state space is exponential in the number of crates.

## Types

Two-branch hierarchy. `place` covers locations where activity happens; `locatable` covers everything that can be moved or used.

```
place      > depot, distributor
locatable  > hoist, truck
           > surface > pallet, crate
```

Hoists are fixed at places and never move. Trucks and crates are mobile. Pallets are fixed surfaces; crates become surfaces once placed, allowing stacking.

## Objects

Places (depots and distributors), locatables (hoists, crates, trucks), and surfaces (pallets and crates). Hoists are anchored to a place at problem initialisation.

## Predicates

| name | desc |
|---|---|
| at(x, p) | locatable x is at place p |
| on(c, s) | crate c rests on surface s |
| in(c, t) | crate c is inside truck t |
| lifting(h, c) | hoist h is holding crate c |
| available(h) | hoist h is not lifting anything |
| clear(s) | no crate rests on surface s |

## Actions

#### lift(h, c, s, p) — hoist picks up a crate from a surface
```
preconditions: at(h,p) ∧ available(h) ∧ at(c,p) ∧ on(c,s) ∧ clear(c)
add effects:   lifting(h,c), clear(s)
del effects:   available(h), at(c,p), on(c,s), clear(c)
```

#### drop(h, c, s, p) — hoist places a crate on a clear surface
```
preconditions: at(h,p) ∧ lifting(h,c) ∧ at(s,p) ∧ clear(s)
add effects:   available(h), at(c,p), on(c,s), clear(c)
del effects:   lifting(h,c), clear(s)
```

#### load(h, c, t, p) — hoist loads a lifted crate into a truck
```
preconditions: at(h,p) ∧ at(t,p) ∧ lifting(h,c)
add effects:   in(c,t), available(h)
del effects:   lifting(h,c)
```

#### unload(h, c, t, p) — hoist unloads a crate from a truck
```
preconditions: at(h,p) ∧ at(t,p) ∧ available(h) ∧ in(c,t)
add effects:   lifting(h,c)
del effects:   in(c,t), available(h)
```

#### drive(t, from, to) — truck drives between any two places
```
preconditions: at(t, from)
add effects:   at(t, to)
del effects:   at(t, from)
```

## Goal

A conjunction of on(c, s) literals specifying the desired stacking configuration at destination places.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| instance-01 | 1 | 5 | proven optimal | | instances/instance-01.pddl |
| instance-02 | 2 | - | unknown | | instances/instance-02.pddl |
| instance-03 | 3 | - | unknown | | instances/instance-03.pddl |
| ipc02-depots-s1 | - | - | unknown | IPC02DepotsArchive | |
