import Skeleton
import SQL

import pygame, sys
import numpy as np
import cv2

from os.path import realpath

import Tkinter as tk
from tkFileDialog import askopenfilename
from tkMessageBox import showwarning as WarnMsg
from tkMessageBox import showinfo as InfoMsg


# TODO Sort out inferred tracking etc

# defaults

COLOUR = [(255,0,0),(255,255,0),
          (0,0,255),(255,0,255),
          (0,255,0),(0,255,255)]

BLACK  = (0,0,0)

WHITE = (255,255,255)

def img(surface):
    """ img(pygame.Surface) -> numpy.array """
    array = pygame.surfarray.array3d(surface)
    array = cv2.transpose(array)
    array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    return array

def surface(img, resize=1):
    """ surface(numpy.array) -> pygame.Surface """
    surf = cv2.resize(img, (0,0), fx=resize, fy=resize)
    surf = cv2.cvtColor(surf, cv2.COLOR_BGR2RGB)
    surf = pygame.surfarray.make_surface(surf)
    surf = pygame.transform.rotate(surf, -90)
    surf = pygame.transform.flip(surf, True, False)
    return surf

class KinectDataSelect:
    """ Tkinter UI for selecting a processed Kinect file for playing back """

    def __init__(self):

        # init

        self._root = tk.Tk()

        # Load initial data from database

        self._db = SQL.Database("../Performances.db")
        
        tbl_PerformanceName = self._db["tbl_PerformanceName"]
        tbl_AudioPath       = self._db["tbl_AudioPath"]

        # Create widget to display selector
        self._listbox = tk.Listbox(self._root)
        self._listbox.pack()
        self._performances = []
        for i, name in tbl_PerformanceName:
            self._listbox.insert(tk.END, name)
            self._performances.append(i)

        # Add Audio Button
        self._addAudio = tk.Button(self._root, text="Add Audio Files", command=self.add_audio)
        self._addAudio.pack()

        # Playback Button
        self._playback = tk.Button(self._root, text="Play", command=self.start_playback)
        self._playback.pack()

        # Save to video Button
        self._toVideo = tk.Button(self._root, text="Save as Video", command=self.to_video)
        self._toVideo.pack()

        # Location of videos
        self._video_fp_root = "../VIDEO/%s.avi"

        # Run
        self._root.mainloop()

    def selected(self):
        """ Returns the index of the selected item """
        return self._listbox.curselection()[0]

    def performance_name(self):
        """ Returns the name of the selected item """
        return self._listbox.get(self.selected())

    def video_filename(self):
        """ Returns the video file path of the recording """
        return realpath(self._video_fp_root % self.performance_name())

    def performance_id(self):
        """ Returns the performance ID of the selected item """
        return self._performances[self.selected()]

    def associated_audio(self, pid):
        paths = {}
        for row in self._db["tbl_AudioPath"]:
            if row['performance_id'] == pid:
                paths[row['audio_id']] = row['path']
        return paths

    def audio_paths(self, pid):
        """ Returns a list of audio file paths for a performance """
        return self.associated_audio(pid).values()

    def audio_id(self, pid):
        """ Returns a list of all the audio IDs for associated audio """
        return self.associated_audio(pid).keys()

    def start_playback(self):
        """ Loads the performance data and plays back with pygame """

        try:

            # Get the performance id

            pid = self.performance_id()

            # Begin pygame playback

            player = KinectDataPlayer(pid)
            self._root.withdraw()
            player.run()

            # re-show root

            self._root.deiconify()

        except:

            pass

        return

    def to_video(self):
        """ Creates a player object that outputs to file not screen """

        try:

            # Get the performance id

            pid = self.performance_id()

            # Begin pygame to video

            player = KinectDataPlayer(pid, output=self.video_filename())
            player.run()

            InfoMsg("File Saved", "%s has been saved successfully" % self.video_filename())

        except:

            pass

        return

    def openfilepath(self):
        """ Returns the realpath of a file from tkinter open file dialog """
        f = askopenfilename()
        return realpath(f)

    def add_audio(self):
        """ Opens file dialog for adding audio waveforms to a performance """

        if 1==1: #try:        
        
            # Get pid

            p_id = self.performance_id()

            # Get the file to add
            
            fn = self.openfilepath()
            
            # If the file is already added to it, show a message

            if fn in self.audio_paths(p_id):

                WarnMsg("Warning", "Wav file '%s' is already attached to this performance." % fn)

            else:

                # Get the newest audio_id

                a_id = max(self.audio_id(p_id)) + 1

                # Update database

                self._db.insert("tbl_AudioPath", [("performance_id", p_id), ("audio_id", a_id), ("path", fn)])

                self._db.save()
                
                InfoMsg("Audio Added", "Wav file '%s' has been added to the selected performance" % fn )
                
        else:#except:

            pass

        return       

class KinectDataPlayer:

    def __init__(self, performance_id, **kwargs):

        # Set up video writer

        self._toFile = kwargs.get("output", None)

        self._video = cv2.VideoCapture("../VIDEO/Output_000.avi")

        # Kinect data

        self._bodies = Skeleton.LoadPerformance(performance_id)

        self._key_joints = "HandTipLeft", "HandTipRight", "SpineShoulder"

        frame = []
        time  = []

        self._time = {}

        for body in self._bodies:

            frame += body.frames()
            time  += body.time()
            self._time.update(body.all_frame_time())

        self._clip_start, self._clip_end = min(frame), max(frame)
        self._start_time, self._end_time = min(time), max(time)

        # PyGame Setup

        pygame.init()

        self._resolution = 1920, 1080

        # If we are saving the video, display a %

        if self._toFile:

            self._size = self._width, self._height = self._resolution

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            
            self._writer = cv2.VideoWriter(self._toFile, fourcc, 30.0, self._size)

            self._screen = pygame.display.set_mode((120,75))
            
            self._percent = pygame.Surface((120,75))

        else:

            self._size = self._width, self._height = 960, 540
        
            self._screen = pygame.display.set_mode(self._size)
        
        self._clock = pygame.time.Clock()

        self._surface = pygame.Surface(self._size)

        self._head_size = sum(self._size) / 60

    def update(self):
        """ Writes new frame to screen/file """
        if self._toFile:
            self._writer.write( img(self._surface) )
            self._screen.blit( self._percent, (0,0))
            pygame.display.flip()
        else:
            self._screen.blit(self._surface, (0,0))
            pygame.display.flip()
            self._clock.tick(30)
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

    def draw_percent_complete(self, val):
        try:
            self._percent.fill(BLACK)
            font = pygame.font.SysFont("Courier New", 32)
            label = font.render("%.2f%%" % val, 1 , WHITE)
            self._percent.blit(label, (5,5))
        except:
            return

    def run(self):
        
        """ Plays the performance using real time rendering in PyGame """

        quitting = False
        t = self._time
        
        for frame in xrange(self._clip_end):

            # Handle quit or resize events
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quitting = True

            # Break out of loops
            if quitting:
                break

            # Load video frame

            try:

                ret, videoFrame = self._video.read()
                self._surface = surface(videoFrame, self.ratio())

            except:

                self._surface.fill(BLACK)

            # Load the video frame

            if self._toFile:
                x = (float(frame) / self._clip_end) * 100
                self.draw_percent_complete( x )

            # Frame and Time

            try:
                time = t[frame]
            except:
                time = "0.0"

            self.draw_label("Frame %06d: %s" % (frame, time), 24, (0,0), WHITE)

            # Draw bodies

            for i, body in enumerate(self._bodies):

                # Draw the limbs of each body for the current frame

                if body.hasData(frame):

                    # Draw the body

                    self.draw_skeleton(body, frame, COLOUR[i])

                    # Label the body with appropriate value 0-5

                    self.draw_label(i, 36, body['Head'].pixel(frame), COLOUR[i], offset=[self._head_size*2]*2)

                    # Draw X, Y, Z data for certain joints

                    for joint in self._key_joints:

                        values = ["%.2f" % f for f in body[joint][frame]]

                        self.draw_label(values, 14, body[joint].pixel(frame), COLOUR[i], offset=(25,25))
                        
            # Update the screen
            self.update()

        # Exit pygame
        self._video.release()
        pygame.quit()
        
        #cv2.destroyAllWindows()
        # Exit OpenCV
        if self._toFile:
            self._writer.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":

    app = KinectDataSelect()
