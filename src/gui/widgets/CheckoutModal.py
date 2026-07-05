from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image, CoreImage
from kivy.graphics import Color, RoundedRectangle
import io
from helper import convertCentsToString
from kivy.metrics import dp
from helper.logger import logger
from weakref import WeakMethod

class CheckoutModal(ModalView):

    def __init__(self, **kwargs):
        self.item = kwargs.pop('item')
        funds = kwargs.pop('funds')
        super(CheckoutModal, self).__init__(**kwargs)

        
        self.content = BoxLayout(
            orientation='vertical',
            padding = dp(24)
            )
        self.add_widget(self.content)

        rawImageData = io.BytesIO(self.item.png)
        self.image = Image(size_hint_y=.7)
        self.image.texture = CoreImage(rawImageData, ext='png').texture
        self.content.add_widget(self.image)

        self.flavorLabel = Label(
            text=f"{self.item.flavor} - {convertCentsToString(self.item.price)}" ,
            size_hint_y = .1
            )
        self.content.add_widget(self.flavorLabel)

        self.hintLabel = Label(
            text = "Zum bezahlen Chip erneut scannen." if funds else "Nicht genüngend Gutgaben",
            font_size= '17sp',
            size_hint_y= .1,
            color= (1, .5, .5, 1) if not funds else (1,1,1,1)
        )
        self.content.add_widget(self.hintLabel)

        self.background_color = (0,0,0,0)
        with self.canvas.before:
            Color(.4,.4,.4,1)
            self.bg=RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius = [dp(12)]
            )
        
        self.bind(
            size=self._update_canvas,
            pos = self._update_canvas
        )
        App.get_running_app().ev.bind(
            on_logout=self.dismiss,
            on_item_bought=self.on_item_bought
        )

    def on_item_bought(self, *args, **kwargs):
        self.hintLabel.text = "Danke für deinen Einkauf!"
        self.hintLabel.color = (.5, 1, .5, 1)
        self.auto_dismiss = False
        logger.debug(f'on_item_bought called für modal {self}')


    def on_dismiss(self, *args, **kwargs):
        App.get_running_app().ev.dispatch('on_CheckoutModal_dismiss')



    def _update_canvas(self, *args, **kwargs):
        self.bg.pos=self.pos
        self.bg.size=self.size


    def open(self, *_args, **kwargs):
        kwargs['animation'] = False
        super(CheckoutModal, self).open(**kwargs)
        
    def dismiss(self, *_args, **kwargs):
        kwargs['animation'] = False
        super(CheckoutModal, self).dismiss(**kwargs)