---
id: prob004
slug: depots
title: Depots
subtitle: "Crates must be transported between depots and distributors using trucks, and stacked onto pallets using hoists. A deliberate combination of Blocksworld and Logistics that tests planners on interleaved transportation and stacking subgoals."
proposers: ["Maria Fox", "Derek Long"]
origin: "Fox & Long, IPC 2002"
origin_year: 2002
last_updated: "2025-01-01"
category: Classical
tags: [Classical, Fully Observable, Deterministic, Multi-Agent, Transportation, Stacking]
languages: [PDDL 2.1]
ipc_editions: [IPC 2002]
complexity_summary: {existence: PSPACE-complete, optimal: PSPACE-complete}
---

## Description

Crates must be transported from depots (sources) to distributors (destinations) by trucks. At each location, hoists stack crates onto pallets — making the local stacking problem equivalent to Blocksworld with a robot arm. Pallets are fixed in number and serve as the only valid base surfaces, playing the role of the table. Trucks can also act as temporary storage surfaces while hoists are repositioned.

## History

Depots was created by Maria Fox and Derek Long for IPC 2002 (the 3rd International Planning Competition) [FoxLong03] to test whether planners that perform well on Blocksworld and Logistics also perform well on their combination. The answer in practice was often no: the tight coupling between transportation and stacking subgoals exposed weaknesses in planners that handled each domain well in isolation. The domain appeared in four variants — STRIPS, numeric (fuel/weight), simple-time (fixed durations), and timed (distance-dependent durations).

## Variants

- [STRIPS (IPC 2002)](#domain-base)
- Numeric with fuel and weight constraints (IPC 2002)
- Simple-time with fixed durations (IPC 2002)
- Timed with distance-dependent durations (IPC 2002)

The STRIPS version is the base. In the numeric version, trucks consume fuel and crates have weights that determine hoist fuel use. In the timed version, durations depend on distance and hoist power.

## Complexity

| Problem | Qualifier | Result | Class |
|---|---|---|---|
| Plan existence | propositional STRIPS | PSPACE-complete | hard |
| Optimal plan length | | PSPACE-complete | hard |
