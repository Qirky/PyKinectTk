""" Wrapper for OpenCV2 Video Writer """

from cv2 import VideoWriter as writer
from cv2 import VideoWriter_fourcc, destroyAllWindows

from numpy import array, concatenate

# Use wave module to write audio
import wave

class VideoWriter:

    def __init__(self, path, fps=30.0):

        fourcc    = VideoWriter_fourcc(*"XVID")
        self.path = path
        self.data = writer(self.path, fourcc, fps, (1920,1080))

    def __str__(self):
        return self.path

    def write(self, data):
        self.data.write(data)
        return

    def release(self):
        self.data.release()
        destroyAllWindows()
        return


class AudioWriter:

    def __init__(self, path):

        self.data = array([])
        self.path = path
        self.start = None
        self.offset = None
        self.time = []
        self.subframes = 0

    def add(self, array):
        """ Add data """
        self.data = concatenate((self.data, array))

    def write(self):
        if self.data is not None:
            f = wave.open(self.path, "wb")
            f.setparams((1, 4, 32000.0, self.data.size, "NONE", "NONE"))
            f.writeframes(self.data.tostring())
            f.close()
