from django.core.management.base import BaseCommand
from core.models import RfidCard, EntryLog
from django.utils import timezone
import paho.mqtt.client as mqtt
import json
import datetime

class Command(BaseCommand):
    help = 'Uruchamia nasłuchiwanie MQTT dla systemu RFID'

    def handle(self, *args, **options):
        # Konfiguracja
        BROKER = "localhost"
        
        # Tematy
        TOPIC_VERIFY = "reader/verification"
        TOPIC_REGISTER = "reader/register"
        TOPIC_RESPONSE = "reader/response"
        TOPIC_MODE = "reader/mode"  

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS(f"Połączono z brokerem (Kod: {rc})"))
                client.subscribe([
                    (TOPIC_VERIFY, 0), 
                    (TOPIC_REGISTER, 0),
                    (TOPIC_MODE, 0) 
                ])
                self.stdout.write(f"Nasłuchuję na: {TOPIC_VERIFY}, {TOPIC_REGISTER} oraz {TOPIC_MODE}")
            else:
                self.stdout.write(self.style.ERROR(f"Błąd połączenia: {rc}"))

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                
                self.stdout.write(f"[{msg.topic}] Payload: {payload}")


                if msg.topic == TOPIC_MODE:
                    new_mode = payload.get("mode")
                    self.stdout.write(self.style.WARNING(f"!!! ZMIANA TRYBU SYSTEMU NA: {new_mode} !!!"))


                elif msg.topic == TOPIC_VERIFY:
                    uid = payload.get('uid')
                    handle_verification(client, uid)

                elif msg.topic == TOPIC_REGISTER:
                    uid = payload.get('uid')
                    handle_registration(client, uid)

            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR("Błąd dekodowania JSON"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Błąd ogólny: {e}"))


        def handle_verification(client, uid):
            access_granted = False
            message = ""
            status_enum = EntryLog.AccessStatus.DENIED_UNKNOWN
            card_obj = None

            try:
                card = RfidCard.objects.get(uid=uid)
                card_obj = card
                
                if card.is_valid():
                    access_granted = True
                    # Pobieramy nazwę użytkownika (zabezpieczenie jeśli user jest None)
                    owner_name = card.user.full_name if card.user else "Gość"
                    message = f"Witaj {owner_name}!"
                    status_enum = EntryLog.AccessStatus.GRANTED
                elif not card.valid:
                    message = "Karta zablokowana"
                    status_enum = EntryLog.AccessStatus.DENIED_INACTIVE
                else:
                    message = "Karta przeterminowana"
                    status_enum = EntryLog.AccessStatus.DENIED_EXPIRED
                    
            except RfidCard.DoesNotExist:
                message = "Brak karty w bazie"
                status_enum = EntryLog.AccessStatus.DENIED_UNKNOWN

            EntryLog.objects.create(
                card=card_obj,
                uid_raw=uid,
                status=status_enum
            )
            
            response = {
                "type": "VERIFICATION_RESULT", 
                "access": access_granted,
                "message": message,
                "status": status_enum.value 
            }
            client.publish(TOPIC_RESPONSE, json.dumps(response))
            self.stdout.write(self.style.SUCCESS(f"Odesłano weryfikację: {status_enum.value}"))

        def handle_registration(client, uid):
            status_enum = EntryLog.AccessStatus.REGISTERED
            card_obj = None
            response_status = ""
            response_msg = ""
            
            try:
                card = RfidCard.objects.get(uid=uid)
                
                # Przedłużenie o 30 dni
                card.expiry_date = timezone.now() + datetime.timedelta(days=30)
                card.valid = True
                card.save()
                
                status_enum = EntryLog.AccessStatus.UPDATED
                response_status = "UPDATED"
                response_msg = "Waznosc przedluzona"
                self.stdout.write(self.style.SUCCESS(f"Zaktualizowano kartę: {uid}"))

            except RfidCard.DoesNotExist:
                # Tworzenie nowej
                card = RfidCard.objects.create(
                    uid=uid,
                    expiry_date=timezone.now() + datetime.timedelta(days=30), 
                    valid=True,
                    user=None 
                )
                
                response_status = "CREATED"
                response_msg = "Dodano nowa karte"
                self.stdout.write(self.style.SUCCESS(f"Utworzono nową kartę: {uid}"))

            card_obj = card
            EntryLog.objects.create(
                card=card_obj,
                uid_raw=uid,
                status=status_enum
            )

            response = {
                "type": "REGISTRATION_RESULT", 
                "access": False, 
                "message": response_msg,
                "status": response_status 
            }
            client.publish(TOPIC_RESPONSE, json.dumps(response))

        # Start klienta
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        
        try:
            client.connect(BROKER, 1883, 60)
            self.stdout.write(self.style.WARNING("Worker MQTT uruchomiony..."))
            client.loop_forever()
        except ConnectionRefusedError:
             self.stdout.write(self.style.ERROR("Nie można połączyć z Mosquitto. Czy usługa działa?"))