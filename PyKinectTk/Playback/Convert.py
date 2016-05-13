"""
    Uses Capture.Writers.VideoWriter to write extracted data streams into one .avi file

"""

# Utility modules
import sys
from ..utils import *
from ..utils.SQL import *

import Player
import ProgressBar
from ..Capture import Writers

class ConvertKinect(Writers.VideoWriter, Player.KinectDataPlayer):

    def __init__(self, performance_id, outputFile=None, **kwargs):

        # Inheritance

        Player.KinectDataPlayer.__init__(self, performance_id, **kwargs)
        
        Writers.VideoWriter.__init__(self, VIDEO_DIR + outputFile, self._fps)

        # Set up size

        self._size = self._width, self._height = self._resolution

        # Progress bar

        self._progress = kwargs.get("progressbar", None)

        if self._progress is None:

            self._progress = ProgressBar.Console(outputFile)


    def update(self):
        """ Over-rides KinectDataPlayer to write the output to the VideoWriter """
        
        self.write(self._surface)

        x = (float(self._current_frame - self._clip_start) / self._clip_length) * 100

        self._progress.update(x)        
        
        return
        
