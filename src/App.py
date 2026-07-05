from kivy.app import App
from kivy.core.window import Window
from gui import CustomDispatcher
from helper import logger
from gui import MyScreenManager
import model
import platform

#Check obs auf Raspberry PI läuft. Falls ja, nutze den echten RFID Card Reader anstelle der Dummy Implementation 
if ('rpi' in platform.release()):
    from rfid.RFIDService import RFIDService
else:
    from rfid.RFIDDummy import RFIDService

from gui import *


Window.size = (1024, 768)

class MonsterApp(App):
    def build(self):

        self.config = {
            "loginErrorTime" : 3,
            "loginTimeout" : 60
        }

        self.ev = CustomDispatcher(
            loginErrorTimeout= self.config["loginErrorTime"],
            loginTimeout=self.config["loginTimeout"]
            )       

        self.rfidService = RFIDService(self.ev.rfidcallback, 2)
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
    


