"""
    Example script for extracting Kinect Data from Kinect Studio
"""

if __name__ == "__main__":

    # Import module

    import PyKinectXEF

    # Initialise work environment

    PyKinectXEF.init()

    # Create TKinter GUI to select recording

    App = PyKinectXEF.Playback.KinectDataSelect()
