from .HardwareComponent import HardwareComponent
import RPi.GPIO as GPIO
from config import * # pylint: disable=unused-wildcard-import
from mfrc522 import MFRC522


class RfidReader(HardwareComponent): 
    
    def __init__(self):
        super()
        self.missed_reads_THRESHOLD = 4
        self.Reader = MFRC522()
        self.last_uid = None
        self.missed_reads = 0 
    
    def initialize(self):
        print("RFID Reader initialized")

    def check_card(self): 
        (status_req, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        
        read_success = False
        found_new_uid = None

        if status_req == self.reader.MI_OK:
            (status_anti, uid) = self.reader.MFRC522_Anticoll()

            if status_anti == self.reader.MI_OK:
                read_success = True
                self.missed_reads = 0 
                current_uid_str = self.uid_to_string(uid)

                if current_uid_str != self.last_uid:                        
                    self.last_uid = current_uid_str
                    found_new_uid = current_uid_str 
                else:
                    pass

        if not read_success:
            self.missed_reads += 1
            if self.missed_reads >= self.missed_reads_threshold:
                self.last_uid = None
                self.missed_reads = self.missed_reads_threshold 

        return found_new_uid
    
    def uid_to_string(self, uid):
        return "-".join([str(x) for x in uid])

    def cleanup(self):
        print('RFIDreader cleanup')