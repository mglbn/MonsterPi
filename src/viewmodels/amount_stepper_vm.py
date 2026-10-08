from kivy.event import EventDispatcher
from kivy.properties import (OptionProperty, BooleanProperty, NumericProperty,
                             StringProperty, ObjectProperty)
from helper import convertCentsToString


class AmountStepperViewModel(EventDispatcher):
    """Zustand des Guthaben-Steppers im AdminScreen.

    Der Admin baut über nudge() ein Delta auf; geschrieben wird erst
    mit confirm(). target_preview zeigt den Zielstand, bevor
    irgendetwas persistiert wird. confirmable ist False, solange das
    Delta 0 ist oder der Zielstand unter dem Dispo läge.

    Events: on_applied(ok, user) nach confirm() - AdminViewModel lädt
    darauf die Userliste neu, SessionViewModel aktualisiert die
    Balance-Anzeige.
    """

    HIDDEN = "hidden"
    EDITING = "editing"

    __events__ = ('on_applied',)

    def on_applied(self, ok, user):
        """Default-Handler: läuft zusätzlich zu gebundenen Callbacks."""

    state = OptionProperty(HIDDEN, options=[HIDDEN, EDITING])
    user = ObjectProperty(None, rebind=True, allownone=True)
    username = StringProperty("")
    balance_text = StringProperty("")
    delta = NumericProperty(0)
    target_preview = StringProperty("")
    confirmable = BooleanProperty(False)

    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)
        self.service = service

    def open(self, user):
        self.user = user
        self.username = f"{user.firstname} {user.lastname}".strip() or user.tag_id
        self.delta = 0
        self.state = self.EDITING
        self._refresh()

    def nudge(self, step: int):
        if self.state != self.EDITING:
            return
        self.delta += step
        self._refresh()

    def reset(self):
        if self.state == self.EDITING:
            self.delta = 0
            self._refresh()

    def confirm(self) -> bool:
        if self.state != self.EDITING or not self.confirmable:
            return False
        user = self.user
        ok = self.service.adjust_balance(user, self.delta)
        self.close()
        self.dispatch('on_applied', ok, user)
        return ok

    def close(self):
        self.state = self.HIDDEN
        self.user = None
        self.username = ""
        self.balance_text = ""
        self.delta = 0
        self.target_preview = ""
        self.confirmable = False

    def _refresh(self):
        neu = self.user.balance + self.delta
        self.balance_text = convertCentsToString(self.user.balance)
        self.target_preview = convertCentsToString(neu)
        self.confirmable = self.delta != 0 and neu >= self.user.dispo
