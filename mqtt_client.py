import paho.mqtt.client as mqtt
from flask_mqtt import Mqtt
import os

# Configure MQTT client
mqtt_client = Mqtt()

# Define default MQTT settings
DEFAULT_BROKER = 'localhost'
DEFAULT_PORT = 1883
DEFAULT_USERNAME = None
DEFAULT_PASSWORD = None

# Get MQTT settings from environment or use defaults
MQTT_BROKER = os.environ.get('MQTT_BROKER', DEFAULT_BROKER)
MQTT_PORT = int(os.environ.get('MQTT_PORT', DEFAULT_PORT))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', DEFAULT_USERNAME)
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', DEFAULT_PASSWORD)

# Flag to check if MQTT should be enabled
MQTT_ENABLED = os.environ.get('MQTT_ENABLED', 'false').lower() == 'true'

def publish(topic, message):
    """Safe wrapper for MQTT publish that won't crash if MQTT is not available"""
    try:
        if hasattr(mqtt_client, 'publish'):
            mqtt_client.publish(topic, message)
    except Exception as e:
        print(f"MQTT Publish Error: {str(e)}")

def init_app(app):
    """Initialize MQTT client with the app if enabled"""
    if not MQTT_ENABLED:
        print("MQTT is disabled. Set MQTT_ENABLED=true to enable it.")
        return
        
    app.config['MQTT_BROKER_URL'] = MQTT_BROKER
    app.config['MQTT_BROKER_PORT'] = MQTT_PORT
    
    if MQTT_USERNAME and MQTT_PASSWORD:
        app.config['MQTT_USERNAME'] = MQTT_USERNAME
        app.config['MQTT_PASSWORD'] = MQTT_PASSWORD
    
    app.config['MQTT_KEEPALIVE'] = 60
    app.config['MQTT_TLS_ENABLED'] = False
    
    try:
        mqtt_client.init_app(app)
        
        @mqtt_client.on_connect()
        def handle_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker")
                mqtt_client.subscribe('user/#')
            else:
                print(f"Failed to connect to MQTT Broker, return code: {rc}")
        
        @mqtt_client.on_message()
        def handle_message(client, userdata, message):
            print(f"Received message on topic {message.topic}: {message.payload.decode()}")
    except Exception as e:
        print(f"MQTT Initialization Error: {str(e)}")
