import utils

from Tkinter import Tk
from tkFileDialog import askdirectory
from os.path import isdir, realpath

def init():
    """ Should be called at the start of an application """
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
        root = Tk()
        root.withdraw()
        path = realpath(askdirectory(parent=root))  
        root.destroy()
        with open(filename, 'w') as f:
            f.write(path)

    # Create the selected work environment
        
    reload(utils)
    utils.CreateEnvironment()

    import Capture
    import Playback
