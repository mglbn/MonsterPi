from types import SimpleNamespace

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from gui import CheckoutModal, MyScreenManager
from helper import logger
from services.purchase import PurchaseService
from viewmodels import SessionViewModel
import model
import platform

#Check obs auf Raspberry PI läuft. Falls ja, nutze den echten RFID Card Reader anstelle der Dummy Implementation
if ('rpi' in platform.release()):
    from rfid.RFIDService import RFIDService
else:
    from rfid.RFIDDummy import RFIDService

Window.size = (1024, 768)


class MonsterApp(App):

    def build(self):

        config = {
            "loginErrorTime" : 3,
            "loginTimeout" : 30
        }

        service = PurchaseService()
        session_vm = SessionViewModel(
            service,
            login_timeout=config["loginTimeout"],
            login_error_timeout=config["loginErrorTime"]
        )
        self.vm = SimpleNamespace(
            session=session_vm,
            checkout=session_vm.checkout,
            items=session_vm.items,
            stepper=session_vm.stepper,
            admin=session_vm.admin,
            stock_stepper=session_vm.stock_stepper,
            stock=session_vm.stock
        )

        #RFID-Callback kommt aus einem Nebenthread: in den Main-Thread marshallen
        def on_tag(tag):
            Clock.schedule_once(lambda dt: session_vm.on_tag(str(tag[0])))

        #jede Touch-Eingabe startet den Logout-Timer neu
        Window.bind(on_touch_down=lambda *args: session_vm.notify_activity())

        #ModalView gehört nicht in den Widget-Baum: open() hängt es an das Window
        self.checkoutModal = CheckoutModal(
            checkout=session_vm.checkout,
            size_hint=(.6, .8),
            pos_hint={"center_x": .5, "center_y": .5}
        )

        self.rfidService = RFIDService(on_tag, debouncetimer=2)
        self.rfidService.start()
        logger.info("RFID Service gestartet")
        logger.info("Starte Frontend")
        return MyScreenManager()

    def on_stop(self):
        self.rfidService.stop()
        logger.info("App beendet")


if __name__ == "__main__":
    model.init_db()
    logger.info("DB verbindung steht")
    MonsterApp().run()
