import threading
import time




class RFIDService():

    _delay = 10
    
    def __init__(self, callback, debouncetimer):
        self.on_tag = callback
        self.running = False
        self.debouncetimer = debouncetimer + self._delay
        self.counter = 0
        self.dummy_tags: list = [
            ('1234','foobar'),
            ('4567','barfoo'),
            ('4567','barfoo')
            
            ]


    def start(self):
        
        self.running = True
        threading.Thread(
            target=self._run,
            daemon=True

        ).start()
        
    
    def stop(self):
        self.running = False
        

    def _run(self):
        time.sleep(5)
        while self.running:
            tag = self.dummy_tags[self.counter % len(self.dummy_tags)]
            self.counter += 1
            self.on_tag(tag) # TODO --> im Callback auch eine Clock zur Abmeldung starten
            time.sleep(self.debouncetimer)
        
       