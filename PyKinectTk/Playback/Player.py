"""
    This module reads data from extracted video and skeleton data
    from the Kinect and plays it back to the user using PyGame.

    The data can also be saved as an .avi file, useful for adding
    audio data -> A function to be added.

"""

# Playback modules
from Readers import *

# Utility modules
from ..utils import Load
from ..utils import *
from ..utils.SQL import *

# OpenCV to display
import numpy as np
import cv2


class KinectDataPlayer:

    def __init__(self, performance_id, **kwargs):

        #: Define what data to play back
        self._drawing = {}
        self._drawing['body']  = bool(kwargs.get('body', True))
        self._drawing['info']  = bool(kwargs.get('info', True))
        self._drawing['video'] = bool(kwargs.get('video', True))
        
        self._drawing['depth'] = bool(kwargs.get('depth', False)) # TODO
        self._drawing['audio'] = bool(kwargs.get('audio', False)) # TODO

        self._layers = self.layers_to_draw()

        #: Set the FPS

        self._fps = 30.0
        self._wait = 20

        #: Define the timeframe to draw

        self._timeframe = kwargs.get('time',(None, None))

        # Stores the methods to draw the selected streams
        self.draw = {}
        
        #: Dictionary of stream name -> the frame in that stream currently on screen
        self._frame_playing = dict([(stream, -1) for stream in self._drawing.keys() if self._drawing[stream] is True])

        #: Dictionary of stream name -> dictionary of frame numbers and timestamps
        self._frames = {}

        #######################--- SETUP STREAMS ---#######################

        # Video data

        if self._drawing['video']:

            self._video = VideoReader(performance_id)

            VideoFrameTime = Load.VideoData(performance_id)

            self._frames['video'] = Load.FrameTime(VideoFrameTime)

            # This is a method draws the video image to screen

            self.draw['video'] = self.draw_video

            self._videoSurface = None

            self._wait = 1

        # Body data

        if self._drawing['body']:

            self._bodies = Load.BodyData(performance_id)

            self._key_joints = ["HandTipLeft",
                                "HandTipRight",
                                "SpineShoulder"]

            self._key_joints = []
    
            BodyFrameTime = {}

            for body in self._bodies:

                BodyFrameTime.update(body.all_frame_time())

            self._frames['body'] = Load.FrameTime(BodyFrameTime)

            # This is a method that draws the skeleton data to screen

            self.draw['body'] = self.draw_bodies

        # Audio data - TODO

        if self._drawing['audio']:

            pass

        # Depth data - TODO

        if self._drawing['depth']:

            pass

        # Frame and time data

        if self._drawing['info']:

            self._frames['info'] = Load.FrameTime({0:-1.0})
            self.draw['info'] = self.draw_info


        #######################--- SETUP DISPLAY ---#######################

        self._resolution = 1920, 1080

        self._size = self._width, self._height = 960, 540

        self._surface = None

        self._head_size = sum(self._size) / 200

        self._largest_clip = max(self._frames.values(), key=lambda x: x.max_time() ).max_time()

        self._clip_start  = 0 if self._timeframe[0] is None else int(self._timeframe[0] * self._fps)

        self._clip_length = int((self._largest_clip if self._timeframe[1] is None else self._timeframe[1]) * self._fps)

    #: General utility methods

    def update(self):
        """ Writes new frame to screen/file """
        cv2.imshow('PyKinectTk Playback', self._surface)
        return

    def layers_to_draw(self):
        """ Returns a list of streams being drawn, in order of background to foreground """
        layers = [ 'video','body','depth','audio','info' ]
        for stream, beingDrawn in self._drawing.items():
            if not beingDrawn:
                del layers[layers.index(stream)]
        return layers

    def draw_new_frame(self):
        """ Clears the next frame to display """
        self._surface = np.zeros((self._height, self._width, 3), np.uint8)
        return

    def ratio(self):
        """ Returns the the % of change in size of frame """
        return float(self._size[0]) / self._resolution[0]

    def convert(self, *xy ):
        """ Converts an x,y value in original resolution to current frame size """
        return tuple([int(xy[i] * (float(self._size[i])/self._resolution[i])) for i in range(2)])

    def frame_time(self, t, stream):
        """ Returns the frame number for data stream that occurs at time t """
        if stream is not "info":
            return self._frames[stream].frame_at_time(t)
        else:
            return t

    def entry_time(self, stream):
        """ Returns the timestamp of the first occurence of data of the given stream """
        return min(self._frames[stream].timestamps())

    #: Drawing skeleton methods

    def draw_bodies(self, n):
        """ Draws the body data at frame n """

        for i, body in enumerate(self._bodies):

            if body.hasData(n):

                # Draw the body

                self.draw_skeleton(body, n, COLOUR[i])

                # Label the body with appropriate value 0-5

                self.draw_label(str(body), body['Head'].pixel(n), COLOUR[i], offset=[25]*2, size=2)

                # Draw X, Y, Z data for certain joints

                for joint in self._key_joints:

                    values = ["%.2f" % f for f in body[joint][n]]

                    self.draw_label(values, 14, body[joint].pixel(n), COLOUR[i], offset=(25,25))
        return

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
                            
                        
    def draw_bone(self, xy1, xy2, colour, width=2):
        try:
            start = self.convert(*xy1)
            end   = self.convert(*xy2)
            cv2.line(self._surface, start, end, colour, width)
        except:
            return

    def draw_head(self, xy, colour):
        try:
            pos = self.convert(*xy)
            cv2.circle(self._surface, pos, self._head_size, colour, -1)
        except:
            return

    #: Drawing video methods

    def draw_video(self, n):
        """ Reads the next frame of video """

        if n > self._frame_playing['video']:

            self._video.set_frame(n)

            self._videoSurface = self._video.read()

            self._videoSurface = cv2.resize(self._videoSurface, (self._width, self._height))

            self._frame_playing['video'] = n

        # Draw onto self._screen
        
        self._surface = np.copy(self._videoSurface)

        return

    #: Drawing information labels

    def draw_label(self, text, xy, colour, offset=(0,0), size=1):
        try:
            pos = tuple([val - offset[i] for i, val in enumerate(self.convert(*xy))])
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(self._surface, str(text), pos, font, size, colour, 1, cv2.LINE_AA)
        except:
            return

    def draw_info(self, t):
        """ Draws frame time and num """
        y, offset = 25, 25
        for stream, drawing in self._drawing.items():
            if drawing and stream is not 'info':
                try:
                    frame_number = self.frame_time(t, stream)
                    real_time = self._frames[stream][frame_number]
                    self.draw_label("%s Frame %06d: %.4f" % (stream, frame_number, real_time), (0,y), WHITE)
                    y += offset
                except:
                    pass
        return
    
    def quitting(self):
        return cv2.waitKey(self._wait) & 0xFF == ord('q')

    def run(self, verbose=False):
        
        """ Plays the performance using real time 'rendering' in Open CV.

            The program loops at 30fps and then uses the timestamp for each stream
            to decide whether or not to render the next frame
        """
        
        for frame in xrange(self._clip_start, self._clip_length):

            self._current_frame = frame

            t = frame / self._fps

            # Check for exits

            if self.quitting() or t >= self._largest_clip:

                break

            # Start by clearing the frame

            self.draw_new_frame()

            # Iterate over in order of layers and draw streams

            for stream in self._layers:

                if t >= self.entry_time(stream):

                    try:

                        self.draw[stream](self.frame_time(t, stream))

                    except TimeIndexError as e:

                        if verbose:

                            print "Error in %s stream: %s" % (stream, e)

            # Update the screen
                
            self.update()

        # Exit cleanly
        
        self.close()

    def close(self):
        """ Closes and open modules / files etc """
        if self._drawing['video']:
            self._video.close()
        cv2.destroyAllWindows()
