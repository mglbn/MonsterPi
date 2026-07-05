from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.app import App
from model import User
from helper import logger, convertCentsToString
from gui.widgets.LogoutButton import LogoutButton



class UserInfoLayout(BoxLayout):


    def __init__(self, **kwargs):
        super(UserInfoLayout, self).__init__(**kwargs)
        self.size_hint = (1, .15)
        self.orientation = 'horizontal'

        self.NameLabel = Label(text='Hallo UNBEKANNT')
        self.add_widget(self.NameLabel)
        self.BalanceLabel = Label(text=convertCentsToString(0))
        self.add_widget(self.BalanceLabel)

        self.logout_button = LogoutButton(
            text = "Abmelden",
            size_hint_y = 0.5,
            size_hint_x = 0.8,
            pos_hint = {"top": 0.5},
            duration = App.get_running_app().config["loginTimeout"]
        )
        self.button_wrapper = AnchorLayout(
            anchor_y = 'center'
        )
        self.button_wrapper.add_widget(self.logout_button)

        self.add_widget(self.button_wrapper)

        App.get_running_app().ev.bind(
            on_login=self.on_login_or_on_item_bought,
            on_item_bought=self.on_login_or_on_item_bought,
            on_logout=self.on_logout
        )

    def on_login_or_on_item_bought(self, *args, **kwargs):
        user: User = kwargs.get("user")
        if user:
            self._display_user(user)
        else:
            self._display_no_user()
        
    def on_logout(self, *args):
        self._display_no_user()

    # Darf nicht mit None aufgerufen werden
    def _display_user(self, user: User):
        username = "UNBEKANNT"
        negativ = False
        balance = convertCentsToString(0)
        if user:
            username = user.firstname
            balance = convertCentsToString(user.balance)
            negativ = user.balance < 0
        self.NameLabel.text = f"Hallo {username}"
        self.BalanceLabel.text = balance
        self.BalanceLabel.color = (1, .5, .5, 1) if negativ else (1,1,1,1)
        self.logout_button.start_Animation()
        logger.debug(f"UserInfoLayout: Nutzer {user.id} dargestellt")

    def _display_no_user(self):
        self.NameLabel.text= 'Hallo UNBEKANNT'
        self.BalanceLabel.text = '0,00 €'
        self.BalanceLabel.color = (1,1,1,1)
        self.logout_button.reset()
        logger.debug("UserInfoLayout zurücksgesetzt")
        
               
        