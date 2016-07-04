#! /usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as gpio
import time
import requests

PIN = 14
API_URL = 'http://api.project-p.xyz'
TOKEN = 'YOUR TOKEN'
WAIT_TIME = 2

class Sensor(object):
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.status = False

    def toggle(self, _):
        self._toggle_status()

        if not self.status:
            time.sleep(WAIT_TIME)
            if gpio.input(PIN) == 0:
                print 'toggle on'
                self.start_time = int(time.time())-WAIT_TIME
        else:
            time.sleep(WAIT_TIME)
            if gpio.input(PIN) == 1:
                print 'toggle off'
                self.end_time = int(time.time())+WAIT_TIME
                self._send_visit()

        # Remove event listener for a second to prevent it from instantly
        # toggeling back
        gpio.remove_event_detect(PIN)
        time.sleep(1)
        gpio.add_event_detect(PIN, gpio.BOTH, callback=self.toggle)

    def _send_visit(self):
        # Don't log entries shorter than 10 seconds
        if (self.end_time - self.start_time) <= 10:
            return

        requests.post('%s/visits' % API_URL, data={
            'start_time': self.start_time,
            'end_time': self.end_time,
        }, headers={'Authorization': TOKEN})

    def _toggle_status(self):
        self.status = not self.status
        requests.put('%s/locations/toggle' % API_URL, headers={
            'Authorization': TOKEN
        })

if __name__ == '__main__':
    gpio.setmode(gpio.BCM)
    gpio.setup(PIN, gpio.IN, pull_up_down=gpio.PUD_UP)

    sensor = Sensor()
    gpio.add_event_detect(PIN, gpio.BOTH, callback=sensor.toggle)

    while True:
        time.sleep(1)
