"""
    Example script for extracting Kinect Data from Kinect Studio
"""

if __name__ == "__main__":

    from PyKinectXEF import Capture

    App = Capture.KinectService(timeout=2)

    print "Listening for Kinect data"
    
    App.listen(getVideo=True, Clicking=True)
    
    name = raw_input("Would you like to name your recording? ")

    App.NameRecording(name)

    raw_input("Recording saved as '%s', press Return to quit" % name)

    App.close()
