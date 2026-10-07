from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty


class MyScreenManager(ScreenManager):

    session = ObjectProperty(None)

    def on_session(self, instance, session):
        session.bind(active_screen=self._on_screen)

    def _on_screen(self, session, screen):
        self.transition.direction = 'left' if screen == 'CheckoutScreen' else 'right'
        self.current = screen
