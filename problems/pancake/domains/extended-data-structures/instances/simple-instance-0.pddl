; ──────────────────────────────────────────────────────────
; Instance:  Simple_instance_0
; Domain:    extended-data-structures (PDDL-XDS)
; n:         5  (five pancakes)
; k*:        2  (proven optimal: flip at index 1, then flip at index 4)
; Status:    proven optimal
;
; Initial stack (index 0 = top): [4, 5, 3, 2, 1]
; Goal   stack (index 0 = top): [1, 2, 3, 4, 5]
;
; Optimal plan:
;   1. flip(1)  — reverse indices [0..1]: [4,5,...] → [5,4,3,2,1]
;   2. flip(4)  — reverse indices [0..4]: → [1,2,3,4,5]
; ──────────────────────────────────────────────────────────

(define (problem simple-instance-0)
  (:domain extended-data-structures)

  (:init
    (= (pancake_stack) (array 4 5 3 2 1))
  )

  (:goal
    (= (pancake_stack) (array 1 2 3 4 5))
  )
)
