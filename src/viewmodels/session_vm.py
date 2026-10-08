from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from helper import logger, convertCentsToString
from viewmodels.checkout_vm import CheckoutViewModel
from viewmodels.items_vm import ItemListViewModel
from viewmodels.amount_stepper_vm import AmountStepperViewModel
from viewmodels.admin_vm import AdminViewModel
from viewmodels.stock_stepper_vm import StockStepperViewModel
from viewmodels.stock_vm import StockViewModel

PROGRESS_TICK = 1 / 20.


class SessionViewModel(EventDispatcher):
    """Session-Zustand: Login, Balance, Fehleranzeige, Logout-Timer.

    Commands: on_tag(), select_item(), logout().
    Alle Zustandsänderungen laufen über Properties; die Views binden nur.
    """

    GREET_DEFAULT = "Chip her!"
    NAME_DEFAULT = "UNBEKANNT"

    ADMIN_MENU = "AdminScreen"
    BALANCE_SCREEN = "BalanceScreen"
    STOCK_SCREEN = "StockScreen"
    ADMIN_SCREENS = (ADMIN_MENU, BALANCE_SCREEN, STOCK_SCREEN)

    active_screen = StringProperty("LoginScreen")
    user_logged_in = BooleanProperty(False)
    user_is_admin = BooleanProperty(False)
    greet = StringProperty(GREET_DEFAULT)
    greet_color = ListProperty([1, 1, 1, 1])
    username = StringProperty(NAME_DEFAULT)
    balance = StringProperty("0,00 €")
    balance_negative = BooleanProperty(False)
    logout_progress = NumericProperty(0)

    def __init__(self, service, checkout_vm=None, login_timeout=30,
                 login_error_timeout=3, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.checkout = checkout_vm or CheckoutViewModel()
        self.items = ItemListViewModel(self)
        self.stepper = AmountStepperViewModel(service)
        self.admin = AdminViewModel(service, self.stepper)
        self.stock_stepper = StockStepperViewModel(service)
        self.stock = StockViewModel(service, self.stock_stepper)
        #hat der Admin am eingeloggten User gedreht: Balance-Anzeige aktualisieren
        self.stepper.bind(on_applied=self._balance_applied)
        self.login_timeout = login_timeout
        self.login_error_timeout = login_error_timeout
        self._logout_event = None
        self._progress_event = None
        self._progress_duration = login_timeout
        self._greet_event = None

    def on_tag(self, tag_id: str):
        user = self.service.currentUser
        #Login
        if user is None or user.tag_id != tag_id:
            self.logout()
            self._login(tag_id)
            return

        #bezahle
        if self.service.selectedItem is not None:
            self._pay(tag_id)
            return

        logger.debug(f"Bekam Tag, aber weder login noch bezahle :/")

    def select_item(self, item_vm):
        funds = self.service.select_item(item_vm.item)
        self.checkout.open(item_vm, funds)
        self._start_login_timer(self.login_timeout)

    def logout(self):
        self.service.logout()
        self.checkout.close()
        self.stepper.close()
        self.stock_stepper.close()
        self._stop_login_timer()
        self._cancel_greet_error()
        self.user_logged_in = False
        self.user_is_admin = False
        self.username = self.NAME_DEFAULT
        self.balance = convertCentsToString(0)
        self.balance_negative = False
        self._reset_greet()
        self.active_screen = "LoginScreen"

    def notify_activity(self):
        # Touch-Eingabe: laufenden Logout-Timer von vorn starten
        if self._logout_event is not None:
            self._start_login_timer(self._progress_duration)

    def enter_admin(self):
        # nur mit Flag, offenes Checkout wird nicht mitgenommen
        if not self.user_is_admin:
            return
        self.checkout.close()
        self.active_screen = self.ADMIN_MENU

    def show_admin(self, screen):
        """Zu einem Admin-Screen wechseln (Menü oder Untermenü)."""
        if not self.user_is_admin or screen not in self.ADMIN_SCREENS:
            return
        if screen == self.BALANCE_SCREEN:
            self.admin.load()
        if screen == self.STOCK_SCREEN:
            self.stock.load()
        self.active_screen = screen

    def back_to_admin_menu(self):
        """Aus dem Untermenü zurück, offene Bearbeitung verwerfen."""
        self.stepper.close()
        self.stock_stepper.close()
        self.active_screen = self.ADMIN_MENU

    def leave_admin(self):
        self.active_screen = "CheckoutScreen"

    def _balance_applied(self, stepper, ok, user):
        if ok and self.user_logged_in and self.service.currentUser is not None:
            self._display_balance(self.service.currentUser)

    def _login(self, tag_id: str):
        user = self.service.login(tag_id)
        if user is None:
            self.greet = f"Fehler bei Chip: {tag_id}"
            self.greet_color = [1, 0, 0, 1]
            self._cancel_greet_error()
            self._greet_event = Clock.schedule_once(
                lambda dt: self._reset_greet(), self.login_error_timeout)
            return

        self.user_logged_in = True
        self.user_is_admin = user.isAdmin
        self.username = user.firstname
        self._display_balance(user)
        self.items.load(user)
        self.active_screen = "CheckoutScreen"
        self._start_login_timer(self.login_timeout)

    def _pay(self, tag_id: str):
        logger.info(f"User mit Tag {tag_id} will bezahlen")
        item_vm = self.checkout.item
        success = self.service.pay(tag_id)
        if success:
            self.checkout.bought()
            self._display_balance(self.service.currentUser)
            if item_vm is not None:
                item_vm.refresh_stock()
            self._start_login_timer(5)
        else:
            logger.debug("Kauf fehlgeschlagen")

    def _start_login_timer(self, timeout):
        self._stop_login_timer()
        self._logout_event = Clock.schedule_once(lambda dt: self.logout(), timeout)
        self._progress_duration = timeout
        self._progress_event = Clock.schedule_interval(self._tick_progress, PROGRESS_TICK)
        logger.debug(f"Login timeout startet ({timeout})")

    def _tick_progress(self, dt):
        self.logout_progress = min(1., self.logout_progress + dt / self._progress_duration)
        return self.logout_progress < 1.

    def _stop_login_timer(self):
        if self._logout_event is not None:
            Clock.unschedule(self._logout_event)
            self._logout_event = None
        if self._progress_event is not None:
            Clock.unschedule(self._progress_event)
            self._progress_event = None
        self.logout_progress = 0

    def _display_balance(self, user):
        self.balance = convertCentsToString(user.balance)
        self.balance_negative = user.balance < 0

    def _cancel_greet_error(self):
        if self._greet_event is not None:
            Clock.unschedule(self._greet_event)
            self._greet_event = None

    def _reset_greet(self):
        self.greet = self.GREET_DEFAULT
        self.greet_color = [1, 1, 1, 1]
