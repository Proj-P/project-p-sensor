import time
import requests
from gpiozero import Button
from signal import pause

API_URL = 'http://192.168.1.149:5000'
TOKEN = 'b22f74b27eb3881fd9b10ef89f2019c2'
reed_sensor = Button(14)


class Sensor:

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.occupied = False

    def door_opened(self):
        print('Door opened')
        self.occupied = False
        send_status(self.occupied)
        self.end_time = int(time.time())

        time.sleep(1)
        if self.start_time and self.end_time and not self.occupied:
            send_visit(self)

    def door_closed(self):
        print('Door closed')
        self.occupied = True
        send_status(self.occupied)
        self.start_time = int(time.time())


def send_status(status):
    requests.put('%s/locations/status' % API_URL, data={
        'occupied': str(status).lower()
    }, headers={'Authorization': TOKEN})


def send_visit(self):
    # Don't log entries shorter than 10 seconds
    if (self.end_time - self.start_time) <= 10:
        print('Not saving visit, too short.')
        return

    requests.post('%s/visits' % API_URL, data={
        'start_time': self.start_time,
        'end_time': self.end_time,
    }, headers={'Authorization': TOKEN})


print('starting Project P...')

sensor = Sensor()

reed_sensor.when_pressed = sensor.door_closed
reed_sensor.when_released = sensor.door_opened

pause()
