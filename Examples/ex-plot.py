"""
    ex-plot.py

        Example script for plotting Kinect Body Frame data over time
"""

if __name__ == "__main__":

    # Import module

    import PyKinectTk

    # Create a blank plot

    plot = PyKinectTk.Analysis.Plot()

    # Load the data

    #name = raw_input("Recording Name: ")

    name = "heartofmyheart_deadpan"

    p_id = PyKinectTk.Load.PerformanceID(name)

    print "%s found. Loading..." % name,

    data = PyKinectTk.Load.BodyData(p_id)

    print "Done"

    # Choose the data you want to see

    head = PyKinectTk.Analysis.Data(data,
                                    #bodies = ["lead","tenor"],
                                    joints=['head'],
                                    axis='x')

    # Choose the timeframe (15s - 30s)

    head = head[30:120]

    # Plot the data

    plot.add(head, relative=True)

    # Save the data as CSV

    #plot.save("data.csv")

    # View using matplotlib

    plot.display()
    
