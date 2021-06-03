from __future__ import annotations

from labster.lib.workflow import Workflow

from .states import ALL_STATES, EN_EDITION
from .transitions import ABANDONNER, ACCUSER_RECEPTION, COMMENTER, \
    CONFIRMER_FINALISATION_DGRTT, CONFIRMER_RECEVABILITE_DGRTT, DESARCHIVER, \
    PRENDRE_LA_MAIN_DGRTT, PRENDRE_LA_MAIN_GESTIONNAIRE, REJETER_DGRTT, \
    REQUERIR_MODIFICATION_DGRTT, REQUERIR_MODIFICATION_DIR, SOUMETTRE, \
    VALIDER_DIR


class LabsterWorkflow(Workflow):
    initial_state = EN_EDITION

    states = ALL_STATES

    # NB: order counts!
    transitions = [
        SOUMETTRE,
        PRENDRE_LA_MAIN_GESTIONNAIRE,
        VALIDER_DIR,
        PRENDRE_LA_MAIN_DGRTT,
        REQUERIR_MODIFICATION_DIR,
        ACCUSER_RECEPTION,
        CONFIRMER_RECEVABILITE_DGRTT,
        CONFIRMER_FINALISATION_DGRTT,
        REQUERIR_MODIFICATION_DGRTT,
        REJETER_DGRTT,
        ABANDONNER,
        DESARCHIVER,
        COMMENTER,
    ]

    def actor_is_contact_labco(self):
        return self.actor == self.case.contact_labco

    def actor_is_porteur_or_gestionnaire(self):
        return self.actor in (self.case.porteur, self.case.gestionnaire)
