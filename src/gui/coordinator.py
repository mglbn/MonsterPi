from kivy.clock import Clock
from helper import logger
from controller import Controller
from model import User
from gui.events.LoginTimer import LoginTimer


class Coordinator():
    """Verbindet Bus-Events mit der Geschäftslogik im Controller.

    Der Coordinator ist der einzige Ort, an dem Event-Bus und Logik
    aufeinandertreffen. Er besitzt den Login-Timer.

    Hinweis: Kivy übergibt gebundenen Callbacks den Dispatcher als erstes
    Positionsargument. Die Handler hier erwarten daher 'bus' als ersten
    Parameter.
    """

    def __init__(self, bus, loginErrorTimeout: int, loginTimeout: int):
        self.bus = bus
        self.loginErrorTimeout = loginErrorTimeout
        self.loginTimeout = loginTimeout
        self.login_timer = LoginTimer(bus)

        bus.bind(
            on_tag=self.on_tag,
            on_logout=self.on_logout,
            on_login=self.on_login,
            on_login_error=self.on_login_error,
            on_item_bought=self.on_item_bought,
            on_BuyButton_release=self.on_BuyButton_release
        )

    def on_tag(self, bus, tag_id, text, *args):
        #Login
        if Controller.currentUser == None or Controller.currentUser.tag_id != tag_id:
            bus.dispatch('on_logout')
            user: User = Controller.loginUser(tag_id)
            if (user == None):
                bus.dispatch('on_login_error', tag_id=tag_id)
            else:
                bus.dispatch('on_login', user=user, items=Controller.getAllItems4User(user))

            return

        #bezahle
        if Controller.currentUser != None and Controller.currentUser.tag_id == tag_id and Controller.shoppingCard != None:
            logger.info(f"User mit Tag {tag_id} will bezahlen")
            is_payed = Controller.payForItem(tag_id)
            if is_payed:
                bus.dispatch('on_item_bought', user=Controller.currentUser)
            else:
                bus.dispatch('on_item_bought_error')
            return

        logger.debug(f"Bekam Tag, aber weder login noch bezahle :/")

    def on_BuyButton_release(self, bus, *args, **kwargs):
        self.login_timer.start_or_reset_login_timer(self.loginTimeout)

    def on_item_bought(self, bus, *args, **kwargs):
        logger.debug("Item erfolgreich gekauft")
        self.login_timer.start_or_reset_login_timer(5)

    def on_logout(self, bus, *args):
        logger.info(f"User wird abgemeldet")
        Controller.logout()

    def on_login(self, bus, *args, **kwargs):
        self.login_timer.start_or_reset_login_timer(self.loginTimeout)

    def on_login_error(self, bus, *args, **kwargs):
        logger.debug(f"Zeige Anmeldefehlermeldung für {self.loginErrorTimeout}")
        Clock.schedule_once(lambda dt: self.bus.dispatch('on_cancel_login_error'), self.loginErrorTimeout)
