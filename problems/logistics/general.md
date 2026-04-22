---
id: prob002
slug: logistics
title: Logistics
subtitle: "Packages must be transported between locations in multiple cities using trucks for intra-city delivery and airplanes for inter-city transfer. A foundational benchmark for typed planning and multi-object goal interaction."
proposers: ["Manuela Veloso"]
origin: "Veloso, 1992 (PRODIGY)"
origin_year: 1992
last_updated: "2025-01-01"
category: Classical
tags: [Classical, Fully Observable, Deterministic, Multi-Object, Typed, Transportation]
languages: [PDDL 1.2, PDDL 2.1]
ipc_editions: [IPC 1998, IPC 2000]
complexity_summary: {optimal: PSPACE-complete, suboptimal: P}
---

## Description

Packages must be delivered to goal locations across a network of cities. Within a city, trucks can drive between any two locations. Between cities, airplanes fly between airports (a special kind of location). A package may require a truck to reach an airport, a flight to reach the destination city, and another truck to reach its final location.

## History

The domain was introduced by Manuela Veloso in her 1992 PhD thesis [Veloso92] as the primary benchmark for the PRODIGY planning system at Carnegie Mellon. It became the canonical multi-object transportation domain and was chosen as the running example in the original PDDL 1.2 specification [McDermott98], where it appears in both STRIPS and ADL formulations. The domain was used in IPC 1998 (rounds 1 ADL and 2 STRIPS) and IPC 2000 (typed and untyped STRIPS).

## Variants

- [Untyped STRIPS (IPC 1998)](#domain-base)
- [Typed STRIPS (IPC 2000)](#domain-typed)
- ADL with conditional effects (IPC 1998 Round 1)
- Temporal Logistics (durative actions)
- Numeric Logistics (fuel and capacity constraints)

The untyped STRIPS version encodes object categories as unary predicates. The typed version uses a full PDDL type hierarchy. The ADL variant uses conditional effects and was used in IPC 1998 Round 1. Zeno Travel (IPC 2002) is a related domain with fuel constraints.

## Complexity

| Problem | Qualifier | Result | Class |
|---|---|---|---|
| Plan existence | propositional STRIPS | PSPACE-complete | hard |
| Optimal plan length | | PSPACE-complete | hard |
| Satisficing plan | single package, one city | P | easy |
