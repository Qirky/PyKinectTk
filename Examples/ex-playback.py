"""
    Example script for extracting Kinect Data from Kinect Studio
"""

if __name__ == "__main__":

    import PyKinectXEF

    PyKinectXEF.start()    

    App = PyKinectXEF.Playback.KinectDataSelect()
