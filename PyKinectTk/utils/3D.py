"""
    3D.py is the interface for plotting Skeleton Wireframes in a 3D
    perspective using matplotlib

"""

# 3D Plotting tool
from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

# PyKinect XEF modules
import Colour

#: 3D View Obj
class View:

    def __init__(self, bodies, **kwargs):
        """ data is a from Load.BodyData """

        # Performance data
        
        self.bodies = bodies

        # Setup Plot
        self.fig = plt.figure()
        self.axis = self.fig.add_subplot(111, projection='3d')
        self.axis.axis('on')

        # Define the lines being used

        kwargs['marker'] = '.'
        kwargs['ms'] = 5
        
        self.lines = []
    
        for i, body in enumerate(self.bodies):

            body_lines = []

            for joint in body:

                for child in joint.children():

                    body_lines += self.axis.plot([],[],[], c = Colour.plt[i], **kwargs)

            self.lines.append(body_lines)


        # Settings
        self.axis.set_ylim(-2,2)
        self.axis.set_xlim(0,4)
        self.axis.set_zlim(-2,2)

        self.rate = 1.0 / 3.0

    def update(self, frame):
        """ Used to animate the drawing - passes a blitting=True argument to draw() """
        self.draw(frame, blitting=True)
        return self.lines

    def draw(self, frame, blitting=False):
        """ Draw the bodies at this frame """
        for body in range(len(self.bodies)):
            try:
                self.draw_body(body, frame)
            except:
                pass

        if blitting:
            self.fig.canvas.blit()
        else:
            self.display()

        return

    @staticmethod
    def display():
        plt.show()

    def draw_body(self, body, frame):
        """ Draws one body at frame """
        bone = 0
        for joint in self.bodies[body]:
            for start, end in joint.bones_3D(frame):
                self.draw_bone(body, start, end, bone)
                bone += 1

    def draw_bone(self, body, a, b, i):
        """ Draws update line i to draw a line between a and b """

        # Re-order axes
            # Kinect Axis Z is depth  (matplot X)
            # Kinect Axis Y is height (matplot Z)
            # Kinect Axis X is width  (matplot y)
            
        y, z, x = [(a[n],b[n]) for n in range(3)]
        
        self.lines[body][i].set_data(x, y)
        self.lines[body][i].set_3d_properties(z)

def animate(view):
    """ Takes a 3D.View object and 'plays' the frames """
    try:
        mov = animation.FuncAnimation(view.fig, view.update, interval=view.rate, blit=False)
        view.display()
    except:
        pass

if __name__ == "__main__":

    # debug

    import Load

    a = View(Load.BodyData(5))

    animate(a)
