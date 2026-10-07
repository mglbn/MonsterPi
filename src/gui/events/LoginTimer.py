from kivy.clock import Clock
from helper.logger import logger

class LoginTimer():

    def __init__(self, bus):
        self.bus = bus
        self.event = None

    def start_or_reset_login_timer(self, timeout: int):
        self.cancel_timer()
        self.__start_timer(timeout)

        # Sende Event um Button Animation zu starten
        self.bus.dispatch('on_timer_reset')

    def __start_timer(self, timeout: int):
        # Sende Logout Event wenn timer feuert
        self.event = Clock.schedule_once(lambda dt: self.bus.dispatch('on_logout'), timeout)
        logger.debug(f"Login timeout startet ({timeout})")

    def cancel_timer(self):
        Clock.unschedule(self.event)
        logger.debug("Login timeout cancelt")
