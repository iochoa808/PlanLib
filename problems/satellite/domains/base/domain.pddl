; ──────────────────────────────────────────────────────────
; Domain:   Satellite — Base formulation (IPC 2002)
; Language: PDDL 2.1 (:typing)
;
; A fleet of satellites must acquire a set of (direction, mode)
; images.  Each instrument must be powered on and calibrated
; (by pointing at its calibration target) before it can take
; an image.  Each satellite has a single power bus.
;
; Reference: Long & Fox, JAIR 2003, doi:10.1613/jair.1240
; ──────────────────────────────────────────────────────────

(define (domain satellite)
  (:requirements :typing)

  (:types satellite direction instrument mode - object)

  (:predicates
    (on_board         ?i - instrument ?s - satellite)
    (supports         ?i - instrument ?m - mode)
    (pointing         ?s - satellite  ?d - direction)
    (power_avail      ?s - satellite)
    (power_on         ?i - instrument)
    (calibrated       ?i - instrument)
    (calibration_target ?i - instrument ?d - direction)
    (have_image       ?d - direction  ?m - mode)
  )

  ; Slew satellite ?s from direction ?d_prev to ?d_new.
  (:action turn_to
    :parameters (?s - satellite ?d_new - direction ?d_prev - direction)
    :precondition (pointing ?s ?d_prev)
    :effect (and
      (pointing ?s ?d_new)
      (not (pointing ?s ?d_prev))
    )
  )

  ; Power on instrument ?i on satellite ?s.
  ; Consumes the satellite's power budget and loses calibration.
  (:action switch_on
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_board ?i ?s) (power_avail ?s))
    :effect (and
      (power_on ?i)
      (not (calibrated ?i))
      (not (power_avail ?s))
    )
  )

  ; Power off instrument ?i on satellite ?s, freeing the power budget.
  (:action switch_off
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_board ?i ?s) (power_on ?i))
    :effect (and
      (not (power_on ?i))
      (power_avail ?s)
    )
  )

  ; Calibrate instrument ?i by pointing satellite ?s at the calibration target.
  (:action calibrate
    :parameters (?s - satellite ?i - instrument ?d - direction)
    :precondition (and
      (on_board ?i ?s)
      (calibration_target ?i ?d)
      (pointing ?s ?d)
      (power_on ?i)
    )
    :effect (calibrated ?i)
  )

  ; Take an image of direction ?d in mode ?m using instrument ?i on satellite ?s.
  (:action take_image
    :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
    :precondition (and
      (calibrated ?i)
      (on_board ?i ?s)
      (supports ?i ?m)
      (power_on ?i)
      (pointing ?s ?d)
    )
    :effect (have_image ?d ?m)
  )
)
