"""
    ex-capture.py
    
        Example script for extracting Kinect Data from Kinect Studio
"""

if __name__ == "__main__":

    # Import package

    import PyKinectTk

    # Create connection to Kinect Service

    App = PyKinectTk.Capture.KinectService(timeout=2)

    # Start capturing data using auto-click

    print "Listening for Kinect data"
    
    App.listen(getVideo=True, Clicking=True, duration=120)

    # Add a meaningful name to the recording
    
    name = raw_input("Would you like to name your recording? ")

    App.NameRecording(name)

    # Exit

    raw_input("Recording saved as '%s', press Return to quit" % name)

    App.close()
