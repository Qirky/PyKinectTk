    
# Python modules for reading kinect data: https://github.com/Kinect/PyKinect2
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

# Our own Kinect data objects module
import Skeleton
import SQL

# Use time from stdlib to check timeout
from time import time as now

# Use numpy and OpenCV to write RGB to video
import numpy as np
import cv2

# Use scipy to write out audio
import wave

# Use real path to name files
from os.path import realpath

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*"XVID")


# Database Constants

DATABASE = '../Performances.db'

JOINT_NAMES_TABLE  = "tbl_JointNames"
HAND_STATES_TABLE  = "tbl_HandStates"
TRACK_STATES_TABLE = "tbl_TrackStates"

PERFORMANCE_NAME_TABLE  = "tbl_PerformanceName"
VIDEO_PATH_TABLE        = "tbl_VideoPath"
AUDIO_PATH_TABLE        = "tbl_AudioPath"
AUDIO_TIME_TABLE        = "tbl_AudioTime"
FRAME_TIME_TABLE        = "tbl_FrameTime"
JOINT_DATA_TABLE        = "tbl_JointData"
HAND_DATA_TABLE         = "tbl_HandData"



# This is object that listens from Kinect data, live or playback, and records joint data

class BodyDataExtract(object):
    
    def __init__(self, db=":memory:", timeout=1):

        # Loop until the program stop receiving kinect stream data
        self._done = False
        self._start_time = None
        self._elapsed = None
        self._frame_count = 0
        self._receiving_data = False

        # When the wait property reaches the timeout limit, we have stopped receiving data
        self._wait = None
        self._timeout = timeout

        # Kinect runtime object
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Body)

        # This stores data about the last retrieved body data
        self._body_frame = None

        # Store references from the body tracking ID to a simpler 0-5 ID
        self._bodies = []

        # This is our access to our database
        self._database = SQL.Database(db)

        # Store data to be inserted into tables
        self._tbl_frame_time = []
        self._tbl_joint_data = []
        self._tbl_hand_data = []

        # Unique performance ID
        self._p_id = self.get_performance_id()

        # This is the descriptor for storing RGB video
        self._video_path = realpath('..\VIDEO\Output_%.03d.avi' % self._p_id)
        self._video = cv2.VideoWriter(self._video_path, fourcc, 30.0, (1920,1080))
        self._video_frames = []

        # This the descriptor for storing audio data
        self._audio_path = realpath('..\AUDIO\Output_%.03d.wav' % self._p_id)
        self._audio_start = None
        self._audio = np.array([])
        self._subframes = 0


        #debug
        self._debug = 0

    def get_performance_id(self):
        """ Returns the highest value in the performance-name table plus 1 """
        table = self._database[PERFORMANCE_NAME_TABLE]
        if len(table) == 0:
            return 0
        else:
            p_id  = [row['performance_id'] for row in table]
            return max(p_id) + 1

        
    def elapsed_time(self):
        """ Returns the time between the current frame and start frame in seconds """
        return (self._body_frame.timestamp - self._start_time) / 10000000.00

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
            frame = np.array(self._kinect.get_last_color_frame(), dtype="uint8")
            return frame.reshape([1080,1920,4])

    def get_audio_frame(self):
        """ Returns a numpy array of values between -1.0 and 1.0
            for the last frame (made of sub-frames) of audio received """
        if self._kinect.has_new_audio_frame():
            frame = self._kinect.get_last_audio_frame()
            return frame

    def add_to_audio(self, audio):
        """ Add any new frames of audio to the accumulator """
        if audio is not None:
            for subframe in audio:
                if subframe is not None:
                    self._audio = np.concatenate((self._audio, subframe))
                    self._subframes += 1
        return

    def write_audio(self):
        """ Writes the collected audio data to file """
        if self._audio is not None:
            f = wave.open(self._audio_path, "wb")
            f.setparams((1, 4, 32000.0, self._audio.size, "NONE", "NONE"))
            f.writeframes(self._audio.tostring())
            f.close()

        return 


    def listen(self, getAudio=True, getVideo=False):
        # -------- Main Program Loop -----------
        while not self._done:

            # BODY JOINTS
            
            self._body_frame = self.get_body_frame()

            # If we have at least a body, start getting data
            
            if self._body_frame is not None:

                # Set the start time to the timestamp of the first frame received 

                if self._start_time is None:

                    print "Receiving Data...",

                    self._receiving_data = True

                    self._start_time = self._body_frame.timestamp

                # Work out the amount of time between frames

                elapsed = self.elapsed_time()

                # Continue looping until we get a new frame or we timeout

                if elapsed == self._elapsed:

                    if now() - self._wait >= self._timeout:

                        self._done = True
                        
                    continue

                else:

                    self._wait = now()

                    self._elapsed = elapsed

                # --- When we have a new frame, increase the counter for number of frames
                
                self._frame_count += 1
                
                # Store the frame number and time relative to the start

                FrameTime = [('performance_id', self._p_id), ('frame', self._frame_count), ('time', self._elapsed)]

                self._database.insert(FRAME_TIME_TABLE, FrameTime)

                # Retrieve body data from the frame
                
                for i in range(0, self._kinect.max_body_count):
                    
                    body = self._body_frame.bodies[i]
                    
                    if not body.is_tracked:
                        
                        continue

                    # Get initial body data

                    body_index = self.body_index(body.tracking_id)

                    KeyData = [('performance_id', self._p_id), ('body', body_index), ('frame', self._frame_count)]

                    # body -> joints & joint_orientations

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

            # AUDIO

            #if self._receiving_data and self._kinect.has_new_audio_frame():
            if getAudio and self._kinect.has_new_audio_frame():

                if self._audio_start is None:

                    self._audio_start = self._elapsed

                audio_frame = self.get_audio_frame()

                self.add_to_audio(audio_frame)


            # RGB VIDEO

            if getVideo:

                pass

        # Done!
        self.close()
        self.write_audio()

        return
        
    def name_recording(self):
        """ Enter a string name for the performance through CLI """
        val = "'%s'" % raw_input("\nEnter a name for your recording: ")
        self._database.insert(PERFORMANCE_NAME_TABLE, [("performance_id", self._p_id),("name", val)])
        self._database.insert(AUDIO_PATH_TABLE, [("performance_id", self._p_id), ("audio_id", 0), ("path", self._audio_path)])
        self._database.insert(AUDIO_TIME_TABLE, [("performance_id", self._p_id), ("audio_id", 0), ("start_pos", self._audio_start), ("end_pos", self._elapsed)])
        return

    def close(self):
        """ Closes any open files and asks for a save name dialog """
        # Close our Kinect and VideoWriter connection
        self._kinect.close()

        # Update the database with a str name
        self.name_recording()

        # Commit the changes to the database
        self._database.save()
        self._database.close()

        return

def FileExists(filename):
    """ Returns true if the filename points to a valid file """
    try:
        f=open(filename)
        f.close()
        return True
    except:
        return False

def CreateDatabase(filename):
    """ Creates the database and adds tables used by all performance data tables """
    db = SQL.Database(filename)

    # JointNames

    db.create_table(JOINT_NAMES_TABLE, [("joint_id","integer"),("joint_name","text")])

    for joint in Skeleton.JointTypes:

        db.insert(JOINT_NAMES_TABLE, [("joint_id", joint._id), ("joint_name", str(joint))])

    # HandStates

    db.create_table(HAND_STATES_TABLE, [("hand_state", "integer"),("state_name","text")])

    for state in Skeleton.HandStates:

        db.insert(HAND_STATES_TABLE, [("hand_state", state._id), ("state_name", str(state))])

    # TrackStates

    db.create_table(TRACK_STATES_TABLE, [("tracking_state","integer"),("state_name","text")])

    for state in Skeleton.TrackStates:

        db.insert(TRACK_STATES_TABLE, [("tracking_state", state._id), ("state_name", str(state))])

    # Empty tables for storing recorded performance data

    db.create_table(PERFORMANCE_NAME_TABLE, [("performance_id","integer"), ("name","text")])

    db.create_table(JOINT_DATA_TABLE, [("performance_id","integer"),
                                       ("body","integer"),
                                       ("frame","integer"),
                                       ("joint_id","integer"),
                                       ("x", "real"),
                                       ("y", "real"),
                                       ("z", "real"),
                                       ("pixel_x","integer"),
                                       ("pixel_y","integer"),
                                       ("tracking_state","integer")])
    
    db.create_table(FRAME_TIME_TABLE, [("performance_id","integer"),
                                       ("frame","integer"),
                                       ("time","real")])
    
    db.create_table(HAND_DATA_TABLE, [("performance_id","integer"),
                                      ("body","integer"),
                                      ("frame","integer"),
                                      ("left_hand_state","integer"),
                                      ("left_hand_confidence","real"),
                                      ("right_hand_state","integer"),
                                      ("right_hand_confidence","real")])

    db.create_table(VIDEO_PATH_TABLE, [("performance_id","integer"),
                                       ("path","text")])

    db.create_table(AUDIO_PATH_TABLE, [("performance_id","integer"),
                                       ("audio_id","integer"),
                                       ("path","text")])

    db.create_table(AUDIO_TIME_TABLE, [("performance_id","integer"),
                                       ("audio_id","integer"),
                                       ("start_pos","real"),
                                       ("end_pos","real")])

    db.save()
    db.close()

    return True
    

if __name__ == "__main__":

    # Check if our database is there, if not then create it
    fn = DATABASE

    if not FileExists(fn):
        CreateDatabase(fn)

    app = BodyDataExtract(fn)

    print "Listening for Kinect data"
    
    app.listen()

    print "done"
