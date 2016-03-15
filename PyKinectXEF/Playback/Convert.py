"""
    Uses Capture.Writers.VideoWriter to write extracted data streams into one .avi file

"""

# Utility modules
from ..utils import *
from ..utils.SQL import *
from ..Capture import Writers

from Player  import *
from Display import *

from pygame import display, font

class ConvertKinect(Writers.VideoWriter, KinectDataPlayer):

    def __init__(self, performance_id, outputFile, **kwargs):

        # Inheritance
        KinectDataPlayer.__init__(self, performance_id, **kwargs)
        Writers.VideoWriter.__init__(self, outputFile, self._fps)

        # Set to "full screen"
        self._size = self._width, self._height = self._resolution
        # Create a small graphic to display progress
        self._screen = pygame.display.set_mode((120,75))
        self._progress = pygame.Surface((120,75))


    def update(self):
        """ Over-rides KinectDataPlayer to write the output to the VideoWriter """
        
        self.write( img(self._surface) )

        self._progress.fill(BLACK)

        try:
            
            self.draw_percent_complete()
            
        except:
            
            pass
        
        self._screen.blit( self._progress, (0,0))
        
        display.flip()
        
        return

    def draw_percent_complete(self):
        """ Draws the portion of video that has been saved as a percent """

        x = (float(self._current_frame) / self._clip_length) * 100

        text  = font.SysFont("Courier New", 32)

        label = text.render("%.2f%%" % x , 1 , WHITE)

        self._progress.blit(label, (5,5))

        return

        
    

        
        
        
        
