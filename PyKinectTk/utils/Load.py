"""

    "Loads" a performance using Skeleton and Database data

"""

from SQL import *
from Env import *

import Skeleton

def BodyData(p_id):
    
    # Load the performance Data

    with Database(DATABASE) as db:
        table = JOINT_DATA_TABLE, BODY_TIME_TABLE, BODY_NAME_TABLE
        
        # Load the co-ordinates and frame timestamps
        
        data = db.query(JOINT_DATA_TABLE, p_id)
        time = db.query(BODY_TIME_TABLE, p_id)

        # Load any custom name labels for the bodies

        role = [r[0] for r in db.query(BODY_NAME_TABLE, p_id, columns=("name",))]
        
    # Convert time to a dict

    time = dict([(row['frame'], row['time']) for row in time])

    num_bodies = max([row['body'] for row in data]) + 1
    
    bodies = [Skeleton.Body(name=(role[n] if n < len(role) else n)) for n in range(num_bodies)]

    for row in data:
        
        body  = bodies[row['body']]

        joint = body[row['joint_id']]

        # Assign 3D co-ordinates (m) in 2dp

        joint[row['frame']] = [f for f in (row['x'], row['y'], row['z'])]

        # Add 2D co-ordinates (px)

        joint.add(row['frame'], row['pixel_x'], row['pixel_y'])

        # Get the real time values and add to BODY object

        body.frame_time(row['frame'], time[row['frame']])

    return bodies

def VideoData(p_id):
    """ Takes a performance id and returns a dictionary of frame numbers and their timestamps """

    # Load frames and times

    with Database(DATABASE) as db:

        data = db.query(VIDEO_TIME_TABLE, p_id)

    # Return as a dict -> Frame no. & Time

    return dict([(row['frame'], row['time']) for row in data])

class FrameTime:

    def __init__(self, frametime):

        self.frametimes = frametime
        
        self.frames = sorted(frametime.keys())[:-1]
        self.times  = sorted(frametime.values())

        self.l = len(self.frametimes)

        try:
            self.max_t = self.times[-1]
        except:
            self.max_t = 0

        try:
            self.max_f = self.frames[-1]
        except:
            self.max_f = 0

    def __len__(self):
        return self.l

    def size(self):
        return self.l

    def max_time(self):
        return self.max_t

    def max_frame(self):
        return self.max_f

    def timestamps(self):

        return self.frametimes.values()

    def __iter__(self):

        for n in self.frametimes:

            yield n

    def __getitem__(self, key):

        return self.frametimes[key]

    def time_at_frame(self, frame):

        return self.frametimes[frame]

    def frame_at_time(self, time):

        for i in range(len(self.frames)-1):

            if time <= self.frametimes[self.frames[i+1]]:

                return self.frames[i]

        else:

            raise TimeIndexError("No frame found at time '{}'".format(time))

def PerformanceID(PerformanceName):
    """ Returns the ID number of a recording based on a name - case invariant.
        Raises an error if not found """

    with Database(DATABASE) as db:

        for row in db[PERFORMANCE_NAME_TABLE]:

            if row['name'].lower() == PerformanceName.lower():

                return row['performance_id']

    raise KeyError("Recording '%s' not found" % PerformanceName)



def DeletePerformance(p_id):
    """ For each table in the database, remove all records where performance_id == p_id """

    with Database(DATABASE) as db:

        for tbl in db.get_tables():

            if "performance_id" in db.get_columns(tbl):

                db.delete(tbl, "performance_id = %s" % str(p_id))

    return True


# Exceptions

class TimeIndexError(Exception):
    pass


        
