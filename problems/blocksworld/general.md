---
id: prob001
slug: blocksworld
title: Blocksworld
subtitle: "A set of blocks resting on a table must be rearranged into a target configuration using a single robot arm that can pick up or place one block at a time. The canonical benchmark domain of classical AI planning."
proposers: ["Terry Winograd", "Richard E. Fikes", "Nils J. Nilsson"]
origin: "Winograd, 1971"
origin_year: 1971
last_updated: "2025-01-01"
category: Classical
tags: [Classical, Fully Observable, Deterministic, Single Agent, STRIPS]
languages: [PDDL 1.2, PDDL 2.1]
ipc_editions: [IPC 1998, IPC 2000, IPC 2023]
complexity_summary: {optimal: PSPACE-complete, suboptimal: P}
---

## Description

The Blocksworld is the oldest and most widely studied domain in automated planning. A flat table holds an unlimited supply of identically sized cubic blocks. A single robot arm can perform one action at a time: pick up a clear block and either place it on the table or stack it on another clear block. Given an arbitrary initial configuration and a goal configuration, the task is to find a sequence of actions that transforms the world from the initial state into the goal.

## History

The domain was first operationalised in Terry Winograd's SHRDLU natural-language understanding program (1971), which accepted English commands and manipulated virtual blocks [Winograd71]. It was then adopted as the flagship demonstration domain for the STRIPS planner by Fikes and Nilsson (1971) [FikesNilsson71], cementing its status as the "hello world" of symbolic AI planning. Gerald Sussman's 1973 thesis [Sussman73] identified the key interaction structure now known as the Sussman Anomaly. The domain appeared in IPC 1998, IPC 2000, and IPC 2023, and has been used as a benchmark in virtually every major planning system evaluation.

## Variants

- [4-op Blocksworld](#domain-untyped)
- [3-op (hand-free) Blocksworld](#domain-3op)
- [Typed Blocksworld (IPC 2000)](#domain-typed)
- Numeric / Weight-constrained
- Temporal Blocksworld
- Stochastic / PPDDL
- Multi-arm / Multi-agent

The canonical 4-operator formulation uses pick-up, put-down, stack, and unstack. A reduced 3-operator variant merges pick-up/unstack into a single move action assuming the arm is always empty before each action. The IPC 2000 typed variant adds explicit :types declarations. The Depots domain (IPC 2002) combines Blocksworld with Logistics.

## Complexity

| Problem | Qualifier | Result | Class |
|---|---|---|---|
| Plan existence | delete-free relaxation | NP-complete | hard |
| Plan existence | with delete effects | PSPACE-complete | hard |
| Optimal plan length | | PSPACE-complete | hard |
| Satisficing plan | any valid plan | P | easy |
