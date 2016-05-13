"""

    QoM.py

    Used for calculating the quanitity of motion in video files

"""

from collections import deque
from ..Playback  import VideoReader
from ..utils     import Load

import cv2
import numpy as np


class MotionDetection(VideoReader):

    def __init__(self, pid, window_size=30):
        VideoReader.__init__(self, pid)

        # Queue of last 30 frames
        
        self.window = deque()
        self.length = window_size

        for n in range(self.length):

            self.window.append(self.read())

        # Get information about the frames

        self.h = self.data.get(3) 
        self.w = self.data.get(4)
        self.area = self.h * self.w

        # Flag

        self.hasData = True

    def MotionImage(self, threshold=200):
        """ Returns the image from the sum of the next window
        """

        # Initialise image

        img = np.zeros((self.w, self.h), dtype=np.uint8)

        # Get first frame of the window

        A = cv2.cvtColor(self.window[0], cv2.COLOR_BGR2GRAY)

        # Iterate over the rest of the window
        
        for i in range(1, self.length):

            # Load next frame

            B = cv2.cvtColor(self.window[i], cv2.COLOR_BGR2GRAY)

            # Image subtraction

            dif = cv2.absdiff(B, A)

            # Add to Motion Image

            img = cv2.add(img, dif)

            # Store the last grayscale frame

            A = B

        r, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)

        # Try and get the next video frame

        try:
            
            self.window.append(self.read())
            self.window.popleft()

        except:

            self.hasData = False
            
        return img

    def Proportion(self, array):
        """ Counts the number of non-black pixels in array and returns the
            value as a proportion of the screen size """
        return (np.count_nonzero(array) / self.area) * 100

def Count(array):
    return 
        
