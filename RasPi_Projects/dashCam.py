import cv2
import os
import datetime


class DashCam:
    def __init__(self):
        print("goig")
        ts = datetime.datetime.now()
        self.filename = "{}.avi".format(ts.strftime("%m-%d-%Y_%H-%M-%S"))
        self.outputPath = os.path.join(os.getcwd(), "Movies")
        print(self.outputPath)
        # if not os.path.exists(self.self.outputPath):
        #     os.mkdir(self.outputPath)

        self.p = os.path.sep.join((self.outputPath, self.filename))
        print(self.p)

        # clear old videos
        for i in os.listdir(self.outputPath):

            print(i)
            # if video too old:
            #     os.removedirs(i)

        self.frames_per_second = 24.0
        self.res = '720p'

        self.VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.STD_DIMENSIONS = {
            "480p": (640, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160),
        }
        self.cap = cv2.VideoCapture(0)
        self.out = cv2.VideoWriter(self.filename, self.get_video_type(self.filename),
                                   25, self.get_dims(self.cap, self.res))

    def startVideo(self):
        while True:
            ret, frame = self.cap.read()
            self.out.write(frame)
            self.cv2.imshow('frame', frame)
            if True # BREAK WHE POWER OFF
                break

    # grab resolution dimensions and set video capture to it.
    def get_dims(self, cap, res='720p'):
        width, height = self.STD_DIMENSIONS["480p"]
        if res in self.STD_DIMENSIONS:
            width, height = self.STD_DIMENSIONS[res]
        ## change the current caputre device
        ## to the resulting resolution
        self.change_res(cap, width, height)
        return width, height

    def get_video_type(self, filename):
        filename, ext = os.path.splitext(filename)
        if ext in self.VIDEO_TYPE:
            return self.VIDEO_TYPE[ext]
        return self.VIDEO_TYPE['avi']

    # Set resolution for the video capture
    def change_res(self, cap, width, height):
        cap.set(3, width)
        cap.set(4, height)

    def gracefulShutdown(self):
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        os.shutdow



if __name__ == "__main__":
    dash = DashCam()

    dash.startVideo()

    dash.gracefulShutdown()

