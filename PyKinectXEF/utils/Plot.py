""" This is a work in progress """

import matplotlib.pyplot as plt
import Skeleton
from math import sqrt

def Lookup(dictionary, names, default):
    """ Takes a dict and searches for multiple names, returns default if not found """
    for name in names:
        if name in dictionary:
            return dictionary[name]
    return default

class Graph(object):
    """ Object used for creating graphs of body joints 3D locations over time """

    def __init__(self, performance_id):

        self._bodies = Skeleton.LoadPerformance(performance_id)
        plt.xlabel("Time (seconds)")
        self.title = ""

    def list_bodies(self, bodies):
        if bodies == '*':
            bodies = range(len(self._bodies))

        if type(bodies) == int:
            bodies = [bodies]

        return bodies

    def list_joints(self, joints):
        if type(joints) in (int, str):
            joints = [joints]
        return joints

    def plot_pos(self, **kwargs):
        """ Specifies how to plot the graph based on keyword arguments: """
        plt.ylabel("Distance (m)")                   

        bodies = Lookup(kwargs, ['bodies','body'], '*')
        joints = Lookup(kwargs, ['joint', 'Joints'], "Head")
        data   = Lookup(kwargs, ['data','axis','axes'], 'xyz')

        bodies = self.list_bodies(bodies)
        joints = self.list_joints(joints)
        
        timeframe  = kwargs.get("timeframe", None )

        # --- Plot lines to graph

        for b in bodies:

            body = self._bodies[b]

            # X-Axis is ALWAYS time

            x_axis = body.time()

            # Iterate over the joints being plotted

            for j in joints:

                for axis in data:

                    # Update the label depending on the keywords

                    line_label = []

                    # Get the timings of each frame
                    
                    y_axis = body[j].get_all(axis)

                    # Specify the time frame to plot

                    if timeframe:

                        x_axis = [(i, t) for i, t in enumerate(x_axis) if timeframe[0] < t < timeframe[1]]
                        y_axis = [y_axis[i] for i, x in x_axis]
                        x_axis = [x[1] for x in x_axis]

                    # Get the position over time relative to the starting point for the desired axis

                    y_axis = [y - y_axis[0] for y in y_axis]

                    # Plot line

                    plt.plot(x_axis, y_axis, label="Body %d %s %s" % (b, j, axis))

        return

    def plot_vel(self, **kwargs):

        plt.ylabel("Velocity (m/s)")

        bodies = Lookup(kwargs, ['bodies','body'], '*')
        joints = Lookup(kwargs, ['joint', 'joints'], "Head")

        bodies = self.list_bodies(bodies)
        joints = self.list_joints(joints)

        timeframe  = kwargs.get("timeframe", None )

        # --- Plot lines to graph

        for b in bodies:

            body = self._bodies[b]

            for j in joints:

                # Get the timings of each frame

                x_axis = body.time()

                # Get the 3D co-ordinate of the joint
                
                y_axis = [body[j][t] for t in body[j].keys()]

                # Specify the time frame to plot

                if timeframe:

                    x_axis = [(i, t) for i, t in enumerate(x_axis) if timeframe[0] < t < timeframe[1]]
                    y_axis = [y_axis[i] for i, x in x_axis]
                    x_axis = [x[1] for x in x_axis]

                # work out the velocity using v = d2-d1/t2-t1

                tmp_y = []
                tmp_x = []

                for t in range(len(y_axis) - 1):

                    # Get the distance travelled using pythagoras
                    
                    D = sqrt(((y_axis[t+1][0] - y_axis[t][0]) ** 2) +
                             ((y_axis[t+1][1] - y_axis[t][1]) ** 2) +
                             ((y_axis[t+1][2] - y_axis[t][2]) ** 2))
                        
                    T = (x_axis[t+1] - x_axis[t])
                    V =  D / T
                    # Y Axis value is the velocity
                    tmp_y.append(V)
                    # X Axis value is the average time between frames
                    tmp_x.append(x_axis[t] + T/2.0)
                    
                y_axis = tmp_y
                x_axis = tmp_x

                # Add line to the plot

                plt.plot(x_axis, y_axis, label="Body %d %s Velocity" % (b, j))

        return

    def plot_acc(self, **kwargs):

        plt.ylabel("Acceleration (m/s/s)")

        bodies = Lookup(kwargs, ['bodies','body'], '*')
        joints = Lookup(kwargs, ['joint', 'joints'], "Head")

        bodies = self.list_bodies(bodies)
        joints = self.list_joints(joints)

        timeframe  = kwargs.get("timeframe", None )

        # --- Plot lines to graph

        for b in bodies:

            body = self._bodies[b]

            for j in joints:

                # Get the timings of each frame

                x_axis = body.time()

                # Get the 3D co-ordinate of the joint
                
                y_axis = [body[j][t] for t in body[j].keys()]

                # Specify the time frame to plot

                if timeframe:

                    x_axis = [(i, t) for i, t in enumerate(x_axis) if timeframe[0] < t < timeframe[1]]
                    y_axis = [y_axis[i] for i, x in x_axis]
                    x_axis = [x[1] for x in x_axis]

                # work out the velocity using v = d2-d1/t2-t1

                tmp_y = []
                tmp_x = []

                for t in range(len(y_axis) - 1):

                    # Get the distance travelled using pythagoras
                    
                    D = sqrt(((y_axis[t+1][0] - y_axis[t][0]) ** 2) +
                             ((y_axis[t+1][1] - y_axis[t][1]) ** 2) +
                             ((y_axis[t+1][2] - y_axis[t][2]) ** 2))
                        
                    T = (x_axis[t+1] - x_axis[t])
                    V =  D / T
                    tmp_y.append(V)
                    tmp_x.append(x_axis[t] + T/2.0)

                y_axis = tmp_y
                x_axis = tmp_x

                # Work out the acceleration using a = v2-v1/t2-t1

                tmp_y = []
                tmp_x = []

                for t in range(len(y_axis) - 1):
                    # Get the change in velocity
                    V = y_axis[t+1] - y_axis[t]
                    # Get the change in time
                    T = x_axis[t+1] - x_axis[t]
                    # Work out acceleration
                    A = V / T

                    tmp_y.append(A)
                    tmp_x.append(x_axis[t] + T/2.0)

                y_axis = tmp_y
                x_axis = tmp_x

                # Add line to the plot

                plt.plot(x_axis, y_axis, label="Body %d %s Acceleration" % (b, j))

        return

    def view(self, legend=True):
        if legend:
            plt.legend()
        plt.show()
        return

    def title(self, s):
        self.title = s
        plt.title(s)
        return

    def __str__(self):
        return self.title


if __name__ == "__main__":

    # DEBUG

    graph = Graph(1)
    graph.plot_pos(axis='y', joint="Head", timeframe=(40,60))
    #graph.plot_acc(bodies="*", joint="Head", timeframe=(40,60))
    #graph.plot_acc()
    graph.view()
            
        
        
