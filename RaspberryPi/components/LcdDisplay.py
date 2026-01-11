from .HardwareComponent import HardwareComponent
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331  # Import sterownika z Twoich laboratoriów

class LcdDisplay(HardwareComponent):
    
    def __init__(self):
        super().__init__()
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

    def _draw_screen(self, title, subtitle, bg_color="BLACK", text_color="WHITE"):
        """
        Metoda prywatna - rysuje obrazek i wysyła na ekran.
        """
        image = Image.new("RGB", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)

        draw.text((5, 5), title, font=self.font_large, fill=text_color)


        draw.text((5, 25), subtitle, font=self.font_small, fill=text_color)

        self.disp.ShowImage(image, 0, 0)

    # --- METODY LOGICZNE ---

    def show_welcome(self):
        self._draw_screen("SYSTEM RFID", "Zbliz karte...", bg_color="BLUE")

    def show_registration_mode(self):
        self._draw_screen("REJESTRACJA", "Czekam na nowa...", bg_color="PURPLE")

    def show_verifying(self):
        self._draw_screen("WERYFIKACJA", "Prosze czekac...", bg_color="BLACK")

    def show_access_granted(self, user_name):
        safe_name = (user_name[:12] + '..') if len(user_name) > 12 else user_name
        self._draw_screen("DOSTEP", safe_name, bg_color="GREEN", text_color="BLACK")

    def show_access_denied(self, reason="Brak dostepu"):
        self._draw_screen("ODMOWA", reason, bg_color="RED", text_color="WHITE")

    def show_new_card_detected(self, uid):
        self._draw_screen("NOWA KARTA", f"UID: {uid}", bg_color="ORANGE", text_color="BLACK")
        
    def show_status(self, line1, line2):
        self._draw_screen(line1, line2)

    def cleanup(self):
        self.disp.clear()
        self.disp.reset()