
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
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.rfid.cleanup()
            self.lcd.cleanup()
            self.buzzer.cleanup()
            GPIO.cleanup()

