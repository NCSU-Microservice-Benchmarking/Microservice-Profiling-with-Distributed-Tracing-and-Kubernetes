from select import select
import cv2
import matplotlib.pyplot as plt
from PIL import Image

class VideoReader(object):
    def __init__(self, video_path):
        self.video = cv2.VideoCapture(video_path)
        self.video_total_frame_number = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_frames_count = self.video.get(cv2.CAP_PROP_POS_FRAMES)
        self.is_over = False
    
    '''readNextFrame
    read next frame of the video

    Args:

    Returns:
        flag: bool, true if successfully read the next frame, false if something went wrong in the reading process
        frame: the next video frame, None if reading is failed
        frame_byte_array: the next video frame in the format of byte array, None if reading is failed
    '''
    def readNextFrame(self):
        flag = False
        frame = None
        frame_byte_array = None
        if self.video.get(cv2.CAP_PROP_POS_FRAMES) != self.video.get(cv2.CAP_PROP_FRAME_COUNT):
            flag, frame = self.video.read()
            if flag:
                self.video_frames_count = self.video.get(cv2.CAP_PROP_POS_FRAMES)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
                frame_byte_array = cv2.imencode('.jpg', frame)[1]
                frame_byte_array = bytearray(frame_byte_array)
            else:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, self.video_frames_count-1)
                self.video_frames_count = self.video.get(cv2.CAP_PROP_POS_FRAMES)
        else:
            print("video reading is finished")
            self.is_over = True
        return flag, frame, frame_byte_array
    
    # realse the video
    def releaseVideo(self):
        self.video.release()

    # check whether the video is finishing playing
    def is_finish_playing(self):
        return self.is_over
    
    '''getFramesCount

    count how many frames have been played
    
    Args:
    
    Returns:
        video_frames_count: float, number of played frames
    '''
    def getFramesCount(self):
        return int(self.video_frames_count)

    '''getTotalFrameNumber

    count how many frames are in the video
    
    Args:
    
    Returns:
        video_total_frame_number: float, total number of frames in the video
    '''
    def getTotalFrameNumber(self):
        return int(self.video_total_frame_number)

    def getFPS(self):
        return int(self.video.get(5))


if __name__  == "__main__":

    VIDEO_PATH = "stuttgart_00.avi"

    video_reader = VideoReader(VIDEO_PATH)

    plt.imshow(video_reader.readNextFrame())
    plt.show()

    plt.imshow(video_reader.readNextFrame())
    plt.show()

    print(video_reader.getFramesCount(), video_reader.getTotalFrameNumber())

    video_reader.releaseVideo()