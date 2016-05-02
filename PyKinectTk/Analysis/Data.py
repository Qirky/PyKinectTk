from copy import copy

class Item:

    def __init__(self, body, joint, axis):

        # Get skeleton data

        self.body  = body
        self.joint = body[joint]
        self.axis  = axis

        # Get time data

        self.frametime = body.all_frame_time()
        self.frames    = sorted(self.frametime.keys())
        self.time_pts  = sorted(self.frametime.values())

        # Get the values

        self.position  = self.joint.get(self.axis)

        # Prepare axis

        self.x = []
        self.y = []

        # Plot descriptors

        self.label   = None
        self.x_label = None
        self.y_label = None

    def __str__(self):
        return str(self.body._name) + '-' + str(self.joint._name) + "-" + str(self.axis) + "_axis"

    def __repr__(self):
        return str(self)

    def __getslice__(self, a, b):
        new = copy(self)

        new.frametime = {}
        new.frames    = []
        new.time_pts  = []
        new.x = []

        for i, f in enumerate(self.frames):

            t = self.time_pts[i]

            if a <= t <= b:

                new.frametime[f] = t
                new.frames.append(f)
                new.time_pts.append(t)

        return new

    def xy(self, relative=False):
        """ Returns a tuple of all x-values and all y-values """

        self.x = []
        self.y = []

        for frame in self.frames:

            self.x.append(self.frametime[frame])
            self.y.append(self.position[frame]-(self.position[self.frames[0]] if relative else 0))
            
        return (self.x, self.y)

    def isEmpty(self):
        """ Returns True if there's no data """
        return len(self.frametime) == 0

class Data:
    """

        This object is used to plot the Kinect Data

    """
    
    data   = None
    bodies = None
    joints = None
    axis   = None
    start  = None
    end    = None

    def __init__(self, data, **kwargs):
            
        self.joints = kwargs.get('joints', ['Head'])
        self.axis   = kwargs.get('axis', 'x')
        self.bodies = kwargs.get('bodies', [str(body) for body in data])

        self.data = []

        for body in data:

            if body in self.bodies:

                for j in self.joints:

                    self.data.append(Item(body, j, self.axis))

    def __iter__(self):
        for item in self.data:
            yield item[self.start:self.end]

    def __getitem__(self, key):
        return self.data[key][self.start:self.end]

    def __getslice__(self, a, b):
        new = copy(self)
        new.start = a
        new.end   = b

        new.data = [item for item in new if not item.isEmpty()]

        return new

    def smooth(self, name=""):
        return self
