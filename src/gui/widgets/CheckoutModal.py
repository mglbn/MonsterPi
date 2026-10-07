import io

from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image, CoreImage
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from helper.logger import logger
from viewmodels.checkout_vm import CheckoutViewModel


class CheckoutModal(ModalView):
    """Kauf-Dialog, rein angetrieben vom CheckoutViewModel.

    checkout.state != hidden -> Modal öffnen, Texte/Bild aus dem VM lesen.
    checkout.state == hidden  -> Modal schließen.
    """

    checkout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(.4, .4, .4, 1)
            self.bg = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(12)]
            )

        self.bind(
            size=self._update_canvas,
            pos=self._update_canvas
        )

        self.content = BoxLayout(
            orientation='vertical',
            padding=dp(24)
        )
        self.add_widget(self.content)

        self.image = Image(size_hint_y=.7)
        self.content.add_widget(self.image)

        self.flavorLabel = Label(size_hint_y=.1)
        self.content.add_widget(self.flavorLabel)

        self.hintLabel = Label(font_size='17sp', size_hint_y=.1)
        self.content.add_widget(self.hintLabel)

    def on_checkout(self, instance, checkout):
        checkout.bind(state=self._on_state)

    def _on_state(self, checkout, state):
        if state == CheckoutViewModel.HIDDEN:
            if self._is_open:
                self.dismiss(animation=False)
            return

        item_vm = checkout.item
        if item_vm is None:
            return

        self.flavorLabel.text = checkout.title
        self.hintLabel.text = checkout.hint
        self.hintLabel.color = checkout.hint_color
        self.auto_dismiss = state != CheckoutViewModel.THANKS

        rawImageData = io.BytesIO(item_vm.image)
        self.image.texture = CoreImage(rawImageData, ext='png').texture

        if not self._is_open:
            self.open()

    def on_dismiss(self, *args, **kwargs):
        logger.debug("CheckoutModal dismissed")
        if self.checkout is not None and self.checkout.state != CheckoutViewModel.HIDDEN:
            self.checkout.close()

    def _update_canvas(self, *args, **kwargs):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def open(self, *_args, **kwargs):
        kwargs['animation'] = False
        super(CheckoutModal, self).open(**kwargs)

    def dismiss(self, *_args, **kwargs):
        kwargs['animation'] = False
        super(CheckoutModal, self).dismiss(**kwargs)
