from kivy.event import EventDispatcher
from kivy.properties import OptionProperty, BooleanProperty, StringProperty, ListProperty, ObjectProperty


class CheckoutViewModel(EventDispatcher):
    """Zustand des Kauf-Dialogs.

    state: hidden -> (confirm | no_funds) -> thanks -> hidden
    """

    HIDDEN = "hidden"
    CONFIRM = "confirm"
    NO_FUNDS = "no_funds"
    THANKS = "thanks"

    HINT_CONFIRM = "Zum bezahlen Chip erneut scannen."
    HINT_NO_FUNDS = "Nicht genügend Guthaben"
    HINT_THANKS = "Danke für deinen Einkauf!"

    state = OptionProperty(HIDDEN, options=[HIDDEN, CONFIRM, NO_FUNDS, THANKS])
    is_open = BooleanProperty(False)
    item = ObjectProperty(None, rebind=True)
    title = StringProperty("")
    hint = StringProperty("")
    hint_color = ListProperty([1, 1, 1, 1])

    def open(self, item_vm, funds: bool):
        self.item = item_vm
        self.title = f"{item_vm.flavor} - {item_vm.price_text}"
        # hint/hint_color vor state setzen - das Modal liest beide
        # synchron, sobald state feuert
        if funds:
            self.hint = self.HINT_CONFIRM
            self.hint_color = [1, 1, 1, 1]
            self.state = self.CONFIRM
        else:
            self.hint = self.HINT_NO_FUNDS
            self.hint_color = [1, .5, .5, 1]
            self.state = self.NO_FUNDS
        self.is_open = True

    def bought(self):
        # wie in open(): erst hint, dann state
        self.hint = self.HINT_THANKS
        self.hint_color = [.5, 1, .5, 1]
        self.state = self.THANKS

    def close(self):
        self.state = self.HIDDEN
        self.is_open = False
