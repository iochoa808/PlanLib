---
title: "Typed Variant"
language: PDDL 2.1
source: Carla25
notes: "Typed PDDL 2.1 formulation using conditional effects and universal quantification. Positions are explicit objects; the flip geometry is encoded via auxiliary lte and flipat predicates set in the initial state."
instances_description: "Parameterised by n (number of pancakes). The flipat predicate encodes all n(n+1)/2 position-mapping pairs; lte encodes the n(n+1)/2 ordering pairs. Both are supplied in the initial state."
generator_note: "Instances can be generated for any permutation of n tiles by computing the lte and flipat tables."
---

## State Space

A state is a total assignment of tiles to positions: exactly one tile occupies each of the n positions. The `at` predicate encodes this bijection. Auxiliary predicates `lte` and `flipat` are fixed across all states (they are part of the problem geometry, not the dynamic state). The state space has n! states, one per permutation of n tiles, and n−1 applicable flip actions in every state.

## Types

| name | parent |
|---|---|
| tile | object |
| position | object |

## Predicates

| name | desc |
|---|---|
| at(?t - tile, ?p - position) | tile ?t is currently at position ?p |
| lte(?p1 - position, ?p2 - position) | position ?p1 is within the prefix ending at ?p2 (i.e. p1 ≤ p2 by index) |
| flipat(?pa - position, ?p - position, ?pnew - position) | flipping at ?pa maps position ?p to ?pnew |

## Actions

#### flip(?pala - position) — Reverse all tiles from the top down to position ?pala
```
preconditions: -
add effects:   (at ?tnext ?p) when (and (lte ?p ?pala) (at ?t ?p) (flipat ?pala ?p ?pnext) (at ?tnext ?pnext))
del effects:   (at ?t ?p) when (and (lte ?p ?pala) (at ?t ?p) (flipat ?pala ?p ?pnext) (at ?tnext ?pnext))
```

The conditional effects execute over all tuples (?t, ?tnext, ?p, ?pnext). In the pre-state: tile ?t sits at ?p, tile ?tnext sits at ?pnext, ?p falls within the flip prefix, and ?pnext is the mirror image of ?p under the flip. After the flip, ?tnext moves to ?p and ?t leaves ?p.

## Goal

All tiles are in sorted order: tile tᵢ occupies position pᵢ for every i, with tile t₁ (smallest) at the top position p₁ and tile tₙ (largest) at the bottom position pₙ.

## Instances

| name | n | k* | status | source | file | description |
|---|---|---|---|---|---|---|
| MyInstance | 5 | 2 | proven optimal | Carla25 | instances/myinstance.pddl | 5 pancakes in initial order [4,5,3,2,1] top-to-bottom; sorted in 2 flips |
