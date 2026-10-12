from kivy.event import EventDispatcher
from kivy.properties import (OptionProperty, BooleanProperty, NumericProperty,
                             StringProperty, ObjectProperty)
from helper import logger


class StockStepperViewModel(EventDispatcher):
    """Zustand des Bestand-Steppers im StockScreen (Lagerverwaltung).

    Wie AmountStepperViewModel: nudge() baut ein Delta auf, geschrieben
    wird erst mit confirm(). target_preview zeigt den Zielbestand, bevor
    irgendetwas persistiert wird. confirmable ist False, solange das
    Delta 0 ist oder der Zielbestand negativ läge.

    Events: on_applied(ok, item) nach confirm() - StockViewModel lädt
    darauf die Artikelliste neu.
    """

    HIDDEN = "hidden"
    EDITING = "editing"

    __events__ = ('on_applied',)

    state = OptionProperty(HIDDEN, options=[HIDDEN, EDITING])
    item = ObjectProperty(None, rebind=True, allownone=True)
    title = StringProperty("")
    stock_text = StringProperty("")
    delta = NumericProperty(0)
    target_preview = StringProperty("")
    confirmable = BooleanProperty(False)

    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)
        self.service = service

    def on_applied(self, ok, item):
        """Default-Handler: läuft zusätzlich zu gebundenen Callbacks."""

    def open(self, item):
        self.item = item
        self.title = f"{item.brand} {item.flavor}".strip()
        self.delta = 0
        self.state = self.EDITING
        self._refresh()
        logger.info(f"Admin bearbeitet Bestand von {self.title}")

    def nudge(self, step: int):
        if self.state != self.EDITING:
            return
        self.delta += step
        self._refresh()
        logger.debug(f"Bestand {self.title}: Schritt {step:+d}, Delta {self.delta:+d}")

    def reset(self):
        if self.state == self.EDITING:
            logger.debug(f"Bestands-Delta zurückgesetzt (war {self.delta:+d})")
            self.delta = 0
            self._refresh()

    def confirm(self) -> bool:
        if self.state != self.EDITING or not self.confirmable:
            return False
        item = self.item
        logger.info(
            f"Admin ändert Bestand von {item.brand} {item.flavor}: "
            f"{item.inStock} -> {item.inStock + self.delta} ({self.delta:+d})"
        )
        ok = self.service.adjust_stock(item, self.delta)
        if not ok:
            logger.warning("Bestandsänderung fehlgeschlagen")
        self.close()
        self.dispatch('on_applied', ok, item)
        return ok

    def close(self):
        self.state = self.HIDDEN
        self.item = None
        self.title = ""
        self.stock_text = ""
        self.delta = 0
        self.target_preview = ""
        self.confirmable = False

    def _refresh(self):
        neu = self.item.inStock + self.delta
        self.stock_text = str(self.item.inStock)
        self.target_preview = str(neu)
        self.confirmable = self.delta != 0 and neu >= 0
