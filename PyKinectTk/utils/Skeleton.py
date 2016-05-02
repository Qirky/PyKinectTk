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

        self._view = {} # Dict of frame no. -> 2D co-ords
        self._real = {} # Dict of frame no. -> 3D co-ords
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

    def bones_3D(self, t):
        return [(self.position(t), child.position(t)) for child in self._children]
    
    def position(self, t):
        return self._real[t]

    @staticmethod
    def index(axis):
        return "xyz".index(axis.lower())

    def separate(self, axis="xyz"):
        d={}
        for a in axis:
            d[a] = dict([(frame, self._real[frame][self.index(a)]) for frame in sorted(self._real.keys())])
        return d

    def get(self, axis):
        if axis in "xX":
            n = 0
        elif axis in "yY":
            n = 1
        elif axis in "zZ":
            n = 2
        else:
            raise ValueError("Axis must be X, Y, or Z")
        return dict([(frame, value[n]) for frame, value in self._real.items()])
    
    def get_all(self, axis, frame=None):
        if axis in "xX":
            return self.x(frame)
        if axis in "yY":
            return self.y(frame)
        if axis in "zZ":
            return self.z(frame)

    def value(self, axis, frame):
        return self.get_all(axis, frame)

    def x(self, t=None):
        if t is not None:
            return  self._real[t][0]
        else:
            return [self._real[t][0] for t in sorted(self._real.keys())]

    def y(self, t=None):
        if t is not None:
            return  self._real[t][1]
        else:
            return [self._real[t][1] for t in sorted(self._real.keys())]

    def z(self, t=None):
        if t is not None:
            return  self._real[t][2]
        else:
            return [self._real[t][2] for t in sorted(self._real.keys())]

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
              
            Joint('SpineBase'),         # 0
            Joint('SpineMid'),          # 1
            Joint('Neck'),              # 2
            Joint('Head'),              # 3
            Joint('ShoulderLeft'),      # 4
            Joint('ElbowLeft'),         # 5
            Joint('WristLeft'),         # 6
            Joint('HandLeft'),          # 7
            Joint('ShoulderRight'),     # 8
            Joint('ElbowRight'),        # 9
            Joint('WristRight'),        # 10
            Joint('HandRight'),         # 11
            Joint('HipLeft'),           # 12
            Joint('KneeLeft'),          # 13
            Joint('AnkleLeft'),         # 14
            Joint('FootLeft'),          # 15
            Joint('HipRight'),          # 16
            Joint('KneeRight'),         # 17
            Joint('AnkleRight'),        # 18
            Joint('FootRight'),         # 19
            Joint('SpineShoulder'),     # 20
            Joint('HandTipLeft'),       # 21
            Joint('ThumbLeft'),         # 22
            Joint('HandTipRight'),      # 23
            Joint('ThumbRight')         # 24
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
        self[4].add_child(self[5], self[12]) # Add shoulder to hip
        self[5].add_child(self[6])
        self[6].add_child(self[7], self[22])
        self[7].add_child(self[21])

        # Right Arm
        self[8].add_child(self[9], self[16]) # Add shoulder to hip
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

    def __init__(self, joints=None, tracking_id=None, name="Null"):

        if joints is not None:
            self._joints = joints
        else:
            self._joints = Joints()
            
        self._id = tracking_id

        self._time = {} # Dict of frame no. -> real time val

        self._name = name

    def __str__(self):
        return str(self._name)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __getitem__(self, key):
        return self._joints[key]

    def __iter__(self):
        for j in self._joints:
            yield j

    def frame_time(self, frame, t=None):
        if t is not None:
            self._time[frame] = t
        return self._time[frame]

    def time(self):
        return self._time.values()

    def frames(self):
        return self._time.keys()

    def all_frame_time(self, timeframe=None):
        if timeframe:
            return dict([(frame, time) for frame, time in self._time.items() if timeframe[0] <= time <= timeframe[1]])
        return self._time

    def num_bones(self):
        num = 0
        for j in self._joints:
            num += len(j.children())
        return num

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
