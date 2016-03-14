"""
    This module sets up the intial work environment and database
"""

from __sql__ import *
from .. import Skeleton

from os.path import realpath, abspath, join
from os.path import isdir, isfile, dirname

from Tkinter import Tk
from tkFileDialog import askdirectory

def local(filename):
    """ Returns the realpath for a file in THIS directory """
    return abspath(join(dirname(__file__), filename))

def getpath(filename):
    """ File should contain just one line; the root directory """
    try:

        with open(filename) as f:
            path = f.read().strip()

        if not isdir(path):

            raise

    except:

        root = Tk()
        root.withdraw()

        path = askdirectory(parent=root) # Ask user to choose new location

        root.destroy()

        with open(filename, 'w') as f:
            f.write(path)
            
    return realpath(path)

class Root:

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path

    def __add__(self, s):
        return join(self.path, s)

    def add(self, s):
        return Root(self + s)

#: DIR Reads the known location of the work folder from the hidden file, 'config'

DIR = Root( getpath(local("config")) )

#: Work Directory Constants

DATABASE  = DIR + 'Recordings.db'

AUDIO_DIR = DIR.add( "AUDIO" )
VIDEO_DIR = DIR.add( "VIDEO" )
XEF_DIR   = DIR.add(  "XEF"  )
IMAGE_DIR = DIR.add( "IMAGE" )


SUBDIRECTORIES = [
                    AUDIO_DIR,
                    VIDEO_DIR,
                      XEF_DIR,
                    IMAGE_DIR
                  ]

# Error messages to display

PYGAME_ERROR = "ImportError: Kinect data playback requires PyGame v1.9"

# This value is used to divided

TIME_DIV = 10000000.0

def CreateEnvironment():
    """ Checks if the necessary folders exist and creates them if not """
    from os import mkdir
    
    directories = SUBDIRECTORIES
    
    for d in directories:
        path = str(d)
        if not isdir(path):
            mkdir(path)

    # Check if our database is there, if not then create environment

    if not isfile(DATABASE):
        CreateDatabase(DATABASE)

    return True

#: Automatically called to create a work environment

CreateEnvironment()
