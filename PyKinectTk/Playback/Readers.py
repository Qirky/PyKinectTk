from ..utils import *
from ..utils.SQL import *
from cv2 import VideoCapture

class VideoReader:

    def __init__(self,  p_id):

        with Database(DATABASE) as db:
            path = VIDEO_DIR + db.get('path','tbl_VideoPath','performance_id',p_id)

        self.data = VideoCapture(path)

    def read(self):

        read, contents = self.data.read()

        if read:

            return contents

        else:

            raise StopIteration

    def set_frame(self, frame):

        self.data.set(1, frame)

        return

    def close(self):

        self.data.release()

        return
        
        
