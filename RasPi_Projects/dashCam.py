import cv2
import os
import datetime
import time
from gpiozero import Button


#tod: files ot uploadig to root directory ad dashcam folder
# todo: video rus really quickly

class DashCam:
    def __init__(self):
        print("goig")
        ts = datetime.datetime.now()
        self.filename = "{}.avi".format(ts.strftime("%m-%d-%Y_%H-%M-%S"))
        self.outputPath = os.path.join(os.getcwd(), "dashCam")
        print(self.outputPath)
        if not os.path.exists(self.outputPath):
            os.mkdir(self.outputPath)

        ### potetiall chage os.path.sep.joi to waht i use aboce for output path
        self.p = os.path.sep.join((self.outputPath, self.filename))
        print(self.p)

        now = time.time()

        # clear old videos
        for f in os.listdir(self.outputPath):
            f = os.path.join(self.outputPath, f)
            # remove files older than 10 days
            if os.stat(f).st_mtime < now - 10 * 86400:
                if os.path.isfile(f):
                    os.remove(os.path.join(self.outputPath, f))

        statvfs = os.statvfs('/home/pi/')
        usedGB = (statvfs.f_frsize * statvfs.f_blocks)/10**9 # used space w/ Pi
        availableGB = (statvfs.f_frsize * statvfs.f_blocks)/10**9 # free space w/ Pi
        if availableGB <= 5:
            # # Get list of all files only in the given directory
            # list_of_files = filter(lambda x: os.path.isfile(os.path.join(self.p, x)),
            #                        os.listdir(self.p))
            # # Sort list of files based on last modification time in ascending order
            # list_of_files = sorted(list_of_files,
            #                        key=lambda x: os.path.getmtime(os.path.join(self.p, x))
            #                        )

## code above has differet os.path. Istead usig code from testig
            # Get list of all files only in the given directory
            list_of_files = filter(lambda x: os.path.isfile(os.path.join(self.outputPath, x)),
                                   os.listdir())
            # Sort list of files based on last modification time in ascending order
            list_of_files = sorted(list_of_files,
                                   key=lambda x: os.path.getmtime(os.path.join(self.outputPath, x))
                                   )

            # delete the oldest three videos
            for file_name in list_of_files[0:3]:
                file_path = os.path.join(self.outputPath, file_name)
                timestamp_str = time.strftime('%m/%d/%Y :: %H:%M:%S',
                                              time.gmtime(os.path.getmtime(file_path)))
                print(timestamp_str, ' -->', file_name)
                os.remove(file_path)



        # start new video

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
        ## maybe chage self.fileame to self.p
        self.out = cv2.VideoWriter(self.filename, self.get_video_type(self.filename),
                                   25, self.get_dims(self.cap, self.res))

        #setup pi to moiter
        button = Button(21)

    def startVideo(self):
        while button.is_pressed():
            ret, frame = self.cap.read()
            self.out.write(frame)
            self.cv2.imshow('frame', frame)



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
        car_off = time.time()
        while time.time() - car_off <= 90:
            ret, frame = self.cap.read()
            self.out.write(frame)
            self.cv2.imshow('frame', frame)

        # double check car didot go o off
        self.startVideo()
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        os.system("sudo shutdown -h now")



if __name__ == "__main__":
    dash = DashCam()

    dash.startVideo()

    dash.gracefulShutdown()s

