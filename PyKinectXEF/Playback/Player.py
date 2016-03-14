"""
    This module reads data from extracted video and skeleton data
    from the Kinect and plays it back to the user using PyGame.

    The data can also be saved as an .avi file, useful for adding
    audio data -> A function to be added.

"""

# Playback modules
from Display import *
from Readers import *

# Reads body frame data from database
import Load

# Utility modules
from ..utils import *
from ..utils.SQL import *

import pygame

class KinectDataPlayer:

    def __init__(self, performance_id, **kwargs):

        # Define what data to play back
        
        self._drawing = {}
        self._drawing['body']  = kwargs.get('body', True)
        self._drawing['info']  = kwargs.get('info', True)
        self._drawing['video'] = kwargs.get('video', False)
        self._drawing['depth'] = kwargs.get('depth', False) # TODO
        self._drawing['audio'] = kwargs.get('audio', False) # TODO

        self._frame_playing = {}
        for key, sel in self._drawing.items():
            if self:
                self._frame_playing[key] = -1

        # Video data

        self._video = VideoReader(performance_id)

        self._video_frames = Load.VideoData(performance_id)

        # Kinect data

        self._bodies = Load.BodyData(performance_id)

        self._key_joints = "HandTipLeft", "HandTipRight", "SpineShoulder"

        frame = []
        time  = []

        self._time = {}

        for body in self._bodies:

            frame += body.frames()
            time  += body.time()
            self._time.update(body.all_frame_time())

        print self._time

        self._clip_start, self._clip_end = min(frame), max(frame)
        self._start_time, self._end_time = min(time), max(time)

        self._current_frame = 0

        # PyGame Setup

        pygame.init()

        self._resolution = 1920, 1080

        self._fps = 30.0

        self._size = self._width, self._height = 960, 540
            
        self._screen = pygame.display.set_mode(self._size)
        
        self._clock = pygame.time.Clock()

        self._surface = pygame.Surface(self._size)

        self._head_size = sum(self._size) / 60

    def update(self):
        """ Writes new frame to screen/file """
        self._screen.blit(self._surface, (0,0))
        self._clock.tick(self._fps)
        pygame.display.flip()
        return

    def ratio(self):
        """ Returns the the % of change in size of frame """
        return float(self._size[0]) / self._resolution[0]

    def convert(self, *xy ):
        """ Converts an x,y value in original resolution to current frame size """
        return [xy[i] * (float(self._size[i])/self._resolution[i]) for i in range(2)]

    def draw_skeleton(self, skeleton, time, colour):

        for joint in skeleton:

            if joint == "Head":

                # Draw a circle

                self.draw_head(joint.pixel(time), colour)

            else:

                # Draw any bones from the joint

                lines = joint.bones(time)

                for start, end in lines:

                    self.draw_bone(start, end, colour)
                            
                        
    def draw_bone(self, xy1, xy2, colour, width=3):
        try:
            start = self.convert(*xy1)
            end   = self.convert(*xy2)
            pygame.draw.aaline(self._surface, colour, start, end, width)
        except:
            return

    def draw_head(self, xy, colour):
        try:
            pos = [int(a) for a in self.convert(*xy)]
            pygame.draw.circle(self._surface, colour, pos, self._head_size)
        except:
            return

    def draw_label(self, text, size, xy, colour, offset=(0,0)):
        try:
            font = pygame.font.Font(None, size)
            label = font.render(str(text),1,colour)
            pos = [val - offset[i] for i, val in enumerate(self.convert(*xy))]
            self._surface.blit(label, pos)
        except:       
            return

    def draw_bodies(self, n):
        """ Draws the body data at frame n """

        for i, body in enumerate(self._bodies):

            if body.hasData(n):

                # Draw the body

                self.draw_skeleton(body, n, COLOUR[i])

                # Label the body with appropriate value 0-5

                self.draw_label(i, 36, body['Head'].pixel(n), COLOUR[i], offset=[self._head_size*2]*2)

                # Draw X, Y, Z data for certain joints

                for joint in self._key_joints:

                    values = ["%.2f" % f for f in body[joint][n]]

                    self.draw_label(values, 14, body[joint].pixel(n), COLOUR[i], offset=(25,25))
        return

    def draw_video_old(self, n):
        """ Draws the RGB image at frame n """
        try:

            videoFrame = self._video.nextFrame()
                
            self._surface = surface(videoFrame, self.ratio())

        except:

            pass

    def draw_video(self, t):
        """ Reads the next frame if it falls  """
        cur = self._frame_playing['video']
        
        if t <= self._video_frames[cur+1]:

            videoFrame = self._video.nextFrame()
                
            self._surface = surface(videoFrame, self.ratio())

            self._frame_playing['video'] += 1

        else:

            pass

    def draw_new_frame(self):
        """ Clears the next frame to display """
        self._surface.fill(BLACK)
        return

    def draw_info(self, n):
        """ Draws frame no. and time """
        try:

            time = self._time[n]
            
        except:

            time = n / self._fps #: Estimate time for frames we don't have timestamps for

        self.draw_label("Body Frame %06d: %.4f" % (n, time), 24, (0,0), WHITE)
        self.draw_label("VideoFrame %06d: %.4f" % (n, self._video_frames[n]), 24, (0,25), WHITE)
        

        return

    @staticmethod
    def quitting():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def release(self):
        """ Placeholder """
        return

    def run(self):
        
        """ Plays the performance using real time 'rendering' in PyGame """

        for frame in xrange(self._clip_end):

            # Check for exits
            if self.quitting():
                break

            self._current_frame = frame
            self._current_time  = t = self._time[frame]

            #: Layer 0: New frame

            self.draw_new_frame()

            #: Layer 1: Draw RGB Video Data

            if self._drawing['video']:

                self.draw_video(t)

            #: Layer 2: Draw depth data

            if self._drawing['depth']:

                pass # TODO                          

            #: Layer 3: Draw body data

            if self._drawing['body']:

                self.draw_bodies(frame)

            #: Layer 4: Draw any informative labels

            if self._drawing['info']:
    
                self.draw_info(frame)

            # Update the screen
                
            self.update()

        # Exit cleanly
        
        self.close()

    def close(self):
        """ Closes and open modules / files etc """
        self._video.close()
        pygame.quit()
        self.release()
