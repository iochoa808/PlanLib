---
id: prob003
slug: gripper
title: Gripper
subtitle: "A robot with two grippers moves between rooms and transports balls. The canonical domain for studying the interaction between carrying capacity and heuristic quality."
proposers: ["IPC 1998 Organizers"]
origin: "IPC 1998"
origin_year: 1998
last_updated: "2025-01-01"
category: Classical
tags: [Classical, Fully Observable, Deterministic, Single Agent, Transportation]
languages: [PDDL 1.2, PDDL 2.1]
ipc_editions: [IPC 1998]
complexity_summary: {existence: PSPACE-complete, optimal: "4⌈n/2⌉+⌊n/2⌋−1"}
---

## Description

A robot equipped with two grippers moves between two rooms. All balls begin in one room and must be transported to the other. The robot can move between rooms, pick up a ball with a free gripper, or drop a carried ball. With two grippers the robot can carry two balls per trip, making the optimal plan significantly shorter than a naive one-ball strategy.

## History

Gripper was introduced as a benchmark in IPC 1998 [McDermott98], appearing in both the ADL round (typed) and the STRIPS round. It is the canonical domain demonstrating a fundamental failure mode of delete-relaxation heuristics: in the relaxed problem, a ball can be considered delivered without the gripper ever being freed, causing h⁺ to underestimate severely. Hoffmann and Nebel [HoffmannNebel01] used Gripper as the primary example showing that enforced hill-climbing in FF fails on this domain in default configuration.

## Variants

- [2-room STRIPS (IPC 1998)](#domain-base)
- [2-room ADL typed (IPC 1998)](#domain-typed)
- Multi-room Gripper
- n-gripper Gripper

The standard formulation has exactly 2 rooms and 2 grippers. Multi-room and n-gripper generalisations exist but are less commonly used.

## Complexity

| Problem | Qualifier | Result | Class |
|---|---|---|---|
| Plan existence | propositional STRIPS | PSPACE-complete | hard |
| Optimal plan length | 2 grippers, 2 rooms, n balls | 4⌈n/2⌉ + ⌊n/2⌋ − 1 | easy |
