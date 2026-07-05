from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from model import *

class MyScreenManager(ScreenManager):

    dispatcher = ObjectProperty(None)       
    
    def on_dispatcher(self, instance, dispatcher):
        dispatcher.bind(
            on_login=self.on_login,
            on_logout=self.on_logout
        )
    
    def on_login(self, *args, **kwargs):
        self.transition.direction = 'left'
        self.current='CheckoutScreen'

    def on_logout(self, *args):
        self.transition.direction = 'right'
        self.current='LoginScreen'

