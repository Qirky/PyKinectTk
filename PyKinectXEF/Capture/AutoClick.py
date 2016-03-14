""" Module that automates mouse clicking until Clicker.stop() is called """

from threading import Thread
from pyautogui import click, position
from time import sleep

class Clicker:

    def __init__(self, pos=None):
        if pos is not None:
            self.x, self.y = pos
        else:
            self.x, self.y = self.fromPosition()

    def click(self):
        click(self.x, self.y)

    @staticmethod
    def fromPosition():
        raw_input("Hover over the location you want to click and press enter")
        return position()
        
        

class ThreadClicker(Thread, Clicker):

    def __init__(self, wait=1):
        Thread.__init__(self)
        Clicker.__init__(self)
        
        self.running = True
        self.time_step = wait

    def run(self):
        while self.running:
            self.click()
            sleep(self.time_step)
            if (self.x, self.y) != position():
                self.running=False

    def stop(self):
        self.running = False
