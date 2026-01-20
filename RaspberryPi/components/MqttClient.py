import paho.mqtt.client as mqtt
import json
class MqttClientWrapper:

    TOPIC_VERIFY = "reader/verification"      
    TOPIC_REGISTER = "reader/register"        
    TOPIC_RESPONSE = "reader/response"        
    TOPIC_SET_MODE = "reader/mode"


    def __init__(self, broker_address, message_callback, mode_callback):
        self.broker = broker_address
        self.message_callback = message_callback
        self.mode_callback = mode_callback
        self.connected = False

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self):
        try:
            print(f"[MQTT] Łączenie z brokerem {self.broker}...")
            self.client.connect(self.broker, 1883, 60)
            
            self.client.loop_start() 
        except Exception as e:
            print(f"[MQTT ERROR] Nie można połączyć: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("[MQTT] Rozłączono")

    def publish_verification(self, uid):
        if self.connected:
            try:
                payload = json.dumps({"uid": uid})
                self.client.publish(self.TOPIC_VERIFY, payload)
            except Exception as e:
                print(f"[MQTT ERROR] Publish verify failed: {e}")
        else:
            print(f"[MQTT WARNING] Cannot publish verification - not connected to broker")

    def publish_registration(self, uid):
        if self.connected:
            try:
                print(f"[MQTT] Sending registration request: {uid}")
                payload = json.dumps({"uid": uid})
                self.client.publish(self.TOPIC_REGISTER, payload)
            except Exception as e:
                print(f"[MQTT ERROR] Publish register failed: {e}")
        else:
            print(f"[MQTT WARNING] Cannot publish registration - not connected to broker")
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("[MQTT] Connected successfully.")
            self.connected = True
            client.subscribe([(self.TOPIC_RESPONSE, 0), (self.TOPIC_SET_MODE, 0)])
        else:
            print(f"[MQTT] Connection failed code: {rc}")
            self.connected = False

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode('utf-8')
            data = json.loads(payload_str)
            
            if msg.topic == self.TOPIC_SET_MODE:
                new_mode = data.get("mode") 
                if self.mode_callback and new_mode:
                    self.mode_callback(new_mode)

            elif msg.topic == self.TOPIC_RESPONSE:
                if self.message_callback:
                    self.message_callback(data)

        except json.JSONDecodeError:
            print(f"[MQTT ERROR] Invalid JSON received on {msg.topic}")
        except Exception as e:
            print(f"[MQTT ERROR] Message processing error: {e}")