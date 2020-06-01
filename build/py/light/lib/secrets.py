from json import load, dump

n = '/secrets.json'

l = (
    'WIFI_NAME',
    'WIFI_PASSWORD',
    'MQTT_SERVER',
    'MQTT_USER',
    'MQTT_PASSWORD',
    'MQTT_PREFIX',
)

try:
    with open(n) as f:
        d = load(f)
except:
    d = {}

x = 0
for k in l:
    if k not in d:
        d[k] = input(k + '?:')
        x = 1

if x:
    with open(n, 'w') as f:
        dump(d, f)
        
locals().update(d)
