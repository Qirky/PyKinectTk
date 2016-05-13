    
if __name__ == "__main__":

    import PyKinectTk

    # Load a recording

    recordings = ["LetTheRestoftheworldgoby_Normal",
                  "LetTheRestoftheworldgoby_deadpan",
                  "LetTheRestoftheworldgoby_Exag"]

    for i, name in enumerate(recordings):

        print i + 1, "/", len(recordings), name

        p_id = PyKinectTk.Load.PerformanceID(name)

        f = open("%s.csv" % name, "w")

        # Use image subtraction to get quantity of motion over last 30 frames

        frames = 30

        Img = PyKinectTk.Analysis.MotionDetection(p_id, frames)
        Vid = PyKinectTk.Load.VideoData(p_id)

        print "running...",

        while frames <= max(Vid.keys()):

            # Get motion image for the last second

            arr = Img.MotionImage(threshold=225)

            try:

                # Calculate the proportion of the screen is white pixels
            
                f.write( str(Vid[frames]) + "," + str(Img.Proportion(arr)) + "\n")

            except:

                pass

            frames += 1

        print "done"

        f.close()
        Img.close()
