#!/usr/bin/python

"""
    Contains the Object that connects with the Kinect Service and converts the streams into usable data

"""

# Utility modules
from ..utils import *
from ..utils.SQL import *
from ..utils.PyKinect2 import *  

#: Import a user friendly wrapper for writing video / audio
from Writers import VideoWriter, AudioWriter

# Use time from stdlib to check timeout
from time import time as now

# Use processes to write data
from multiprocessing import Process

# This is object that listens from Kinect data, live or playback, and records joint data

class KinectService():
    
    def __init__(self, timeout=1):

        # Loop until the program stop receiving kinect stream data
        self._done = False
        self._start_time = None
        self._elapsed = None
        self._receiving_data = False

        # Used if recording a set amount of time of the XEF file
        self._first_frame_time = -1
        self._last_frame_time  = -1

        # When the wait property reaches the timeout limit, we have stopped receiving data
        self._wait = None
        self._timeout = timeout

        # Kinect runtime object
        self._kinect = PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body | PyKinectV2.FrameSourceTypes_Body )

        # Store references from the body tracking ID to a simpler 0-5 ID
        self._bodies = []
        self._body_stream = DataStream()

        # This is our access to our database
        self._database = Database(DATABASE)

        # Unique performance ID (the last index + 1)
        self._p_id = self.get_performance_id()

        # This is the descriptor for storing RGB video
        self._video_fn   = 'Output_%.03d.avi' % self._p_id
        self._video_path = VIDEO_DIR + self._video_fn
        self._video = VideoWriter(self._video_path)
        self._video_stream = DataStream()

        # This the descriptor for storing audio data
        self._audio_path = AUDIO_DIR + 'Output_%.03d.wav' % self._p_id
        self._audio = AudioWriter(self._audio_path)
        self._audio_stream  = DataStream()

        # This is the descriptor for storing depth data

            # pass

        # Holds any streams being used
        
        self._streams = []

    ### Database methods

    def get_performance_id(self):
        """ Returns the highest value in the performance-name table plus 1 """
        table = self._database[PERFORMANCE_NAME_TABLE]
        if len(table) == 0:
            return 0
        else:
            p_id  = [row['performance_id'] for row in table]
            return max(p_id) + 1

    ### Time Methods

    def wait(self):
        """ Returns the value  """
        if self._elapsed is not None:
            return now() - self._elapsed

    def timed_out(self):
        """ Returns True when the value of KinecService.wait() > KinecService._timeout  """
        if self.wait() is not None:
            return self.wait() >= self._timeout
        else:
            return False

    def timeframe_exceeded(self, dur):
        """ Returns True if the difference between the last frame timestamp
            and the first frame timestamp exceeds dur """
        return (self._last_frame_time - self._first_frame_time)  >= dur if dur is not None else False

    def update_timings(self):
        """ Reset the timeout timer to 0 and updates user if first frame """
        self._elapsed = now()
        if self._receiving_data is False:
            print "Receiveing Data...",
            self._receiving_data = True

    def reduce_start_times(self):
        """ Removes any streams that were not recorded and finds
            the earliest starting stream (body, depth, colour etc)
            and reduces all streams to starting points relative to it """
        
        self._streams = [stream for stream in self._streams if not stream.isEmpty()]
        
        sub = min([x.start_time() for x in self._streams])
        
        for stream in self._streams:

            stream.subtract(sub)
            
        return

    ### Kinect methods

    def body_index(self, body_tracking_id):
        """ Stores any new id's and returns their index """
        if body_tracking_id not in self._bodies:
            self._bodies.append(body_tracking_id)
        return self._bodies.index(body_tracking_id)

    def get_body_frame(self):
        """ Gets the last body frame data if it exists """
        if self._kinect.has_new_body_frame():
            return self._kinect.get_last_body_frame()

    def get_rgb_frame(self):
        """ Returns the RGB image of the frame as 3D matrix """
        if self._kinect.has_new_color_frame():
            return self._kinect.get_last_color_frame()

    def get_audio_frame(self):
        """ Returns a numpy array of values between -1.0 and 1.0
            for the last frame (made of sub-frames) of audio received """
        if self._kinect.has_new_audio_frame():
            return self._kinect.get_last_audio_frame()

    ### Media I/O methods
            
    def add_to_audio(self, audio):
        """ Add any new frames of audio to the accumulator """
        if audio is not None:
            for subframe in audio:
                if subframe is not None:
                    self._audio.add(subframe)
        return

    ### Main Loop
        
    def listen(self, getBodies=True, getAudio=False, getVideo=False, getDepth=False, Clicking=False, duration=None):
        """ Main application loop """

        if duration is not None and duration <= 0:

            raise ValueError("duration must be a value greater than 0")

        # Store the streams being captured

        if getBodies: self._streams.append(self._body_stream)
        if getAudio:  pass
        if getVideo:  self._streams.append(self._video_stream)
        if getDepth:  pass

        # Set up automated stepping of file
        
        if Clicking:

            import AutoClick

            clicker = AutoClick.ThreadClicker(0.5)

            clicker.start()

        # Enter loop
        
        while not self._done:

            # If service timed out

            wait = self.wait()

            if (wait >= self._timeout) if wait is not None else False:

                self._done = True

                continue

            # If a specified duration (length of recording) is exceeded

            if (self._last_frame_time - self._first_frame_time) >= duration if duration is not None else False:

                self._done = True

                continue
                    

            # BODY JOINTS

            if getBodies:

                body_frame = self.get_body_frame()

                if self._body_stream.has_new_frame( body_frame ):

                    self._body_stream.append( body_frame.timestamp() )

                    # Retrieve body data from the frame
                    
                    for i in range(0, self._kinect.max_body_count):
                        
                        body = body_frame.bodies[i]
                        
                        if not body.is_tracked:
                            
                            continue

                        # Get initial body data

                        body_index = self.body_index(body.tracking_id)

                        KeyData = [('performance_id', self._p_id), ('body', body_index), ('frame', self._body_stream.last_frame_index())]

                        # Get the x, y, z location of each joint in metres

                        joints = body.joints
                        
                        joints_2D = self._kinect.body_joints_to_color_space(joints)

                        for j in range(len(Skeleton.JointTypes)):

                            JointData = KeyData

                            # Joint ID

                            JointData += [("joint_id", j)]

                            # Location in 3 dimensional space (m)
                            
                            pos = joints[j].Position

                            x, y, z = pos.x, pos.y, pos.z

                            # Location in 3 dimensional space (px)

                            pos2 = joints_2D[j]

                            pixel_x, pixel_y = pos2.x, pos2.y

                            JointData += [("x", x), ("y", y), ("z", z)]
                            JointData += [("pixel_x", pixel_x),("pixel_y", pixel_y)]

                            # Data on whether the joint is tracked properly

                            tracking_state = joints[j].TrackingState

                            JointData += [("tracking_state", tracking_state)]

                            # Add data to JointData table

                            self._database.insert(JOINT_DATA_TABLE, JointData)

                        # body - > hand_xxxx_state & hand_xxxx_confidence

                        HandData = KeyData

                        L_HandState = body.hand_left_state
                        L_HandConf  = body.hand_left_confidence

                        HandData += [("left_hand_state", L_HandState),("left_hand_confidence", L_HandConf)]

                        R_HandState = body.hand_right_state
                        R_HandConf  = body.hand_right_confidence

                        HandData += [("right_hand_state", R_HandState),("right_hand_confidence", R_HandConf)]

                        # Add to HandData table

                        self._database.insert(HAND_DATA_TABLE, HandData)

                        # Update timings

                        self.update_timings()

            # AUDIO

            if getAudio:

                audio_frame = self.get_audio_frame()                # Get frame

                if self._audio_stream.has_new_frame( audio_frame ):

                    self.add_to_audio(audio_frame.data())               # Write

                    self._audio_stream.append(audio_frame.timestamp())  # Get timestamp

                    self.update_timings()                               # Update timings

            # RGB VIDEO

            if getVideo:

                rgb_frame = self.get_rgb_frame()                    # Get frame

                if self._video_stream.has_new_frame( rgb_frame ):

                    self._video.write(rgb_frame.data())                 # Write

                    self._video_stream.append( rgb_frame.timestamp() )  # Get timestamp

                    self.update_timings()                               # Update timings

            #: Every loop, set the _last_frame_time attribute to the largest time in the streams

            if duration is not None:

                self._last_frame_time = max([stream.end_time() for stream in self._streams if not stream.isEmpty()])

                if self._first_frame_time is -1: self._first_frame_time = self._last_frame_time


        # ;;;;; Done!
        
        print "done!"
        
        if Clicking: clicker.stop()

        # Release any files etc

        if getBodies:
            self.write_bodies()

        if getAudio:
            self._audio.write()
            
        if getVideo:
            self._video.release()

        # Reduce start times so first stream starts at 0.0
        self.reduce_start_times()

        # Add the start/end times of streams to database
        self.store_media_times(getBodies, getAudio, getVideo)
        
        return
        
    def NameRecording(self, name):
        """ Enter a string name for the recording database """
        self._database.insert(PERFORMANCE_NAME_TABLE, [("performance_id", self._p_id),("name", name)])
        return

    def store_media_times(self, body, audio, video):
        """ Stores the start/end times for audio and video streams """
        if body:
            self.write_stream_timestamps(BODY_TIME_TABLE, self._body_stream)
        if audio:
            self._database.insert(AUDIO_PATH_TABLE, [("performance_id", self._p_id), ("audio_id", 0), ("path", self._audio_path), ("start_time", self._audio_stream.start_time())])
        if video:
            self._database.insert(VIDEO_PATH_TABLE, [("performance_id", self._p_id), ("video_id", 0), ("path", self._video_fn), ("start_time", self._video_stream.start_time())])
            self.write_stream_timestamps(VIDEO_TIME_TABLE, self._video_stream)
        return

    def write_bodies(self):
        """ Stores an ID number for each body that appeared in the scene - can be edited later """
        for n in self._bodies:
            self._database.insert(BODY_NAME_TABLE, [("performance_id", self._p_id), ("body", n), ("name", n)])
        return

    def write_stream_timestamps(self, table, stream):
        """ FRAME_TIME_TABLE """

        for frame, time in stream.items(): 

            timestamp = [('performance_id', self._p_id), ('frame', frame), ('time', time )]

            self._database.insert(table, timestamp)

        return

    def close(self):
        """ Closes any open files """
        self._kinect.close()
        self._database.save()
        self._database.close()
        return


class DataStream:
    """ Handles TimeStamp and Frame number data """

    def __init__(self):

        self.timestamps = []
        self.body = []

    def __len__(self):

        return len(self.timestamps)
    
    def __getitem__(self, frame):

        return self.timestamps[frame]

    def has_new_frame(self, frame_data):

        if frame_data is None:

            return False

        if len(self.timestamps) < 1:

            return True

        try:

            timestamp = frame_data.timestamp()

            return self.timestamps[-1] < timestamp / TIME_DIV

        except:

            return False            

    def append(self, timestamp):

        self.timestamps.append(timestamp / TIME_DIV)

        return self
        
    def items(self):

        for n in self.frames():

            yield n, self[n]

    def frames(self):

        return xrange(len(self))

    def last_frame_index(self):
        """ Returns the index of the last frame """

        return len(self.timestamps) - 1

    def writebody(self):
        f = open("body.txt","w")
        f.write("Video --- Body\n")
                                                
        for frame, time in self.items():

            f.write("%s, %s --- %s\n" % (str(frame), str(time), str(self.body[frame]) ) )

        f.close()
        

    def start_time(self):

        return self.timestamps[0]

    def end_time(self):

        return self.timestamps[-1]

    def isEmpty(self):
        return len(self.timestamps) == 0

    def subtract(self, time):
        """ Subtract a time value (seconds) from every timestamp """
        for i, value in self.items():
            self.timestamps[i] = value - time
        return self
        
    
