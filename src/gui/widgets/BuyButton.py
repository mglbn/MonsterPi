from kivy.app import App
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from gui.widgets.CheckoutModal import CheckoutModal

class BuyButton(Button):
    
    def __init__(self, **kwargs):
        self.colorArray = kwargs.pop('color_normal')
        self.colorArrayPressed = kwargs.pop('color_pressed')
        self.color_soldout = kwargs.pop('color_soldout')
        self.item= kwargs.pop('item')
        super(BuyButton, self).__init__(**kwargs)

        if self.item.inStock < 1 :
            self.colorArray = self.color_soldout
            self.disabled = True

        self.background_color = (0,0,0,0)
        self.background_normal = ''
        with self.canvas.before:
            self.Color = Color(self.colorArray[0],self.colorArray[1],self.colorArray[2],self.colorArray[3])
            self.bg_rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius = [dp(12)]
            )

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            state=self._update_color,
        )

        App.get_running_app().ev.bind(
            on_BuyButton_release=self.on_BuyButton_release,
            on_CheckoutModal_dismiss=self.on_CheckoutModal_dismiss
        )

    def on_release(self):
        App.get_running_app().ev.dispatch('on_BuyButton_release', item= self.item)


    def on_BuyButton_release(self, *args, **kwargs):
        self.disabled = True

    def on_CheckoutModal_dismiss(self, *args, **kwargs):
        if self.item.inStock > 0:
            self.disabled = False

    def _update_canvas(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_color(self, *_):
        self.Color.rgba = self.colorArray if self.state == 'normal' else self.colorArrayPressed

