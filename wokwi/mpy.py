import time
import network
from machine import Pin, PWM
import dht
from umqtt.simple import MQTTClient
import _thread

client = None

sensor = dht.DHT22(Pin(5))
trig = Pin(18, Pin.OUT)
echo = Pin(19, Pin.IN)
led_green = Pin(2, Pin.OUT)
led_red = Pin(4, Pin.OUT)
led_blue = Pin(22, Pin.OUT)
servo = PWM(Pin(15), freq=50)

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
CLIENT_ID = "esp32_silo_controller"
TOPIC_HUMIDITY = "silo/humidity"
TOPIC_DISTANCE = "silo/distance"
TOPIC_ALERT = "silo/alert"
TOPIC_COMMAND = "silo/command"

SSID = "Visitantes"
PASSWORD = ""

def conecta_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando ao WiFi...")
    for _ in range(10):
        if wlan.isconnected():
            print("Conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("Falha na conexão WiFi")
    return False

def conecta_mqtt():
    global client
    try:
        client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        client.set_callback(message_callback)
        client.connect()
        client.subscribe(TOPIC_COMMAND)
        print("Conectado ao MQTT")
        return True
    except Exception as e:
        print("Erro MQTT:", e)
        print("Tentando reconectar...")
        time.sleep(5)
        return conecta_mqtt()

def message_callback(topic, mensagem):
    try:
        mensagem = mensagem.decode('utf-8').lower()
        print("Msg recebida:", mensagem)

        pulse_width = int(40 + (int(mensagem) / 180) * (115 - 40))
        servo.duty(pulse_width)
        time.sleep(1)
        
        led_green.value(0)
        led_red.value(0)
        led_blue.value(0)

    except Exception as e:
        print("Erro no callback:", e)

def medir_distancia():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    pulse_start, pulse_end = 0, 0
    timeout = time.ticks_ms() + 1000

    while echo.value() == 0:
        if time.ticks_ms() > timeout:
            return None
        pulse_start = time.ticks_us()
    
    while echo.value() == 1:
        if time.ticks_ms() > timeout:
            return None
        pulse_end = time.ticks_us()

    return (time.ticks_diff(pulse_end, pulse_start) * 0.0343 / 2)

def ler_sensores():
    global sensor
    try:
        time.sleep(1)
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        if -40 <= temp <= 80 and 0 <= hum <= 100:
            return temp, hum
        else:
            print("Valores fora da faixa:", temp, hum)
            return None, None
    except Exception as e:
        print("Erro ao ler sensores:", e)
        return None, None

def verificar_mensagens():
    while True:
        if client:
            try:
                client.check_msg()
            except Exception as e:
                print("Erro ao verificar mensagens MQTT:", e)
                conecta_mqtt()
        time.sleep(0.1)

def main():
    global client

    if not conecta_wifi():
        return
    if not conecta_mqtt():
        return

    _thread.start_new_thread(verificar_mensagens, ())

    while True:
        distancia = medir_distancia()
        temp, umidade = ler_sensores()

        led_green.value(0)
        led_red.value(0)
        led_blue.value(0)
        
        if distancia is not None and distancia < 10:
            led_blue.value(1)
            # Acende o LED azul se a distância for menor que 10 cm
        
        if temp is not None and umidade is not None:
            print(f"Dist: {distancia:.1f}cm | Umid: {umidade}% | Temp: {temp}°C")
            
            if temp < 30 and umidade < 70:
                led_green.value(1)
                # Acende o LED verde se temp < 30 e umidade < 70%
            else:
                led_red.value(1)
                # Acende o LED vermelho se temperatura ou umidade estiverem fora do limite
            
            try:
                client.publish(TOPIC_DISTANCE, str(distancia))
                client.publish(TOPIC_HUMIDITY, str(umidade))
            except Exception as e:
                print("Erro MQTT:", e)
                conecta_mqtt()

        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Programa encerrado")
