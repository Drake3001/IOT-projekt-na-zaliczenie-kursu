from .HardwareComponent import HardwareComponent
import RPi.GPIO as GPIO
import time
from .config import led1, led2, led3, led4
import threading

class LedController(HardwareComponent):    
    def __init__(self):
        super().__init__()
        self.all_leds = [led1, led2, led3, led4]
        self._stop_animation = threading.Event()
        self._animation_thread = None
        
    def initialize(self):
        for led in self.all_leds:
            GPIO.setup(led, GPIO.OUT)
            GPIO.output(led, GPIO.LOW)
        print("[LED] LEDs initialized")
    
    def cleanup(self):
        self._stop_animation.set()
        if self._animation_thread and self._animation_thread.is_alive():
            self._animation_thread.join(timeout=1.0)
        self._turn_off_all()
    
    def _turn_off_all(self):
        for led in self.all_leds:
            GPIO.output(led, GPIO.LOW)
    
    def _stop_current_animation(self):
        self._stop_animation.set()
        if self._animation_thread and self._animation_thread.is_alive():
            self._animation_thread.join(timeout=1.0)
        self._stop_animation.clear()
    
    def _run_animation(self, animation_func):
        self._stop_current_animation()
        self._turn_off_all()
        self._animation_thread = threading.Thread(
            target=animation_func, 
            daemon=True
        )
        self._animation_thread.start()
    
    
    def show_card_reading(self):
        def animation():
            for led in self.all_leds:
                if self._stop_animation.is_set():
                    break
                GPIO.output(led, GPIO.HIGH)
                time.sleep(0.15)
            
            time.sleep(0.2)
            
            self._turn_off_all()
        
        self._run_animation(animation)
    
    def show_rejected(self):
        def animation():
            for _ in range(5):
                if self._stop_animation.is_set():
                    break
                for led in self.all_leds:
                    GPIO.output(led, GPIO.HIGH)
                time.sleep(0.15)
                
                if self._stop_animation.is_set():
                    break
                self._turn_off_all()
                time.sleep(0.15)
            
            self._turn_off_all()
        
        self._run_animation(animation)
    
    def show_confirmed(self):
        def animation():
            for led in self.all_leds:
                if self._stop_animation.is_set():
                    break
                GPIO.output(led, GPIO.HIGH)
                time.sleep(0.1)
            
            time.sleep(0.5)
            
            for led in self.all_leds:
                if self._stop_animation.is_set():
                    break
                GPIO.output(led, GPIO.LOW)
                time.sleep(0.1)
            
            self._turn_off_all()
        
        self._run_animation(animation)
    
    def stop_all(self):
        self._stop_current_animation()
        self._turn_off_all()
