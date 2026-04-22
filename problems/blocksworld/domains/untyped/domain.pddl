;;; Blocksworld Domain — 4-operator version
;;; prob001 · Planning Problem Library

(define (domain blocksworld)
  (:requirements :strips)

  (:predicates
    (on        ?b - object  ?x - object)
    (ontable   ?b - object)
    (clear     ?b - object)
    (holding   ?b - object)
    (handempty))

  (:action pick-up
    :parameters  (?b - object)
    :precondition (and (clear ?b) (ontable ?b) (handempty))
    :effect       (and (holding ?b)
                       (not (clear ?b))
                       (not (ontable ?b))
                       (not (handempty))))

  (:action put-down
    :parameters  (?b - object)
    :precondition (holding ?b)
    :effect       (and (clear ?b) (ontable ?b) (handempty)
                       (not (holding ?b))))

  (:action stack
    :parameters  (?b - object  ?x - object)
    :precondition (and (holding ?b) (clear ?x))
    :effect       (and (on ?b ?x) (clear ?b) (handempty)
                       (not (holding ?b)) (not (clear ?x))))

  (:action unstack
    :parameters  (?b - object  ?x - object)
    :precondition (and (on ?b ?x) (clear ?b) (handempty))
    :effect       (and (holding ?b) (clear ?x)
                       (not (on ?b ?x))
                       (not (clear ?b))
                       (not (handempty))))
)
