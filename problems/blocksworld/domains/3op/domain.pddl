;;; Blocksworld Domain — 3-operator version
;;; prob001 · Planning Problem Library
;;;
;;; Reduces the 4-operator formulation by merging pick-up and unstack
;;; into a single move(b, from) action, where 'from' is either a block
;;; or the special constant 'table'. Similarly, put-down and stack are
;;; merged into place(b, to).
;;;
;;; This variant assumes the arm is always empty at the start of each
;;; action, which is enforced by the preconditions. The semantics are
;;; equivalent to the 4-operator version for any reachable state.
;;;
;;; Requires: :strips :typing :equality

(define (domain blocksworld-3op)
  (:requirements :strips :typing :equality)
  (:types block location)
  (:constants table - location)

  (:predicates
    (on        ?b - block    ?l - location)
    (clear     ?l - location)
    (holding   ?b - block)
    (handempty))

  ;; Pick up a block from any location (table or another block)
  (:action move
    :parameters  (?b - block  ?from - location)
    :precondition (and (on ?b ?from)
                       (clear ?b)
                       (handempty)
                       (not (= ?b ?from)))
    :effect       (and (holding ?b)
                       (clear ?from)
                       (not (on ?b ?from))
                       (not (handempty))))

  ;; Place held block on any location (table or another block)
  (:action place
    :parameters  (?b - block  ?to - location)
    :precondition (and (holding ?b)
                       (clear ?to)
                       (not (= ?b ?to)))
    :effect       (and (on ?b ?to)
                       (clear ?b)
                       (handempty)
                       (not (holding ?b))
                       (not (clear ?to))))
  
  
)