class HashList:
    """ A tuple-like array that supports addressing by string values """
    def __init__(self, *args):
        self.contents = tuple(args)

    def __len__(self):
        return len(self.contents)

    def __iter__(self):
        for item in self.contents:
            yield item

    def __str__(self):
        return str(self.contents)

    def __getitem__(self, key):
        if type(key) is int:
            if key < len(self):
                return self.contents[key]
            else:
                raise IndexError("Sequence index out of range.")
        if type(key) is str:
            for item in self.contents:
                if item == key:
                    return item
            raise KeyError("String key '%s' not found." % key)
        raise TypeError

    def __setitem__(self, key, value):
        raise TypeError("'HashList' object does not support item assignment")



class Joint:
    """ Represents a Kinect Skeleton Joint with a 3D (real plane)
        and 2D (pixel plane) state that changes over time """

    def __init__(self, name, joint_id=None):

        self._name = name
        self._id = joint_id

        self._view = {} # These are dicts of frame no. -> co-ords
        self._real = {}
        self._time = {}
        
        self._children = []
        self._parent = None

    def set_id(self, number):
        self._id = number
        return

    def ID(self):
        return self._id

    def add_child(self, *children):
        for child in children:
            self._children.append( child )
            child._parent = self
        return

    def __eq__(self, other):
        return str(other).lower() == str(self).lower()
            
    def __len__(self):
        return len(self._children)

    def __str__(self):
        return str(self._name)

    def __iter__(self):
        for value in self._view:
            yield value

    def __getitem__(self, key):
        return self._real[key]

    def keys(self):
        return sorted(self._real.keys())

    def __setitem__(self, key, value):
        self._real[key] = value

    def __contains__(self, key):
        return key in self._view

    def add(self, t, x, y):
        self._view[t] = (x, y)

    def pixel(self, t):
        return self._view[t]

    def bones(self, t):
        return [(self.pixel(t), child.pixel(t)) for child in self._children]
    
    def position(self, t):
        return self._real[t]

    def get_all(self, axis):
        if axis in "xX":
            return self.x()
        if axis in "yY":
            return self.y()
        if axis in "zZ":
            return self.z()

    def x(self, t=None):
        if t is not None:
            return  self._real[t][0]
        else:
            return [self._real[t][0] for t in self._real.keys()]

    def y(self, t=None):
        if t is not None:
            return  self._real[t][1]
        else:
            return [self._real[t][1] for t in self._real.keys()]

    def z(self, t=None):
        if t is not None:
            return  self._real[t][2]
        else:
            return [self._real[t][2] for t in self._real.keys()]

    def children(self):
        return self._children

    def parent(self):
        return self._parent

    def isParent(self):
        return bool(self._children)

    def isLeaf(self):
        return not bool(self._children)

# Define Joint Data

class Joints(HashList):

    def __init__(self):

        HashList.__init__(self,
              
            Joint('SpineBase'),
            Joint('SpineMid'),
            Joint('Neck'),
            Joint('Head'),
            Joint('ShoulderLeft'),
            Joint('ElbowLeft'),
            Joint('WristLeft'),
            Joint('HandLeft'),
            Joint('ShoulderRight'),
            Joint('ElbowRight'),
            Joint('WristRight'),
            Joint('HandRight'),
            Joint('HipLeft'),
            Joint('KneeLeft'),
            Joint('AnkleLeft'),
            Joint('FootLeft'),
            Joint('HipRight'),
            Joint('KneeRight'),
            Joint('AnkleRight'),
            Joint('FootRight'),
            Joint('SpineShoulder'),
            Joint('HandTipLeft'),
            Joint('ThumbLeft'),
            Joint('HandTipRight'),
            Joint('ThumbRight')
        )

        # JointTypes index are also their Kinect IDs

        for index, joint in enumerate(self):
            joint.set_id(index)

        # Define the relationship between joints

        # Spine
        self[0].add_child(self[1], self[12], self[16])
        self[1].add_child(self[20])
        self[2].add_child(self[3])
        self[20].add_child(self[2], self[4], self[8])

        # Left Arm
        self[4].add_child(self[5])
        self[5].add_child(self[6])
        self[6].add_child(self[7], self[22])
        self[7].add_child(self[21])

        # Right Arm
        self[8].add_child(self[9])
        self[9].add_child(self[10])
        self[10].add_child(self[11], self[24])
        self[11].add_child(self[23])

        # Left Leg
        self[12].add_child(self[13])
        self[13].add_child(self[14])
        self[14].add_child(self[15])

        # Right Leg
        self[16].add_child(self[17])
        self[17].add_child(self[18])
        self[18].add_child(self[19])

    def __str__(self):
        return str([str(j) for j in self])

class Body:
    """ Body(Joints()) returns an 'empty' body """

    def __init__(self, joints=None, tracking_id=None):

        if joints is not None:
            self._joints = joints
        else:
            self._joints = Joints()
            
        self._id = tracking_id

        self._time = {} # Dict of frame no. -> real time val

    def __getitem__(self, key):
        return self._joints[key]

    def __iter__(self):
        for j in self._joints:
            yield j

    def frame_time(self, frame, t=None):
        if t:  self._time[frame] = t
        return self._time[frame]

    def time(self):
        return self._time.values()

    def frames(self):
        return self._time.keys()

    def all_frame_time(self):
        return self._time

    def hasData(self, t):
        """ returns the a bool of whether the head node has data """
        return t in self._joints['Head']
        

class State:
    """ Object that hold an integer state and equivalent name """
    def __init__(self, name, num):

        self._id = num
        self._name = name

    def __str__(self):
        return str(self._name)

    def __eq__(self, other):
        return (str(other).lower() == str(self).lower()) or (other == self._id)


# Hashable list types

JointTypes = Joints()

HandStates = HashList(
                        State('Unknown', 0),
                        State('NotTracked', 1),
                        State('Open', 2),
                        State('Closed', 3),
                        State('Lasso', 4)
                      )


TrackStates = HashList(
                        State('NotTracked',0),
                        State('Inferred', 1),
                        State('Tracked', 2)
                       )

### - Activity ID
##Activity_EyeLeftClosed = 0
##Activity_EyeRightClosed = 1
##Activity_MouthOpen = 2
##Activity_MouthMoved = 3
##Activity_LookingAway = 4
##
### values for enumeration '_DetectionResult'
##DetectionResult_Unknown = 0
##DetectionResult_No = 1
##DetectionResult_Maybe = 2
##DetectionResult_Yes = 3
##

# Returns a list of Body objects with data filled using the database

def LoadPerformance(p_id):

    import SQL
    
    # Load the performance Data

    db = SQL.Database("../Performances.db")
    table = "tbl_JointData", "tbl_FrameTime"
    data = [row for row in db[table[0]] if row['performance_id'] == int(p_id)]
    time = [row for row in db[table[1]] if row['performance_id'] == int(p_id)]
    db.close()

    # Convert time to a dict

    time = dict([(row['frame'], row['time']) for row in time])

    num_bodies = max([row['body'] for row in data]) + 1

    bodies = [Body() for n in range(num_bodies)]

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

if __name__ == "__main__":
    # Debug
    p = LoadPerformance(1)
    print p[0].frame_time(501)
