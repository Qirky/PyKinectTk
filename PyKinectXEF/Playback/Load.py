"""

    "Loads" a performance using Skeleton and Database data

"""

from ..utils import *
from ..utils.SQL import *

def BodyData(p_id):
    
    # Load the performance Data

    with Database(DATABASE) as db:
        table = JOINT_DATA_TABLE, BODY_TIME_TABLE
        
        data = [row for row in db[table[0]] if row['performance_id'] == int(p_id)]
        time = [row for row in db[table[1]] if row['performance_id'] == int(p_id)]

    # Convert time to a dict

    time = dict([(row['frame'], row['time']) for row in time])

    num_bodies = max([row['body'] for row in data]) + 1

    bodies = [Skeleton.Body() for n in range(num_bodies)]

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

        data = [row for row in db[VIDEO_TIME_TABLE] if row['performance_id'] == int(p_id)]

    # Return as a dict -> Frame no. & Time

    return dict([(row['frame'], row['time']) for row in data])

class FrameTime:

    def __init__(self, frametime):

        self.frametimes = frametime
        
        self.frames = sorted(frametime.keys())[:-1]

        self.l = len(self.frametimes)

    def __len__(self):
        return self.l

    def size(self):
        return self.l

    def timestamps(self):

        return self.frametimes.values()

    def __iter__(self):

        for n in self.frametimes:

            yield n

    def __getitem__(self, key):

        return self.frametimes[key]

    def frame_at_time(self, time):

        for i, frame in enumerate(self.frames):

            if time <= self.frametimes[self.frames[i+1]]:

                return frame      







        
