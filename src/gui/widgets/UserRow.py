from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty


class UserRow(BoxLayout):
    """Zeile der Admin-Userliste (viewclass der RecycleView).

    Die Daten kommen als Dict aus AdminViewModel.users: user (Model),
    name, balance_text, balance_negative.
    """

    user = ObjectProperty(None)
    name = StringProperty("")
    balance_text = StringProperty("")
    balance_negative = BooleanProperty(False)
