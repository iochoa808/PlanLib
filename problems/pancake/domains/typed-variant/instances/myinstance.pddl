; ──────────────────────────────────────────────────────────
; Instance:  MyInstance
; Domain:    pancake-typed
; n:         5  (five pancakes)
; k*:        2  (proven optimal: flip top-2, then flip all-5)
; Status:    proven optimal
; Source:    Carla25
;
; Initial stack (top → bottom): t4 t5 t3 t2 t1
; Goal   stack (top → bottom): t1 t2 t3 t4 t5
;
; Optimal plan:
;   1. flip(p2)  — reverse top 2: [t4,t5,...] → [t5,t4,t3,t2,t1]
;   2. flip(p5)  — reverse all 5: → [t1,t2,t3,t4,t5]
; ──────────────────────────────────────────────────────────

(define (problem myinstance)
  (:domain pancake-typed)

  (:objects
    t1 t2 t3 t4 t5 - tile
    p1 p2 p3 p4 p5 - position
  )

  (:init
    ; ── initial stack (p1 = top, p5 = bottom) ──────────────
    (at t4 p1)
    (at t5 p2)
    (at t3 p3)
    (at t2 p4)
    (at t1 p5)

    ; ── lte: (lte pi pj) iff i ≤ j ────────────────────────
    (lte p1 p1) (lte p1 p2) (lte p1 p3) (lte p1 p4) (lte p1 p5)
                (lte p2 p2) (lte p2 p3) (lte p2 p4) (lte p2 p5)
                            (lte p3 p3) (lte p3 p4) (lte p3 p5)
                                        (lte p4 p4) (lte p4 p5)
                                                    (lte p5 p5)

    ; ── flipat: flip at pa maps position p to pnew ─────────
    ; flip at p1 (trivial, no change)
    (flipat p1 p1 p1)
    ; flip at p2: p1 ↔ p2
    (flipat p2 p1 p2) (flipat p2 p2 p1)
    ; flip at p3: p1 ↔ p3, p2 stays at p2
    (flipat p3 p1 p3) (flipat p3 p2 p2) (flipat p3 p3 p1)
    ; flip at p4: p1 ↔ p4, p2 ↔ p3
    (flipat p4 p1 p4) (flipat p4 p2 p3) (flipat p4 p3 p2) (flipat p4 p4 p1)
    ; flip at p5: p1 ↔ p5, p2 ↔ p4, p3 stays at p3
    (flipat p5 p1 p5) (flipat p5 p2 p4) (flipat p5 p3 p3) (flipat p5 p4 p2) (flipat p5 p5 p1)
  )

  (:goal (and
    (at t1 p1)
    (at t2 p2)
    (at t3 p3)
    (at t4 p4)
    (at t5 p5)
  ))
)
