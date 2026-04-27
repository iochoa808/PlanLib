---
title: "Extended Data Structures"
language: PDDL-XDS
source: Isaac26
notes: "Non-standard PDDL-XDS formulation using bounded-integer types and array mutation. The stack is a single array variable; the flip action performs an in-place reversal of the prefix [0..?f] in one step. Much more compact than the relational typed variant."
instances_description: "Parameterised by n (number of pancakes), encoded as a bounded integer type (number 0 n-1). The array stack has exactly n slots."
generator_note: "Instances are described by the initial permutation of the array; goal is always the sorted order."
---

## State Space

A state is an assignment of the array `pancake_stack` of length n. Unlike the relational typed variant, the entire stack is captured by a single array-valued function rather than n separate `at` ground atoms. The state space has n! states.

## Types

| name | parent |
|---|---|
| pancakes | (number 0 4) |
| stack | (array 5 pancakes) |

## Predicates

| name | desc |
|---|---|
| pancake_stack: stack | the array holding all n pancake values (indices 0..n−1, top to bottom) |

## Actions

#### flip(?f - pancakes) — Reverse the prefix of the stack from index 0 to index ?f
```
preconditions: -
add effects:   ∀ i ∈ [0, ?f]: pancake_stack[i] := pancake_stack[?f − i]
del effects:   (implicit: old values of pancake_stack[0..?f] are overwritten)
```

The array update is expressed as a bulk assignment using PDDL-XDS array-mutation syntax. All positions outside [0..?f] are unaffected.

## Goal

The array `pancake_stack` is non-decreasing: `pancake_stack[i] = i` for all i ∈ [0, n−1] (sorted ascending, smallest value at index 0).

## Instances

| name | n | k* | status | source | file | description |
|---|---|---|---|---|---|---|
| Simple_instance_0 | 5 | 2 | proven optimal | | instances/simple-instance-0.pddl | Initial stack [4,5,3,2,1] (index 0=top); sorted in 2 flips |
