import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import threading
import time

class RFIDService():
    
    def __init__(self, callback, sleeptimer):
        self.reader = SimpleMFRC522()
        self.on_tag = callback
        self.running = False
        self.sleeptimer = sleeptimer

    def start(self):
        # TODO GPIO noch sicherheitshalber frisch initieren
        self.running = True
        threading.Thread(
            target=self._run,
            daemon=True

        ).start()
        
    def stop(self):
        self.running = False
        

    def _run(self):
        while self.running:
            tag = self.reader.read()
            self.on_tag(tag)
            time.sleep(self.sleeptimer)
        
        # TODO: GPIO wieder ordentlich hinterlassen