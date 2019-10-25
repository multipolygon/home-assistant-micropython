import secrets
import subprocess

subprocess.call(f"mosquitto_sub -h {secrets.MQTT_SERVER} -p {secrets.MQTT_PORT} -u {secrets.MQTT_USER} -P {secrets.MQTT_PASSWORD} -t '#' -v", shell=True)
