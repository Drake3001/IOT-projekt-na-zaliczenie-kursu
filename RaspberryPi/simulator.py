import paho.mqtt.client as mqtt
import json
import time

BROKER = "localhost"
TOPIC_VERIFY = "reader/verification"
TOPIC_RESPONSE = "reader/response"

def on_connect(client, userdata, flags, rc):
    print(f"[SYMULATOR] Połączono z brokerem (kod {rc})")
    client.subscribe(TOPIC_RESPONSE)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("\n" + "="*40)
    print(f" [ODPOWIEDŹ Z SERWERA]")
    print(f" Dostęp:    {data['access']}")
    print(f" Komunikat: {data['message']}")
    print(f" Buzzer:    {data['buzzer']}")
    print("="*40 + "\n")
    print("Wpisz UID karty i naciśnij ENTER:")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, 1883, 60)
    client.loop_start()
    
    print("Symulator RPi uruchomiony.")
    print("Wpisz UID (np. 1111) aby 'przyłożyć kartę'.")
    
    while True:
        uid = input()
        if uid:
            print(f"[SYMULATOR] Wysyłam UID: {uid}...")
            payload = json.dumps({"uid": uid})
            client.publish(TOPIC_VERIFY, payload)
            time.sleep(0.5)

except Exception as e:
    print(f"Błąd: {e}")
    client.loop_stop()