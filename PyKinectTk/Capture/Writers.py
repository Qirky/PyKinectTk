""" Wrapper for OpenCV2 Video Writer """

from cv2 import VideoWriter as writer
from cv2 import VideoWriter_fourcc, destroyAllWindows
from numpy import array, concatenate
from threading import Thread
from multiprocessing import Process, Queue, Lock
import wave


class VideoWriter:
    """ Holds a queue of frames to write to disk. """

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

class ThreadedVideoWriter(VideoWriter, Thread):
    pass
                

class DepthWriter:

    def __init__(self, path):

        self.path = path
        self.file = open(path, 'w')
        self.file.close()

    def write(self):
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

    def write(self, **kwargs):

        # Parameters
        nchannels = kwargs.get('nchannels', 1)
        sampwidth = kwargs.get('sampwidth', 4)
        framerate = kwargs.get('framerate', 32000.0)

        self.data.tostring()
        
        if self.data is not None:
            f = wave.open(self.path, "wb")
            f.setparams((nchannels, sampwidth, framerate, self.data.size, "NONE", "NONE"))
            f.writeframes(self.data.tostring())
            f.close()

    def release(self):
        return
