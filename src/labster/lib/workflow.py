"""Modèle de case management adapté au projet Labster."""
from __future__ import annotations

from datetime import datetime
from html import escape
from typing import TYPE_CHECKING

from inflection import humanize, underscore

from labster.domain2.services.notifications import send_notification
from labster.types import JSONList

if TYPE_CHECKING:
    from labster.domain2.model.demande import Demande
    from labster.domain2.model.profile import Profile


class WorkflowException(Exception):
    pass


#
# Generic
#
class State:
    next_action = ""
    is_final = False

    @property
    def label(self):
        return humanize(self.__class__.__name__)

    @property
    def label_short(self):
        return self.label

    @property
    def id(self):
        return underscore(self.__class__.__name__).upper()

    def __eq__(self, other):
        return isinstance(other, State) and self.id == other.id

    def __repr__(self):
        return f"<State {self.id}>"

    def enter(self, workflow: Workflow) -> None:
        self.on_leave(workflow)
        workflow.case.wf_state = self.id
        self.on_enter(workflow)
        if self.is_final:
            self.deactivate(workflow)

    def deactivate(self, workflow: Workflow) -> None:
        workflow.case.active = False
        workflow.case.editable = False

    def on_enter(self, workflow: Workflow) -> None:
        """Callback (override in subclasses)."""

    def on_leave(self, workflow: Workflow) -> None:
        """Callback (override in subclasses)."""

    def task_owners(self, workflow: Workflow) -> set[Profile]:
        """Override in subclasses."""
        return set()


class Transition:
    label = ""
    category = "primary"
    from_states: list[State] = []
    to_state: State | None = None
    message = (
        "Transition de l'état '{old_state}' vers l'état "
        "'{new_state}' initiée par l'utilisateur {actor}."
    )
    note = ""

    def precondition(self, workflow: Workflow) -> bool:
        return True

    def apply(self, workflow: Workflow, data: dict) -> None:
        pass

    @property
    def id(self):
        return underscore(self.__class__.__name__).upper()

    def __eq__(self, other):
        return isinstance(other, Transition) and self.id == other.id

    def __repr__(self):
        return f"<Transition {self.id}>"

    def can_execute(self, workflow: Workflow) -> bool:
        if workflow.state not in self.from_states:
            return False
        return self.precondition(workflow)

    def execute(self, workflow: Workflow, data: dict) -> None:
        if not self.can_execute(workflow):
            raise WorkflowException(f"Can't execute transition {self.id}")
        if hasattr(self, "apply"):
            self.apply(workflow, data)
        if self.to_state and not self.to_state == workflow.state:
            self.to_state.enter(workflow)

    def get_users_to_notify(self, workflow: Workflow, old_state: State) -> set[Profile]:
        return set()

    def get_form(self, workflow: Workflow, **kw) -> JSONList:
        return []


class Workflow:
    states: list[State] = []
    transitions: list[Transition] = []
    initial_state: State | None = None
    case: Demande
    actor: Profile

    def __init__(self, case: Demande, actor: Profile):
        self.case = case
        self.actor = actor
        if not case.wf_state:
            self.start()

    def __repr__(self):
        return f"<LabsterWorkflow state={self.case.wf_state}>"

    def set_actor(self, actor):
        self.actor = actor

    def start(self):
        state = self.initial_state
        state.enter(self)

    @property
    def state(self):
        return self.current_state()

    def current_state(self) -> State:
        for state in self.states:
            if self.case.wf_state == state.id:
                return state
        raise WorkflowException(f"Object is in an unknown state: {self.case.wf_state}")

    def current_owners(self) -> set[Profile]:
        return self.current_state().task_owners(self)

    def possible_transitions(self) -> list[Transition]:
        return [t for t in self.transitions if t.can_execute(self)]

    def execute_transition(self, transition: Transition, data: dict | None = None):
        if not data:
            data = {}
        case = self.case
        old_state = self.state
        transition.note = note = data.get("note", "")
        case.no_infolab = data.get("no_infolab", "") or case.no_infolab
        case.no_eotp = data.get("no_eotp", "") or case.no_eotp

        if callable(transition.message):
            message = transition.message(self)
        else:
            message = transition.message
        transition.execute(self, data)
        new_state = self.state
        for k in data:
            if k == "note":
                continue
            self.case.data[k] = data[k]
        self.log(transition, old_state, new_state, message, note)

        self.case.wf_date_derniere_action = datetime.utcnow()
        self.case.wf_retard = 0

    def log(self, transition, old_state, new_state, msg_tpl, note):
        from labster.util import url_for

        actor = self.actor
        ctx = {
            "old_state": old_state,
            "new_state": new_state,
            "actor": f'<a href="{url_for(actor)}">{actor.full_name}</a>',
        }
        msg = msg_tpl.format(**ctx)
        log_entry = {
            "date": datetime.now().strftime("%d %b %Y %H:%M:%S"),
            "actor_id": actor.id,
            "message": msg,
            "note": note,
            "old_state": old_state.id,
            "new_state": new_state.id,
            "transition": transition.id,
        }
        self.case.wf_history.append(log_entry)

        if note:
            notification_msg = msg + f"<blockquote>{escape(note)}</blockquote>"
        else:
            notification_msg = msg

        users_to_notify = transition.get_users_to_notify(self, old_state)
        for user in users_to_notify:
            # FIXME: this shouldn't happen!
            if not user:
                continue
            send_notification(user, notification_msg, self)

    def get_transition_by_id(self, id: str) -> Transition:
        transitions = self.possible_transitions()
        for transition in transitions:
            if transition.id == id:
                return transition
        raise IndexError()

    def get_state_by_id(self, id: str) -> State:
        for state in self.states:
            if state.id == id:
                return state
        raise IndexError()

    def get_value(self, key, default=None):
        return self.case.wf_data.get(key, default)

    def set_value(self, key, value):
        self.case.wf_data[key] = value
