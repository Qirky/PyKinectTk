About the Project
=================

**PyKinectXEF** is a Python package that allows you to extract the data you want from Microsoft extended event files (.xef) generated from the Microsoft Kinect V2 and even from a live stream of data. The package also comes with modules that allow you to play the captured data back, and even plot the data on graphs using matplot.

 
Requirements
------------

- [OpenCV2](https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html#install-opencv-python-in-windows) and its dependencies for colour stream capture
- [PyAutoGUI](https://pyautogui.readthedocs.org/en/latest/) for automated click-stepping
- [comtypes](https://pypi.python.org/pypi/comtypes)
- [matplotlib](https://pypi.python.org/pypi/matplotlib/1.5.1)
- [PyGame](http://pygame.org/hifi.html)*

\* Non-official 64-bit installtion of PyGame can be found [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame)

Examples
--------

In the Examples folder there are two files; `ex-capture.py` and `ex-playback.py`. These can be used to collect data from a running Kinect Service, and also playback this data to the user.

### Example 1: Data Capture

```
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
```
##### The `Init()` Function 

At the start of your application you need to call the `PyKinectXEF.init()` function. It checks the contents of `PyKinectXEF/utils/Settings/config` to see if it contains a filepath. If it does not, you will be asked to select a folder to set as your working environment. This creates a number of directories for storing extracted data. You will only be asked to set  your working environment on your first use, or if the path to the working environment directory changes. For more info on your working environment, see [Your Working Environment](http://foxdot.github.io/PyKinectXEF/API.html).

##### The `PyKinect.Capture.KinectService()` class

This is the Python class that talks to the Microsoft Kinect service that is running on the local machine. The timeout argument specifies how long it should wait after receiving a frame of data from the Kinect Service before deciding any data streams have stopped. Once it has been created, you can invoke the the `listen()` method to begin collecting data that is being processed by the Kinect Service. By default, the `Capture.KinectService()` only captures skeleton data but you can change this by invoking `listen()` with keyword "getter" arguments:

	App = PyKinectXEF.Capture.KinectService(timeout=2)
	App.listen(getAudio=True, getVideo=True, getDepth=True, Clicking=True)

**Note:** Depth data capture has not been implemented yet

The `Clicking` keyword is used to automatically step through files in Kinect Studio, which is useful when you want to process more data intensive streams such as video. `Clicking` **should not** be set to `True` when capturing data from a live stream. For best results when capturing video data, record your data using the Kinect Studio as an `.xef` file and then process it using the automated clicking method. When doing so, you will be asked to hover over the "step file" button in Kinect Studio and press "Return". This will begin automatically clicking the "step file" button every 0.5 seconds (2fps) to ensure minimal video frames are dropped.  
 
---

### Example 2: Data Playback

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



Documentation
-------------

More detailed information on the PyKinectXEF API can be found here:

http://foxdot.github.io/PyKinectXEF/API.html 

Acknowledgements
----------------

This Python package uses a lot of code from PyKinect2, which can be found here: https://github.com/vladkol, and I would like to thank *vladkol* for his incredible work. His existing code has been adapted and is included as a sub-package as part of this module.
