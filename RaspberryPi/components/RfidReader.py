from .HardwareComponent import HardwareComponent
import RPi.GPIO as GPIO
from .config import * # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522
import threading
import time

class RfidReader(HardwareComponent): 
    
    def __init__(self):
        super().__init__()
        self.reader = MFRC522()
    
        self.threshold = 5
        self.last_scanned_uid = None
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def initialize(self):
        print("RFID Reader initialized (Background Thread Mode)")
        self._start_reading_thread()

    def _start_reading_thread(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        last_uid_raw = None
        missed_reads = 0
        last_uid_internal = None

        while self._running:
            read_success = False
            current_uid_str = None

            (status_req, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            
            if status_req == self.reader.MI_OK:
                (status_anti, uid) = self.reader.MFRC522_Anticoll()
                
                if status_anti == self.reader.MI_OK:
                    read_success = True
                    current_uid_str = self.uid_to_string(uid)
                    
                    if read_success:
                        missed_reads = 0
                        if current_uid_str != last_uid_internal:
                            last_uid_internal = current_uid_str
                            with self._lock:
                                self.last_scanned_uid = current_uid_str
                    else:
                        missed_reads += 1
                        if missed_reads > self.threshold:
                            last_uid_internal = None
                            missed_reads = self.threshold
            time.sleep(0.05)

    def check_card(self): 
        with self._lock:
            if self.last_scanned_uid:
                found = self.last_scanned_uid
                self.last_scanned_uid = None 
                return found
            return None
    
    def uid_to_string(self, uid):
        return "-".join([str(x) for x in uid])

    def cleanup(self):
        self._running = False 
        if self._thread:
            self._thread.join(timeout=1.0)
        print('RFID thread stopped')