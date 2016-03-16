"""
    ex-playback.py

        Example script for combining extracted
        data streams and playing them back to the user
"""

if __name__ == "__main__":

    # Import module

    import PyKinectXEF

    # Initialise work environment

    PyKinectXEF.init()

    # Create TKinter GUI to select recording

    App = PyKinectXEF.Playback.KinectDataSelect()
