import paho.mqtt.client as mqtt
import json
import time
import sys

# --- KONFIGURACJA ---
BROKER = "localhost"  
TOPIC_VERIFY = "reader/verification"
TOPIC_REGISTER = "reader/register"
TOPIC_RESPONSE = "reader/response"
TOPIC_MODE = "reader/mode"

# --- STAN SYMULATORA ---
current_mode = "VALIDATION" 
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[SYMULATOR] Połączono z brokerem (kod {rc})")
        client.subscribe([(TOPIC_RESPONSE, 0), (TOPIC_MODE, 0)])
    else:
        print(f"Błąd połączenia: {rc}")

def on_message(client, userdata, msg):
    global current_mode
    
    try:
        payload = json.loads(msg.payload.decode())

        if msg.topic == TOPIC_MODE:
            new_mode = payload.get("mode")
            if new_mode in ["VALIDATION", "REGISTRATION"]:
                current_mode = new_mode
                print("\n" + "#"*50)
                print(f"!!! OTRZYMANO ROZKAZ ZMIANY TRYBU NA: {current_mode} !!!")
                print("#"*50 + "\n")
                print(f"[{current_mode}] Wpisz UID karty:")

        elif msg.topic == TOPIC_RESPONSE:
            msg_type = payload.get("type", "UNKNOWN")
            status = payload.get("status", "")
            message = payload.get("message", "")
            access = payload.get("access", False)
            print("X", access)

            print("\n" + "-"*40)
            print(f" [WYNIK: {msg_type}]")
            print(f" Status:    {status}")
            print(f" Wiadomość: {message}")
            
            if msg_type == "VERIFICATION_RESULT":
                print(f" Dostęp:    {'✅ TAK' if access else '❌ NIE'}")
            
            print("-"*40 + "\n")
            print(f"[{current_mode}] Wpisz UID karty:")

    except Exception as e:
        print(f"Błąd przetwarzania wiadomości: {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, 1883, 60)
    client.loop_start()
    
    print("\n" + "="*50)
    print(" SYMULATOR RASPBERRY PI URUCHOMIONY")
    print(" 1. Domyślny tryb to VALIDATION.")
    print(" 2. Aby zmienić tryb, wyślij komendę przez Django (przycisk)")
    print("    lub ręcznie opublikuj JSON na temat 'reader/mode'.")
    print("="*50 + "\n")
    
    while True:
        uid = input(f"[{current_mode}] Podaj UID (np. 1111): ")
        
        if uid.strip():
            payload = json.dumps({"uid": uid.strip()})
            
            if current_mode == "VALIDATION":
                print(f" >> [WERYFIKACJA] Wysyłam {uid}...")
                client.publish(TOPIC_VERIFY, payload)
            
            elif current_mode == "REGISTRATION":
                print(f" >> [REJESTRACJA] Wysyłam {uid}...")
                client.publish(TOPIC_REGISTER, payload)
            
            time.sleep(0.5)

except KeyboardInterrupt:
    print("\nZamykanie symulatora...")
    client.loop_stop()
    client.disconnect()
except Exception as e:
    print(f"Błąd krytyczny: {e}")