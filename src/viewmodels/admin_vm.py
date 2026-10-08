from kivy.event import EventDispatcher
from kivy.properties import ListProperty
from helper import convertCentsToString


class AdminViewModel(EventDispatcher):
    """Userliste im AdminScreen.

    users hält Snapshots als Dicts - direkt als data für eine
    RecycleView nutzbar (viewclass UserRow). load() wird beim Betreten
    des AdminScreens und nach jeder angewandten Guthaben-Änderung
    aufgerufen, damit die Liste aktuelle Werte zeigt.
    """

    users = ListProperty([])

    def __init__(self, service, stepper_vm, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.stepper = stepper_vm
        self.stepper.bind(on_applied=self._on_applied)

    def load(self):
        self.users = [{
            'user': user,
            'name': f"{user.firstname} {user.lastname}".strip() or user.tag_id,
            'balance_text': convertCentsToString(user.balance),
            'balance_negative': user.balance < 0,
        } for user in self.service.all_users()]

    def _on_applied(self, stepper, ok, user):
        self.load()
