import cv2
import numpy as np
import sys

class ProgressBar:
    
    def __init__(self, length):
        self.l = length
        self.x = 0

    def barsize(self):
        a = int(self.l * self.x / 100)
        return a, self.l - a

    def update(self, val):
        self.x = val
        self.draw()

    def draw(self):
        return

class GraphicalBar(ProgressBar):
    def __init__(self, length=250, height=40):
        ProgressBar.__init__(self, length)
        self.h = height
    def draw(self):
        a, b = self.barsize()
        window = np.zeros((self.h, self.l, 3), np.uint8)
        cv2.rectangle(window, (0,0), (a,self.h), (0,255,20), -1)
        cv2.putText(window, "%.2f%%" % self.x, (self.l - 50, self.h / 2), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1, cv2.LINE_AA)
        cv2.imshow('Converting...', window)
        return        
    

class Console(ProgressBar):
    def __init__(self, fn, length=60):
        ProgressBar.__init__(self, length)         
        print "Converting to video '%s'" % fn
    def draw(self):
        a, b = self.barsize()
        out = "[%s%s] %.2f%%" % ("=" * a, " " * b, self.x)       
        sys.stdout.write("\r" + out)
        sys.stdout.flush()
        return
