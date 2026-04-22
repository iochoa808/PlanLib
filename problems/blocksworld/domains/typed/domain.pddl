;;; Blocksworld Domain — typed variant (IPC 2000 style)
;;; Uses :typing to allow planners to prune irrelevant groundings.
;;; Semantics are identical to domain.pddl.

(define (domain blocksworld-typed)
  (:requirements :strips :typing)
  (:types block)

  (:predicates
    (on        ?b - block  ?x - block)
    (ontable   ?b - block)
    (clear     ?b - block)
    (holding   ?b - block)
    (handempty))

  (:action pick-up
    :parameters  (?b - block)
    :precondition (and (clear ?b) (ontable ?b) (handempty))
    :effect       (and (holding ?b)
                       (not (clear ?b))
                       (not (ontable ?b))
                       (not (handempty))))

  (:action put-down
    :parameters  (?b - block)
    :precondition (holding ?b)
    :effect       (and (clear ?b) (ontable ?b) (handempty)
                       (not (holding ?b))))

  (:action stack
    :parameters  (?b - block  ?x - block)
    :precondition (and (holding ?b) (clear ?x))
    :effect       (and (on ?b ?x) (clear ?b) (handempty)
                       (not (holding ?b)) (not (clear ?x))))

  (:action unstack
    :parameters  (?b - block  ?x - block)
    :precondition (and (on ?b ?x) (clear ?b) (handempty))
    :effect       (and (holding ?b) (clear ?x)
                       (not (on ?b ?x))
                       (not (clear ?b))
                       (not (handempty))))
)
