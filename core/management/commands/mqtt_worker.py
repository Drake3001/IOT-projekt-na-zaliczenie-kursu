from django.core.management.base import BaseCommand
from core.models import RfidCard, EntryLog
from django.utils import timezone
import paho.mqtt.client as mqtt
import json

class Command(BaseCommand):
    help = 'Uruchamia nasłuchiwanie MQTT dla systemu RFID'

    def handle(self, *args, **options):
        BROKER = "localhost"
        TOPIC_VERIFY = "reader/verification"
        TOPIC_RESPONSE = "reader/response"

        def on_connect(client, userdata, flags, rc):
            self.stdout.write(self.style.SUCCESS(f"Połączono z brokerem MQTT (Kod: {rc})"))
            client.subscribe(TOPIC_VERIFY)

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                uid = payload.get('uid')
                
                self.stdout.write(f"Otrzymano UID: {uid}")

                access_granted = False
                message = ""
                status_enum = EntryLog.AccessStatus.DENIED_UNKNOWN
                card_obj = None

                try:
                    card = RfidCard.objects.get(uid=uid)
                    card_obj = card
                    
                    if card.is_valid():
                        access_granted = True
                        message = f"Witaj {card.user.full_name}!"
                        status_enum = EntryLog.AccessStatus.GRANTED
                    elif not card.valid:
                        message = "card zablokowana"
                        status_enum = EntryLog.AccessStatus.DENIED_INACTIVE
                    else:
                        message = "card przeterminowana"
                        status_enum = EntryLog.AccessStatus.DENIED_EXPIRED
                        
                except RfidCard.DoesNotExist:
                    message = "Odmowa dostepu (Brak w bazie)"
                    status_enum = EntryLog.AccessStatus.DENIED_UNKNOWN

                # --- ZAPIS LOGU DO BAZY ---
                EntryLog.objects.create(
                    card=card_obj,
                    uid_raw=uid,
                    status=status_enum
                )
                self.stdout.write(self.style.SUCCESS(f"Zapisano log: {status_enum}"))

                # --- WYSŁANIE ODPOWIEDZI DO RPI ---
                response = {
                    "access": access_granted,
                    "message": message,
                    "buzzer": "short" if access_granted else "long"
                }
                client.publish(TOPIC_RESPONSE, json.dumps(response))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Błąd: {e}"))

        # Start klienta
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        
        try:
            client.connect(BROKER, 1883, 60)
            self.stdout.write(self.style.WARNING("Worker MQTT uruchomiony. Czekam na karty..."))
            client.loop_forever()
        except ConnectionRefusedError:
             self.stdout.write(self.style.ERROR("Nie można połączyć z Mosquitto. Czy usługa działa?"))