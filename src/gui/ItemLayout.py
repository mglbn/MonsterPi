from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import CoreImage, Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from gui.BuyButton import BuyButton
from model import Item
from helper import convertCentsToString
import io

class ItemLayout(BoxLayout):

    item = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ItemLayout, self).__init__(**kwargs)
        self.item: Item = kwargs["item"]
        self.orientation = 'vertical'
        self.borderradius = dp(12)
        self.padding = dp(12)
        
        with self.canvas.before:
            Color(.5,.5,.5,.1)
            self.bg_rect = RoundedRectangle(
                pos = self.pos,
                size = self.size,
                radius = [self.borderradius]
            )

        self.bind(pos=self._update_bg, size= self._update_bg)
        
        rawImageData = io.BytesIO(self.item.png)
        self.image = Image(size_hint_x=1, size_hint_y=1)
        self.image.texture = CoreImage(rawImageData, ext='png').texture
        self.add_widget(self.image)

        self.flavorLabel = Label(text=self.item.flavor, size_hint_y=.1)
        self.add_widget(self.flavorLabel)

        self.buyButton = BuyButton(
            text=convertCentsToString(self.item.price),
            size_hint_y=.1,
            color_normal=(.6,.1,.1,1),
            color_pressed=(.3,.1,.1,1),
            color_soldout=(.2,.2,.2,1),
            item = self.item
        )
        self.add_widget(self.buyButton)


    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

