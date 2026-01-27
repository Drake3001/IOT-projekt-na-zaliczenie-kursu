from .HardwareComponent import HardwareComponent
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import os
import textwrap

class LcdDisplay(HardwareComponent):
    
    def __init__(self):
        super().__init__()
        os.system('sudo systemctl stop ip-oled.service')
        self.disp = SSD1331.SSD1331()
        self.width = self.disp.width
        self.height = self.disp.height
        
        try:
            self.font_large = ImageFont.truetype('./lib/oled/Font.ttf', 15)
            self.font_small = ImageFont.truetype('./lib/oled/Font.ttf', 10)
        except OSError:
            print("[OLED WARNING] Nie znaleziono Font.ttf, używam domyślnej.")
            self.font_large = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def initialize(self):
        try:
            self.disp.Init()
            self.disp.clear()
            print("OLED Initialized")
        except Exception as e:
            print(f"[OLED ERROR] Inicjalizacja nieudana: {e}")

    def _draw_screen(self, title, subtitle="", bg_color="BLACK", text_color="WHITE"):
        image = Image.new("RGB", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)

        title_lines = textwrap.wrap(title, width=12)
        current_y = 5
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_large)
            w = bbox[2] - bbox[0]
            draw.text(((self.width - w) // 2, current_y), line, font=self.font_large, fill=text_color)
            current_y += 16 

        if subtitle:
            subtitle_lines = textwrap.wrap(subtitle, width=18)
            current_y = max(current_y + 4, 35) 
            for line in subtitle_lines:
                bbox = draw.textbbox((0, 0), line, font=self.font_small)
                w = bbox[2] - bbox[0]
                if current_y + 10 <= self.height:
                    draw.text(((self.width - w) // 2, current_y), line, font=self.font_small, fill=text_color)
                    current_y += 12

        self.disp.ShowImage(image, 0, 0)


    def show_welcome(self):
        self._draw_screen("SYSTEM RFID", "Zbliz karte do czytnika", bg_color="BLUE")

    def show_registration_mode(self):
        self._draw_screen("REJESTRACJA", bg_color="PURPLE")

    def show_verifying(self):
        self._draw_screen("WERYFIKACJA", "Czekaj...", bg_color="BLACK")

    def show_access_granted(self, user_name):
        self._draw_screen("DOSTĘP", user_name, bg_color="GREEN", text_color="BLACK")

    def show_access_denied(self, reason="Brak uprawnien"):
        self._draw_screen("ODMOWA", reason, bg_color="RED", text_color="WHITE")

    def show_new_card_detected(self):
        self._draw_screen("NIEZNANA", "Zarejestruj karte", bg_color="ORANGE", text_color="BLACK")

    def show_new_card_registration(self):
        self._draw_screen("SUKCES", "Karta dodana", bg_color="GREEN", text_color="BLACK")

    def show_card_extended_registration(self): 
        self._draw_screen("KARTA", "JUZ ISTNIEJE", bg_color="BLUE", text_color="WHITE")
        
    def show_status(self, line1, line2):
        self._draw_screen(line1, line2)

    def cleanup(self):
        self.disp.clear()
        self.disp.reset()