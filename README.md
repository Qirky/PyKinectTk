The Python Kinect Toolkit
=========================

The **Python Kinect Toolkit** (PyKinectTk) is a Python package that allows you to extract the data you want from Microsoft extended event files (.xef) generated from the Microsoft Kinect V2, and even from a live stream of data. The package also comes with modules that allow you to play the captured data back, and plot the data on graphs using matplot.


Requirements
------------

- [OpenCV2](https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html#install-opencv-python-in-windows)
- [PyAutoGUI](https://pyautogui.readthedocs.org/en/latest/)
- [comtypes](https://pypi.python.org/pypi/comtypes)
- [matplotlib](https://pypi.python.org/pypi/matplotlib/1.5.1)

Installation
------------

Download the `.zip` or `.tar.gz` file and extract its contents. Then, from the command line, change directory to where you extracted the files and run the command `python setup.py install` and you're good to go! I hope to have this up on `pip` in the near future.

Examples
--------

In the Examples folder there are two files; `ex-capture.py` and `ex-playback.py`. These can be used to collect data from a running Kinect Service, and also playback this data to the user.

### Example 1: Data Capture

```Python
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
    
    App.listen(getVideo=True, Clicking=True)

    # Add a meaningful name to the recording
    
    name = raw_input("Would you like to name your recording? ")

    App.NameRecording(name)

    # Exit

    raw_input("Recording saved as '%s', press Return to quit" % name)

    App.close()
```
##### First time use

On first import, PyKinectTk checks the contents of `PyKinectTk/utils/Settings/config` to see if it contains a filepath. If it does not, you will be asked to select a folder to set as your working environment. This creates a number of directories for storing extracted data. You will only be asked to set  your working environment on your first use, or if the path to the working environment directory changes. For more info on your working environment, see [Your Working Environment](https://github.com/Qirky/PyKinectTk/blob/master/docs.md).

##### The `PyKinect.Capture.KinectService()` class

This is the Python class that talks to the Microsoft Kinect service that is running on the local machine. The timeout argument specifies how long it should wait after receiving a frame of data from the Kinect Service before deciding any data streams have stopped. Once it has been created, you can invoke the the `listen()` method to begin collecting data that is being processed by the Kinect Service. By default, the `Capture.KinectService()` only captures skeleton data but you can change this by invoking `listen()` with keyword "getter" arguments:

```Python
App = PyKinectTk.Capture.KinectService(timeout=2)
App.listen(getAudio=True, getVideo=True, getDepth=True, Clicking=True)
```

**Note:** Depth data capture has not been implemented yet

The `Clicking` keyword is used to automatically step through files in Kinect Studio, which is useful when you want to process more data intensive streams such as video. `Clicking` **should not** be set to `True` when capturing data from a live stream. For best results when capturing video data, record your data using the Kinect Studio as an `.xef` file and then process it using the automated clicking method. When doing so, you will be asked to hover over the "step file" button in Kinect Studio and press "Return". This will begin automatically clicking the "step file" button every 0.5 seconds (2fps) to ensure minimal video frames are dropped.  

---

### Example 2: Data Playback

```Python
"""
ex-playback.py

    Example script for combining extracted
    data streams and playing them back to the user

    To use the graphical user interface:

        python ex-playback.py -GUI

    CLI Usage:

        python ex-playback.py <recording_id>

        python ex-playback.py -n <recording_name>

    Other flags:

    -video  :   1 to display RGB video, 0 to skip. Default is 0.
    -info   :   1 to display frame no. and time stamp, 0 to skip. Default is 1.
    -body   :   1 to display wireframes, 0 to skip. Default is 1.
    
    -c <output.avi>     :   Signals the program to convert the playback data to an .avi file
    -t <start:end>      :   Specifies the timeframe (in seconds) to playback
"""


if __name__ == "__main__":

    # Get command arguments from the user

    import sys, shlex

    args = sys.argv[1:] if sys.argv[1:] else shlex.split(raw_input("Input: "))

    if len(args) < 1:
        
        print __doc__

        sys.exit()
    
    # Import module

    import PyKinectTk

    # Create TKinter GUI to select recording

    if "-GUI" in args:

        application = PyKinectTk.Playback.KinectDataSelect()

        sys.exit()

    else:

        application = PyKinectTk.Playback.KinectDataPlayer

    # Can choose a recording by cli

    kwargs = {}

    # By default, the first argument is the id of the recordings

    pid = args[0]

    if "-n" in args:

        pid = PyKinectTk.Load.PerformanceID(args[args.index("-n") + 1])

    if "-c" in args:

        application = PyKinectTk.Playback.ConvertKinect

        kwargs['outputFile'] =  args[args.index("-c") + 1]

    if "-t" in args:

        time = args[args.index("-t") + 1].split(':')

        time = tuple([float(t) if t else None for t in time])

        kwargs['time'] = time

    if "-video" in args:

        kwargs['video'] = bool(args[args.index("-video") + 1])

    if "-body" in args:

        kwargs['body'] = bool(args[args.index("-body") + 1])

    if "-info" in args:

        kwargs['info'] = bool(args[args.index("-info") + 1])

    # Run application

    print "loading..." ,

    try:

        pid = int(pid)

    except:

        print "Argument %s is not a valid ID" % repr(pid)

        sys.exit()

    application(pid, **kwargs).run()

    raw_input("done! Press return to exit")
```

Documentation
-------------

Technical documentation for the project is found in the docs.md file found here: *[PyKinectTk Documentation](https://github.com/Qirky/PyKinectTk/blob/master/docs.md)*

Acknowledgements
----------------

This Python package uses a lot of code from PyKinect2, which can be found here: https://github.com/vladkol, and I would like to thank *vladkol* for his incredible work. His existing code has been adapted and is included as a sub-package as part of this module.
