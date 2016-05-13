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
        
        raw_input( __doc__ )

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

    print "loading..."

    try:

        pid = int(pid)

    except:

        print "Argument %s is not a valid ID" % repr(pid)

        sys.exit()

    application(pid, **kwargs).run()

    print
    
    raw_input("Done! Press return to exit")
