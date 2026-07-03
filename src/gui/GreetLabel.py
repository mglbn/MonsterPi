from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from gui import CustomDispatcher
class GreetLabel(Label):

    dispatcher = ObjectProperty(None)

    # def __init__(self, dispatcher: CustomDispatcher, **kwargs):
    #     super().__init__(**kwargs)
    #     dispatcher.bind(on_login_error = self.on_login_error)

    def on_dispatcher(self, instance, dispatcher):
        dispatcher.bind(
            on_login_error=self.on_login_error,
            on_cancel_login_error=self.on_cancel_login_error
        )
    
    def on_login_error(self, *args):
        self.text = "Fehler bei der Anmeldung"
        self.color = 1,0,0,1
        pass

    def on_cancel_login_error(self, *args):
        self.text = "Chip her!"
        self.color = 1,1,1,1