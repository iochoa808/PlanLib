---
title: Domain example title
language: Language and version
source: SourceIfApplicable
notes: Any notes regarding the domain, similarities to other domains, changes or viewpoint
---

## State Space

Description of state-space

## Types

If applicable, explain the types and how and why are they used.

## Objects

A line, list or table describing the different objects that might be present

## Predicates

| name | desc |
|---|---|
| pred1 | description of pred1 |
| pred2(x) | description of pred2 and its argument |
| pred3(x, y) | description of pred3 and its arguments |
| pred4 | description of pred4 |

## Actions

#### action1(x - typex) — one line description of action1
```
preconditions: pred1 ∧ pred2(x)
add effects:   pred3(x,y)
del effects:   pred4
```

#### action2(x - typex, y - typey) — one line description of action2
```
preconditions: pred4
add effects:   pred1
del effects:   pred3(x,y) ∧ pred2(x)
```

## Goal

A description of the goal, the predicates and all the final state.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| instance0 | n | min-steps-found | optimality | If applicable | instances/fileName |
