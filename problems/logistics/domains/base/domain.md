---
title: PDDL Domain (untyped STRIPS)
language: PDDL 1.2
source: IPC98Archive
notes: Untyped formulation from IPC 1998 Round 2. Object categories (package, truck, airplane, city, location, airport) are encoded as unary predicates. Compatible with all PDDL 1.x planners.
instances_description: "Instances of increasing size. n is the number of packages; k* is the optimal plan length where known."
generator_note: "Instances are parameterised by number of packages, cities, locations per city, trucks, and airplanes. IPC 1998 STRIPS instances: https://github.com/potassco/pddl-instances/tree/master/ipc-1998/domains/logistics-round-2-strips"
---

## State Space

A state describes the location of every package (at a place or inside a vehicle) and the location of every vehicle (at a place). Cities and the in-city relation are static. The state space grows exponentially in the number of packages and vehicles.

## Objects

Cities, places (locations and airports), packages, trucks, and airplanes. Airports are places accessible to airplanes; trucks are restricted to locations within a single city.

## Predicates

| name | desc |
|---|---|
| package(?x) | x is a package |
| truck(?x) | x is a truck |
| airplane(?x) | x is an airplane |
| location(?x) | x is a location |
| airport(?x) | x is an airport (also a location) |
| city(?x) | x is a city |
| in-city(?l, ?c) | place l is in city c (static) |
| at(?x, ?l) | object x is at place l |
| in(?pkg, ?v) | package pkg is inside vehicle v |

## Actions

#### load-truck(pkg, truck, loc) — load a package onto a truck
```
preconditions: at(truck, loc) ∧ at(pkg, loc)
add effects:   in(pkg, truck)
del effects:   at(pkg, loc)
```

#### unload-truck(pkg, truck, loc) — unload a package from a truck
```
preconditions: at(truck, loc) ∧ in(pkg, truck)
add effects:   at(pkg, loc)
del effects:   in(pkg, truck)
```

#### drive-truck(truck, from, to, city) — drive between locations in the same city
```
preconditions: at(truck, from) ∧ in-city(from, city) ∧ in-city(to, city)
add effects:   at(truck, to)
del effects:   at(truck, from)
```

#### load-airplane(pkg, airplane, airport) — load a package onto an airplane
```
preconditions: at(airplane, airport) ∧ at(pkg, airport)
add effects:   in(pkg, airplane)
del effects:   at(pkg, airport)
```

#### unload-airplane(pkg, airplane, airport) — unload a package from an airplane
```
preconditions: at(airplane, airport) ∧ in(pkg, airplane)
add effects:   at(pkg, airport)
del effects:   in(pkg, airplane)
```

#### fly-airplane(airplane, from, to) — fly between airports
```
preconditions: at(airplane, from)
add effects:   at(airplane, to)
del effects:   at(airplane, from)
```

## Goal

A conjunction of at(pkg, loc) literals specifying the desired final location of each package. Vehicle positions are unconstrained in the goal.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| instance-01 | 1 | 6 | proven optimal | | instances/instance-01.pddl |
| instance-02 | 2 | 14 | proven optimal | | instances/instance-02.pddl |
| instance-03 | 4 | - | unknown | | instances/instance-03.pddl |
| ipc98-log-s1 | 5 | - | unknown | IPC98Archive | |
