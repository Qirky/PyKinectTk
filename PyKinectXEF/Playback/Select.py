# Utility modules
from ..utils import *
from ..utils.SQL import *

# tKinter for creating user interface

import Tkinter as tk
from tkFileDialog import askopenfilename
from tkMessageBox import showwarning as WarnMsg
from tkMessageBox import showinfo as InfoMsg

# Player uses PyGame to run the file back to us
from Player import KinectDataPlayer
from Convert import ConvertKinect

class KinectDataSelect:
    """ Tkinter UI for selecting a processed Kinect file for playing back """

    def __init__(self):

        # init

        self._root = tk.Tk()

        # Load initial data from database

        self._db = Database(DATABASE)
        
        tbl_PerformanceName = self._db["tbl_PerformanceName"]
        tbl_AudioPath       = self._db["tbl_AudioPath"]

        # Create widget to display selector
        self._listbox = tk.Listbox(self._root)
        self._listbox.pack()
        self._performances = []
        for i, name in tbl_PerformanceName:
            self._listbox.insert(tk.END, name)
            self._performances.append(i)

        # Add Audio Button
        self._addAudio = tk.Button(self._root, text="Add Audio Files", command=self.add_audio)
        self._addAudio.pack()

        # Playback Button
        self._playback = tk.Button(self._root, text="Play", command=self.start_playback)
        self._playback.pack()

        # Save to video Button
        self._toVideo = tk.Button(self._root, text="Save as Video", command=self.to_video)
        self._toVideo.pack()

        # Location of videos
        self._video_fp_root = VIDEO_DIR + "%s.avi"

        # Run
        self._root.mainloop()

    def close(self):
        """ Close connection with database """
        self._db.close()
        self._root.destroy()
        return

    def selected(self):
        """ Returns the index of the selected item """
        return self._listbox.curselection()[0]

    def performance_name(self):
        """ Returns the name of the selected item """
        return self._listbox.get(self.selected())

    def video_filename(self):
        """ Returns the video file path of the recording """
        return (self._video_fp_root % self.performance_name())

    def performance_id(self):
        """ Returns the performance ID of the selected item """
        return self._performances[self.selected()]

    def associated_audio(self, pid):
        paths = {}
        for row in self._db["tbl_AudioPath"]:
            if row['performance_id'] == pid:
                paths[row['audio_id']] = row['path']
        return paths

    def audio_paths(self, pid):
        """ Returns a list of audio file paths for a performance """
        return self.associated_audio(pid).values()

    def audio_id(self, pid):
        """ Returns a list of all the audio IDs for associated audio """
        return self.associated_audio(pid).keys()

    def start_playback(self):
        """ Loads the performance data and plays back with pygame """

        if True:#try:

            # Get the performance id

            pid = self.performance_id()

            # Begin pygame playback

            player = KinectDataPlayer(pid, video=True)
            self._root.withdraw()
            player.run()

            # re-show root

            self._root.deiconify()

        else:#except:

            pass

        return

    def to_video(self):
        """ Creates a player object that outputs to file not screen """

        try:

            # Get the performance id

            pid = self.performance_id()

            # Begin pygame to video

            player = ConvertKinect(pid, self.video_filename())
            player.run()

            InfoMsg("File Saved", "%s has been saved successfully" % self.video_filename())

        except:

            pass

        return

    def openfilepath(self):
        """ Returns the realpath of a file from tkinter open file dialog """
        f = askopenfilename()
        return realpath(f)

    def add_audio(self):
        """ Opens file dialog for adding audio waveforms to a performance """

        if 1==1: #try:        
        
            # Get pid

            p_id = self.performance_id()

            # Get the file to add
            
            fn = self.openfilepath()
            
            # If the file is already added to it, show a message

            if fn in self.audio_paths(p_id):

                WarnMsg("Warning", "Wav file '%s' is already attached to this performance." % fn)

            else:

                # Get the newest audio_id

                a_id = max(self.audio_id(p_id)) + 1

                # Update database

                self._db.insert("tbl_AudioPath", [("performance_id", p_id), ("audio_id", a_id), ("path", fn)])

                self._db.save()
                
                InfoMsg("Audio Added", "Wav file '%s' has been added to the selected performance" % fn )
                
        else:#except:

            pass

        return       
