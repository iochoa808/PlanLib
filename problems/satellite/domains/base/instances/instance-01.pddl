; ──────────────────────────────────────────────────────────
; Instance:  instance-01
; Domain:    satellite (IPC 2002 base)
; n:         3 objects (1 satellite, 1 instrument, 2 directions)
; k*:        4  (switch_on + calibrate + turn_to + take_image)
; Status:    proven optimal
; Source:    Long03
;
; Setup:
;   sat1 carries instrument0 (supports thermograph mode).
;   instrument0 must face groundstation0 to calibrate.
;   sat1 starts pointing at groundstation0.
;   Goal: capture a thermograph image of star1.
;
; Optimal plan:
;   1. switch_on(instrument0, sat1)
;   2. calibrate(sat1, instrument0, groundstation0)
;   3. turn_to(sat1, star1, groundstation0)
;   4. take_image(sat1, star1, instrument0, thermograph)
; ──────────────────────────────────────────────────────────

(define (problem satellite-instance-01)
  (:domain satellite)

  (:objects
    sat1          - satellite
    groundstation0
    star1         - direction
    instrument0   - instrument
    thermograph   - mode
  )

  (:init
    (on_board instrument0 sat1)
    (supports instrument0 thermograph)
    (calibration_target instrument0 groundstation0)
    (power_avail sat1)
    (pointing sat1 groundstation0)
  )

  (:goal (and
    (have_image star1 thermograph)
  ))
)
