from .HardwareComponent import HardwareComponent
import RPi.GPIO as GPIO
import time
from .config import buzzerPin
import threading

class Buzzer(HardwareComponent):
    def __init__(self, ):
        super().__init__()
        self.pin = buzzerPin
        
    def initialize(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)

    def _beep_job(self, count, duration, delay):
            """To jest funkcja, która będzie działać w osobnym wątku"""
            for _ in range(count):
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(duration)
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(delay)

    def _start_thread(self, count, duration, delay=0.1):
        t = threading.Thread(target=self._beep_job, args=(count, duration, delay), daemon=True)
        t.start()

    
    def beep_success(self):
        self._start_thread(count=1, duration=0.1)

    def beep_error(self):
        self._start_thread(count=3, duration=0.1, delay=0.1)

    def beep_input(self):
        self._start_thread(count=1, duration=0.05)
        
    def cleanup(self):
        GPIO.output(self.pin, GPIO.HIGH)