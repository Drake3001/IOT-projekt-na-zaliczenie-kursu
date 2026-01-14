import json 
import time
import RPi.GPIO as GPIO

from .RfidReader import RfidReader
from .LcdDisplay import LcdDisplay
from .BuzzerComp import Buzzer

class AccessController(): 
    def __init__(self): 
        self.rfid = RfidReader()
        self.lcd = LcdDisplay()
        self.buzzer = Buzzer()
        
        self.VALID_TEST_UID = "136-4-22-11" 
        
        self.initialize()

    def initialize(self):
        print("[System] Inicjalizacja komponentów...")
        self.rfid.initialize()
        self.lcd.initialize()
        self.buzzer.initialize()
        
        self.lcd.show_welcome()
        print("[System] Gotowy. Zbliż kartę.")

    def run(self): 
        try: 
            while True: 
                uid = self.rfid.check_card()
                
                if uid:
                    self.handle_mock_validation(uid)
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n[System] Zamykanie...")
            self.rfid.cleanup()
            self.lcd.cleanup()
            self.buzzer.cleanup()
            GPIO.cleanup()

    def handle_mock_validation(self, uid):
        """
        Symuluje proces weryfikacji bez użycia MQTT/Django.
        """
        print(f"[Karta] Wykryto UID: {uid}")
        
        self.buzzer.beep_input()
        self.lcd.show_verifying()
        
        time.sleep(0.5)

        if uid == self.VALID_TEST_UID:
            self._access_granted_sequence()
        else:
            self._access_denied_sequence()

        time.sleep(2.0)
        self.lcd.show_welcome()

    def _access_granted_sequence(self):
        print(" -> Decyzja: WSTĘP DOZWOLONY")
        self.lcd.show_access_granted("Test User") 
        self.buzzer.beep_success()

    def _access_denied_sequence(self):
        print(" -> Decyzja: ODMOWA")
        self.lcd.show_access_denied("Brak dostepu")
        self.buzzer.beep_error()