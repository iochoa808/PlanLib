; ──────────────────────────────────────────────────────────
; Domain:   Pancake Sorting — Typed Variant
; Language: PDDL 2.1 (conditional effects, universal quantification)
;
; A stack of n tiles (pancakes) must be sorted top-to-bottom using
; prefix reversals.  The geometry of each flip is encoded in the
; initial state via two auxiliary predicates:
;
;   lte(?p1, ?p2)             — position p1 is within the prefix ending at p2
;   flipat(?pa, ?p, ?pnew)    — flipping at pa maps position p to pnew
;
; These are constant across all states and are supplied in :init.
; ──────────────────────────────────────────────────────────

(define (domain pancake-typed)
  (:requirements :strips :typing :conditional-effects :universal-preconditions)

  (:types tile position - object)

  (:predicates
    (at ?t - tile ?p - position)
    (lte ?p1 - position ?p2 - position)
    (flipat ?pa - position ?p - position ?pnew - position)
  )

  ; Reverse all tiles from the top of the stack down to position ?pala.
  ; Conditions are evaluated against the pre-action state (PDDL semantics),
  ; so add and delete effects are applied simultaneously.
  (:action flip
    :parameters (?pala - position)
    :precondition ()
    :effect (and
      (forall (?t ?tnext - tile ?p ?pnext - position)
        (when (and (lte ?p ?pala)
                   (at ?t ?p)
                   (flipat ?pala ?p ?pnext)
                   (at ?tnext ?pnext))
          (and (at ?tnext ?p)
               (not (at ?t ?p)))
        )
      )
    )
  )
)
