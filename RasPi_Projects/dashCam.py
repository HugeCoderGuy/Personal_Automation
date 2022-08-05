import cv2
import os
import datetime
import time
import sys
from gpiozero import Button
from threading import Timer



#tod: files ot uploadig to root directory ad dashcam folder
# todo: video rus really quickly

class DashCam:
    def __init__(self, clear_space=True, debug=False):
        self.clear_space = clear_space
        self.debug_mode = debug

        ts = datetime.datetime.now()
        self.filename = "{}.avi".format(ts.strftime("%m-%d-%Y_%H-%M-%S"))
        self.outputPath = os.path.join(os.getcwd(), "dashCam")
        print(self.outputPath)
        if not os.path.exists(self.outputPath):
            os.mkdir(self.outputPath)

        ### potetiall chage os.path.sep.joi to waht i use aboce for output path
        self.p = os.path.sep.join((self.outputPath, self.filename))

        now = time.time()

        if self.clear_space:
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
            if availableGB <= 7:
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
            # 'avi': cv2.VideoWriter_fourcc(*'XVID'),
            'avi': cv2.VideoWriter_fourcc(*'MJPG'),
            # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
            # 'mp4': cv2.VideoWriter_fourcc(*'XVID'),
            'mp4': cv2.VideoWriter_fourcc(*'DIVX')
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

        # setup pi to check car on
        if not self.debug_mode:
            self.button = Button(21)

        # self.timer = Timer(3300, self.restart_system())  # restart system after 55mins
        if self.debug_mode:
            self.timer = Timer(4, lambda: self.restart_system())  # restart system after 55mins
        else:
            self.timer = Timer(55*60, self.restart_system())  # restart system after 55mins
        self.timer.start()

    def start_video(self):
        if not self.debug_mode:
            while self.button.is_pressed():
                ret, frame = self.cap.read()
                self.out.write(frame)
                cv2.imshow('frame', frame)
        else:
            ret, frame = self.cap.read()
            self.out.write(frame)
            cv2.imshow('frame', frame)

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

    def graceful_shutdown(self):
        car_off = time.time()
        while time.time() - car_off <= 10:
            ret, frame = self.cap.read()
            self.out.write(frame)
            if self.debug_mode:
                cv2.imshow('frame', frame)
                print("here")

        ## double check to see if car is bback o
        if not self.debug_mode:
            if self.button.is_pressed():
                self.restart_system()

        # double check car didot go o off
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        # os.system("sudo shutdown -h now")

    def restart_system(self):
        if self.debug_mode:
            print("restart")
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == "__main__":
    dash = DashCam(clear_space=False, debug=True)

    dash.start_video()

    dash.graceful_shutdown()

