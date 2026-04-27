; ──────────────────────────────────────────────────────────
; Domain:   Pancake Sorting — Extended Data Structures variant
; Language: PDDL-XDS (non-standard extension)
;
; Uses bounded-integer types and array mutation syntax.
; The stack is a single array of length n; a flip at index f
; reverses the prefix [0..f] in one bulk array assignment.
;
; TYPES
;   pancakes → (number 0 4)   bounded integer 0–4
;   stack    → (array 5 pancakes)   array of 5 pancake values
;
; FUNCTIONS
;   pancake_stack : stack     the mutable stack array
;
; ACTIONS
;   flip(?f : pancakes)
;     No preconditions.
;     Effect: ∀ i ∈ [0, ?f]: pancake_stack[i] := pancake_stack[?f − i]
; ──────────────────────────────────────────────────────────

(define (domain extended-data-structures)
  (:requirements :strips :typing :xds-arrays)

  (:types
    pancakes - (number 0 4)
    stack    - (array 5 pancakes)
  )

  (:functions
    (pancake_stack) - stack
  )

  ; Reverse the prefix of pancake_stack from index 0 to index ?f.
  (:action flip
    :parameters (?f - pancakes)
    :precondition ()
    :effect
      (array-reverse (pancake_stack) 0 ?f)
  )
)
