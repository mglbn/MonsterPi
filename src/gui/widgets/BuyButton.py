from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty


class BuyButton(Button):

    COLOR_NORMAL = (.6, .1, .1, 1)
    COLOR_PRESSED = (.3, .1, .1, 1)
    COLOR_SOLDOUT = (.2, .2, .2, 1)

    item_vm = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''

        with self.canvas.before:
            self.Color = Color(*self._current_color())
            self.bg_rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(12)]
            )

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            state=self._update_color
        )

    def on_item_vm(self, instance, item_vm):
        item_vm.bind(soldout=self._update_disabled)
        item_vm.session.checkout.bind(is_open=self._update_disabled)
        self._update_disabled()

    def on_release(self):
        if self.item_vm is not None:
            self.item_vm.select()

    def _current_color(self):
        if self.item_vm is not None and self.item_vm.soldout:
            return self.COLOR_SOLDOUT
        if self.state == 'down':
            return self.COLOR_PRESSED
        return self.COLOR_NORMAL

    def _update_disabled(self, *_):
        if self.item_vm is None:
            return
        self.disabled = (
            self.item_vm.soldout or
            self.item_vm.session.checkout.is_open
        )

    def _update_canvas(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_color(self, *_):
        self.Color.rgba = self._current_color()
