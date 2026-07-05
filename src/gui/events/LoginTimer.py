from kivy.clock import Clock
from kivy.app import App
from helper.logger import logger

class LoginTimer():

    def __init__(self):
        self.event = None

    def start_or_reset_login_timer(self, timeout: int):
        self.cancel_timer()
        self.__start_timer(timeout)

        # Sende Event um Button Animation zu starten
        App.get_running_app().ev.dispatch('on_timer_reset')
        
    def __start_timer(self, timeout: int):
        ev = App.get_running_app().ev

        # Sende Logout Event wenn timer feuert
        self.event = Clock.schedule_once(lambda dt: ev.dispatch('on_logout'), timeout)
        logger.debug(f"Login timeout startet ({timeout})")

    def cancel_timer(self):
        Clock.unschedule(self.event)
        logger.debug("Login timeout cancelt")