"""
    The Python Kinect Toolkit
    =========================

    On import, this package checks to see if a working directory has been
    defined, and asks you to select a folder if not.

    The path of the working directory is found in the /PyKinectTk/utils/Settings/config text file

"""

import utils

from Tkinter import Tk
from tkFileDialog import askdirectory, asksaveasfilename
from os.path import isdir, realpath

def select_folder():
    root = Tk()
    root.withdraw()
    path = realpath(askdirectory(parent=root))  
    root.destroy()
    return path

def save_file():
    root = Tk()
    root.withdraw()
    path = realpath(asksaveasfilename(parent=root))  
    root.destroy()
    return path

filename = utils.config

try:
    
    # Read the location of the work environment
    with open(filename) as f:
        path = f.read().strip()

    if not path:

        raise
    
    if not isdir(path):

        raise
except:

    # If one is not set, or doesn't exist anymore, ask the user to choose
    
    with open(filename, 'w') as f:

        f.write(select_folder())

# Create the selected work environment
    
reload(utils)
from utils import *
utils.CreateEnvironment()

import Capture
import Playback
import Analysis
