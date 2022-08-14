import cv2
import os
import datetime
import time
import sys
import RPi.GPIO as GPIO
from threading import Timer, Thread
import shutil
import numpy as np
from queue import Queue


class DashCam:
    def __init__(self, fps, clear_space=True, debug=False):
        self.clear_space = clear_space
        self.debug_mode = debug

        # create directory and initialize file path
        ts = datetime.datetime.now()
        self.filename = "{}.avi".format(ts.strftime("%m-%d-%Y_%H-%M-%S"))
        self.outputPath = os.path.join(os.getcwd(), "cam_videos")
        self.first_path = os.path.join(os.getcwd(), self.filename)  # file location before it moves to dash directory
        if not os.path.exists(self.outputPath):
            os.mkdir(self.outputPath)


        # last chance to prevent videos from being deleted on boot.
        self.stop_auto_boot()

        if self.clear_space:
            # clear old videos
            self.delete_files_after_days(10)

            availableGB = self.check_space('/home/alexscottlewis/')

            if availableGB <= 7:
                self.delete_oldest_three()

            if self.debug_mode:
                self.delete_oldest_three()

        # video initialization
        self.frames_per_second = fps  # 8.4  # decreasing fps increases length of vieo bug
        self.res = '720p'

        self.VIDEO_TYPE = {
            # 'avi': cv2.VideoWriter_fourcc(*'XVID'),
            'avi': cv2.VideoWriter_fourcc(*'MJPG'),  # this codec works for both mac and raspi
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
                                   self.frames_per_second, self.get_dims(self.cap, self.res))
        self.Q = Queue(maxsize=125)
        self.stopped = False

        # setup pi to check car on
        if not self.debug_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(21, GPIO.IN)
            print(GPIO.input(21))

        seconds_till_restart = 60 * 60  # restart script to prevent too long of video 60min
        self.timer = Timer(seconds_till_restart, lambda: self.restart_system())  # restart system after 4s
        self.timer.start()

        self.frames = 0
        self.start_time = 0

    # create thread object to que frames
    def start_vid_thread(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    # update que with video frames
    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return
            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.cap.read()
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                # add the frame to the queue
                self.Q.put(frame)

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def start_video(self):
        # document start time for debugging fps
        self.start_time = time.time()

        if not self.debug_mode:
            # save video frames while car powered
            while GPIO.input(21):
                frame = self.read()
                self.out.write(frame)
                self.frames += 1
        else:
            frame = self.read()
            self.out.write(frame)
            self.frames += 1

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

    # close out connections to camera for proper shutdown
    def close_video_stream(self):
        self.stop()
        # save the last of the frames in the que
        while self.more():
            frame = self.read()
            self.out.write(frame)
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        self.adjust_video_output()
        shutil.move(self.first_path, self.outputPath)

    # turn off pi after 30s of car powering down
    def graceful_shutdown(self):
        car_off = time.time()
        print("Graceful shutdown")
        while time.time() - car_off <= 30:
            frame = self.read()
            self.out.write(frame)
            self.frames += 1

        # double check to see if car is back on
        if not self.debug_mode:
            if GPIO.input(21):
                self.restart_system()

        self.close_video_stream()
        if not self.debug_mode:
            os.system("sudo shutdown -h now")

    # when video gets too long, restart the video feed and double check that the available storage
    def restart_system(self):
        if self.debug_mode:
            print("Restart")
        self.close_video_stream()
        # recall this script with os
        os.execv(sys.executable, ['python'] + sys.argv)

    # delete the oldest 3 videos from the pi
    def delete_oldest_three(self):
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(self.outputPath, x)),
                               os.listdir(self.outputPath))
        # Sort list of files based on last modification time in ascending order
        list_of_files = sorted(list_of_files,
                               key=lambda x: os.path.getmtime(os.path.join(self.outputPath, x))
                               )

        # delete the oldest three videos
        for file_name in list_of_files[0:3]:
            file_path = os.path.join(self.outputPath, file_name)
            timestamp_str = time.strftime('%m/%d/%Y :: %H:%M:%S',
                                          time.gmtime(os.path.getmtime(file_path)))
            if not self.debug_mode:
                os.remove(file_path)
            else:
                print(timestamp_str, ' -->', file_name)

    # check how much memory on Raspi
    def check_space(self, directory):
        statvfs = os.statvfs(directory)
        availableGB = (statvfs.f_frsize * statvfs.f_bfree) / 10 ** 9  # used space w/ Pi
        total_spaceGB = (statvfs.f_frsize * statvfs.f_blocks) / 10 ** 9  # free space w/ Pi
        if self.debug_mode:
            print("total space:", total_spaceGB)
            print('available:', availableGB)
            print("-----")
        return availableGB

    # check if camera is connected before deleting old files. This prevents crash footage from being deleted
    def stop_auto_boot(self):
        # prevent script from running if no camera is connected. This protects old videos that might have a crash
        # from being automatically deleted.
        cap2 = cv2.VideoCapture(0)
        if cap2 is None or not cap2.isOpened():
            raise AttributeError("Camera is not connected!")
        cap2.release()

    # delete the files older tha a certai amout of days
    def delete_files_after_days(self, days):
        now = time.time()

        for f in os.listdir(self.outputPath):
            f = os.path.join(self.outputPath, f)
            # remove files older than 10 days
            if os.stat(f).st_mtime < now - days * (24 * 60 * 60):
                if os.path.isfile(f):
                    if not self.debug_mode:
                        os.remove(os.path.join(self.outputPath, f))
                    else:
                        print(os.path.join(self.outputPath, f))

    # debugging some fps issues with raspi that don't show up on mac.
    def adjust_video_output(self):
        duration = time.time() - self.start_time
        actualFps = np.ceil(self.frames / duration)
        print(self.frames)
        print(actualFps)

#         os.system('ffmpeg -y -i {} -c copy -f h264 tmp.h264'.format(self.filename))
#         os.system('ffmpeg -y -r {} -i tmp.h264 -c copy {}'.format(actualFps, self.filename))



if __name__ == "__main__":
    dash = DashCam(8.4, clear_space=True, debug=False)

    dash.start_vid_thread()
    dash.start_video()

    dash.graceful_shutdown()

