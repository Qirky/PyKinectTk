"""
    Example script for extracting Kinect Data from Kinect Studio
"""

if __name__ == "__main__":

    # Import package

    import PyKinectXEF

    # Initialise work environment

    PyKinectXEF.init()

    # Create connection to Kinect Service

    App = PyKinectXEF.Capture.KinectService(timeout=2)

    # Start capturing data using auto-click

    print "Listening for Kinect data"
    
    App.listen(getVideo=True, Clicking=True)

    # Add a meaningful name to the recording
    
    name = raw_input("Would you like to name your recording? ")

    App.NameRecording(name)

    # Exit

    raw_input("Recording saved as '%s', press Return to quit" % name)

    App.close()
