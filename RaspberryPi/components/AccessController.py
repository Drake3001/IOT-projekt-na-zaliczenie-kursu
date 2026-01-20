import json 
import time
import RPi.GPIO as GPIO
import threading 

from .RfidReader import RfidReader
from .LcdDisplay import LcdDisplay
from .BuzzerComp import Buzzer
from .MqttClient import MqttClientWrapper

class AccessController():
    MODE_VALIDATION = "VALIDATION"
    MODE_REGISTRATION = "REGISTRATION"
    def __init__(self):
        self.is_busy= False 
        self.current_mode =self.MODE_VALIDATION
        self.rfid = RfidReader()
        self.lcd = LcdDisplay()
        self.buzzer = Buzzer()
        BROKER_IP = "192.168.1.XX" 
        self.mqtt = MqttClientWrapper(broker_address=BROKER_IP, message_callback=self.handle_server_response, mode_callback=self.handle_mode_change)      
        self.initialize()

    def initialize(self):
        print("[System] Inicjalizacja komponentów...")
        self.rfid.initialize()
        self.lcd.initialize()
        self.buzzer.initialize()
        self.mqtt.connect()
        
        self.lcd.show_welcome()
        print("[System] Gotowy. Zbliż kartę.")

    def run(self): 
        try: 
            while True:
                if self.is_busy:
                    time.sleep(0.1)
                    continue
                uid = self.rfid.check_card()
                
                if uid:
                    self.is_busy= True; 
                    print(f"[Karta] Wykryto UID: {uid}")
                    self.buzzer.beep_input()
                    self.lcd.show_verifying()
                    if self.current_mode == self.MODE_VALIDATION:
                        self.mqtt.publish_verification(uid)
                    
                    elif self.current_mode == self.MODE_REGISTRATION:
                        self.mqtt.publish_registration(uid)
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n[System] Zamykanie...")
            self.rfid.cleanup()
            self.lcd.cleanup()
            self.buzzer.cleanup()
            self.mqtt.disconnect()
            GPIO.cleanup()

    def handle_mode_change(self, new_mode):
        """Obsługa zmiany trybu z Master Karty"""
        print(f"[TRYB] Zmiana trybu na: {new_mode}")
        if new_mode == "REGISTRATION":
            self.current_mode = self.MODE_REGISTRATION
            self.lcd.show_registration_mode()
        else:
            self.current_mode = self.MODE_VALIDATION
            self.lcd.show_welcome()
        
        self.is_busy = False

    def handle_server_response(self, data):
       
        msg_type = data.get("type", "UNKNOWN") # "VERIFICATION_RESULT" | "REGISTRATION_RESULT"
        access_granted = data.get("access", False)
        message = data.get("message", "")
        status = data.get("status", "")
        
        print(f"[WYNIK] Typ: {msg_type} | Status: {status}")


        if msg_type == "VERIFICATION_RESULT": 
            if access_granted:
                print(f" -> Przyznano dostęp: {message}")            
                self.lcd.show_access_granted(message)
                self.buzzer.beep_success()
                
            else:
                print(f" -> Odmowa: {message}")
                if status in  ['DENIED_INACTIVE', 'DENIED_EXPIRED']: 
                    self.lcd.show_access_denied(message)
                else: 
                    self.lcd.show_new_card_detected()
                self.buzzer.beep_error()
        elif msg_type == "REGISTRATION_RESULT":
            if status == "CREATED":
                print(" -> Nowa karta dodana")
                self.lcd.show_new_card_registration() 
                self.buzzer.beep_success()
            elif status == "UPDATED":
                print(" -> Karta zaktualizowana")
                self.lcd.show_card_extended_registration() 
                self.buzzer.beep_success()
            else:
                print(" -> Błąd rejestracji")
                self.lcd.show_access_denied("Blad zapisu DB")
                self.buzzer.beep_error()
        else:
            print(f"Nieznany typ wiadomości: {msg_type}")
        self._reset_state_after_delay(2.0)

    def _reset_state_after_delay(self, delay):
        def job():
            time.sleep(delay)
            if self.current_mode == self.MODE_REGISTRATION:
                self.lcd.show_registration_mode()
            else:
                self.lcd.show_welcome()
            self.is_busy = False 
            
        t = threading.Thread(target=job, daemon=True)
        t.start()