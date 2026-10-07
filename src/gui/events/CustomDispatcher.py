from kivy.event import EventDispatcher
from kivy.clock import Clock
from helper import logger
from controller import Controller
from model import Item
from gui.widgets.CheckoutModal import CheckoutModal


class CustomDispatcher(EventDispatcher):
    """Eventbus zwischen RFID-Service, Controller und GUI.

    Der Bus selbst enthält keine Logik; der Login- und Bezahl-Fluss liegt im
    Coordinator (gui/coordinator.py). Die Default-Handler sind absichtlich leer.
    TODO Schritt 2: Modal-Handling (on_BuyButton_release / on_CheckoutModal_dismiss)
    in den CheckoutScreen verschieben.
    """

    def __init__(self, **kwargs):
        self.register_event_type('on_tag')
        self.register_event_type('on_logout')
        self.register_event_type('on_login')
        self.register_event_type('on_login_error')
        self.register_event_type('on_cancel_login_error')
        self.register_event_type('on_BuyButton_release')
        self.register_event_type('on_CheckoutModal_dismiss')
        self.register_event_type('on_item_bought')
        self.register_event_type('on_item_bought_error')
        self.register_event_type('on_timer_reset')
        super(CustomDispatcher, self).__init__(**kwargs)

    def rfidcallback(self, tag: tuple[str, str]):
        text = tag[1]
        tag_id = str(tag[0])
        Clock.schedule_once(lambda dt: self.dispatch('on_tag', tag_id, text))

    # --- Default-Handler: leer, der Bus relayt nur ---

    def on_tag(self, tag_id, text, *args):
        pass

    def on_logout(self, *args):
        pass

    def on_login(self, *args, **kwargs):
        pass

    def on_login_error(self, *args, **kwargs):
        pass

    def on_cancel_login_error(self, *args):
        pass

    def on_item_bought(self, *args, **kwargs):
        pass

    def on_item_bought_error(self, *args, **kwargs):
        pass

    def on_timer_reset(self, *args, **kwargs):
        pass

    # --- Modal-Handling (wandert in Schritt 2 in den CheckoutScreen) ---

    def on_BuyButton_release(self, *args, **kwargs):
        item: Item = kwargs.pop('item')
        logger.debug(f"BuyButton von Item {item.id} losgelassen")
        itemIsInShoppingcard: bool = Controller.checkoutItem(item)
        self.modal = CheckoutModal(
            size_hint=(.6,.8),
            item=item,
            pos_hint={'center_x':.5, 'center_y': .5},
            auto_dismiss = True,
            funds= itemIsInShoppingcard
        )
        self.modal.open()

    def on_CheckoutModal_dismiss(self, *args, **kwargs):
        logger.debug(f"CheckoutModal dismissed")
        Controller.reset_shoppingcard()
