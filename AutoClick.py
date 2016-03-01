""" Module that automates mouse clicking until Clicker.stop() is called """

from threading import Thread
from pyautogui import click, position
from time import sleep

class Clicker(Thread):

    def __init__(self, wait=1):
        Thread.__init__(self)
        self.running = True
        self.time_step = wait
        raw_input("Hover over the location you want to click and press enter")
        self.x, self.y = position()

    def run(self):
        while self.running:
            click(self.x, self.y)
            sleep(self.time_step)
            if (self.x, self.y) != position():
                self.running=False

    def stop(self):
        self.running = False
