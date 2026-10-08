from kivy.event import EventDispatcher
from kivy.properties import ListProperty
from helper import convertCentsToString


class StockViewModel(EventDispatcher):
    """Artikelliste der Lagerverwaltung.

    items hält Snapshots als Dicts - direkt als data für eine
    RecycleView nutzbar (viewclass ItemRow). load() wird beim Betreten
    des StockScreens und nach jeder angewandten Bestands-Änderung
    aufgerufen, damit die Liste aktuelle Werte zeigt.
    """

    items = ListProperty([])

    def __init__(self, service, stepper_vm, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.stepper = stepper_vm
        self.stepper.bind(on_applied=self._on_applied)

    def load(self):
        self.items = [{
            'item': item,
            'name': f"{item.brand} {item.flavor}".strip(),
            'price_text': convertCentsToString(item.price),
            'stock_text': str(item.inStock),
            'soldout': item.inStock < 1,
        } for item in self.service.all_items()]

    def _on_applied(self, stepper, ok, item):
        self.load()
