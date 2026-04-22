---
title: PDDL Domain (typed STRIPS)
language: PDDL 2.1
source: IPC00LogArchive
notes: Full IPC 2000 type hierarchy. Requires :typing. Semantics identical to the base domain.
---

## State Space

Identical to the base domain. Type constraints reduce the number of groundings at no semantic cost.

## Types

A two-level hierarchy. At the top, `physobj` covers everything that moves; `place` covers everything that can be a location.

```
place   > airport, location
physobj > package
        > vehicle > truck, airplane
```

Trucks can only drive to `location` nodes; airplanes can only fly to `airport` nodes. Both subtypes of `place` are valid targets for at(·,·).

## Objects

Typed objects following the hierarchy above. In-city relations are still encoded as static predicates (not modelled as a type relationship).

## Predicates

| name | desc |
|---|---|
| in-city(?l - place, ?c - city) | place l is in city c (static) |
| at(?x - physobj, ?l - place) | object x is at place l |
| in(?pkg - package, ?v - vehicle) | package pkg is inside vehicle v |

## Actions

#### load-truck(pkg - package, truck - truck, loc - location) — load a package onto a truck
```
preconditions: at(truck, loc) ∧ at(pkg, loc)
add effects:   in(pkg, truck)
del effects:   at(pkg, loc)
```

#### unload-truck(pkg - package, truck - truck, loc - location) — unload a package from a truck
```
preconditions: at(truck, loc) ∧ in(pkg, truck)
add effects:   at(pkg, loc)
del effects:   in(pkg, truck)
```

#### drive-truck(truck - truck, from - location, to - location, city - city) — drive within a city
```
preconditions: at(truck, from) ∧ in-city(from, city) ∧ in-city(to, city)
add effects:   at(truck, to)
del effects:   at(truck, from)
```

#### load-airplane(pkg - package, airplane - airplane, airport - airport) — load onto airplane
```
preconditions: at(airplane, airport) ∧ at(pkg, airport)
add effects:   in(pkg, airplane)
del effects:   at(pkg, airport)
```

#### unload-airplane(pkg - package, airplane - airplane, airport - airport) — unload from airplane
```
preconditions: at(airplane, airport) ∧ in(pkg, airplane)
add effects:   at(pkg, airport)
del effects:   in(pkg, airplane)
```

#### fly-airplane(airplane - airplane, from - airport, to - airport) — fly between airports
```
preconditions: at(airplane, from)
add effects:   at(airplane, to)
del effects:   at(airplane, from)
```

## Goal

A conjunction of at(pkg, loc) literals.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| instance-01-typed | 1 | 6 | proven optimal | | instances/instance-01-typed.pddl |
| ipc00-log-typed-s1 | 5 | - | unknown | IPC00LogArchive | |
