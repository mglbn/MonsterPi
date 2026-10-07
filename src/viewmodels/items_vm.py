from kivy.event import EventDispatcher
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from helper import convertCentsToString


class ItemViewModel(EventDispatcher):
    """Präsentationszustand eines Artikels im Grid."""

    flavor = StringProperty("")
    price_text = StringProperty("")
    image = ObjectProperty(None)      # PNG-Bytes
    soldout = BooleanProperty(False)
    session = ObjectProperty(None)    # SessionViewModel für Commands

    def __init__(self, item, session_vm, **kwargs):
        super().__init__(**kwargs)
        self.item = item              # Model-Objekt
        self.session = session_vm
        self.flavor = item.flavor
        self.price_text = convertCentsToString(item.price)
        self.image = item.png
        self.soldout = item.inStock < 1

    def select(self):
        self.session.select_item(self)

    def refresh_stock(self):
        self.soldout = self.item.inStock < 1


class ItemListViewModel(EventDispatcher):
    """Artikelliste des eingeloggten Users."""

    items = ListProperty([])

    def __init__(self, session_vm, **kwargs):
        super().__init__(**kwargs)
        self.session = session_vm

    def load(self, user):
        service = self.session.service
        self.items = [ItemViewModel(item, self.session) for item in service.items_for_user(user)]
