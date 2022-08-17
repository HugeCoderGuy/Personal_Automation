import cv2
import os
import datetime
import time
import sys
import RPi.GPIO as GPIO
from threading import Timer, Thread
import shutil
import numpy as np


class DashCam:
    def __init__(self, fps, clear_space=True, debug=False):
        self.working_directory = '/home/alexscottlewis'
        os.chdir(self.working_directory)
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
        print("[SETUP] Camera Connected!")

        if self.clear_space:
            # clear old videos
            self.delete_files_after_days(7)

            availableGB = self.check_space(self.working_directory)
            if availableGB <= 5:
                self.delete_oldest_three()

            if self.debug_mode:
                self.delete_oldest_three()
            
            print("[SETUP] Old and unnecessary videos have been delted.")
            

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
        self.stopped = False
        self.cancel_video_write = False
        # create first instance of frame for video writer
        (self.grabbed, self.frame) = self.cap.read()

        # setup pi to check car on
        if not self.debug_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(21, GPIO.IN)

        seconds_till_restart = 30 * 60  # restart script to prevent too long of video 60min
        self.timer = Timer(seconds_till_restart, lambda: self.restart_system())  # restart system after 4s
        self.timer.start()

        self.frames = 0
        self.start_time = 0
        print("[SETUP] Ready to Record! Video will loop after {} mins.".format(seconds_till_restart/60))

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
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                # print("here")
                return
            # otherwise, ensure the queue has room in it
            else:
                (self.grabbed, self.frame) = self.cap.read()


    # stop all blocking functions once called
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # indicate if video writer should stop
        self.cancel_video_write = True

    # constant loop to save video frames while car is on
    def start_video(self):
        # document start time for debugging fps
        self.start_time = time.time()

        if not self.debug_mode:
            # save video frames while car powered
            while GPIO.input(21) and not self.cancel_video_write:
                self.out.write(self.frame)
                self.frames += 1
        else:
            self.out.write(self.frame)
            self.frames += 1

    # grab resolution dimensions and set video capture to it.
    def get_dims(self, cap, res='720p'):
        width, height = self.STD_DIMENSIONS["480p"]
        if res in self.STD_DIMENSIONS:
            width, height = self.STD_DIMENSIONS[res]
        self.change_res(cap, width, height)
        return width, height

    # identify corresponding codec for video container
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
        # prevent video writer and capture from occurring
        self.stop()

        # preform final close up actions
        self.cap.release()
        if self.debug_mode:
            self.track_frame_rate()
        self.out = None
        time.sleep(1)

        shutil.move(self.first_path, self.outputPath)

    # turn off pi after 30s of car powering down
    def graceful_shutdown(self):
        car_off = time.time()
        print("[DashCam] Begining system Shutdown.")
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        while time.time() - car_off <= 30:
            if not self.cancel_video_write:
                temp_frame = self.frame
                cv2.putText(self.frame, "IGNITION OFF", (25, 50), font, 1, (0, 0, 255), 2, cv2.LINE_4)
                # Important, Copy frame from thread to prevent segmentation fault
                self.out.write(temp_frame)
                self.frames += 1
                if self.debug_mode:
                    print(self.frames)

        # double check to see if car is back on
        if not self.debug_mode:
            if GPIO.input(21):
                self.restart_system()

        self.close_video_stream()
        if not self.debug_mode:
            print("[DashCam] Goodbye!")
            os.system("sudo shutdown -h now")

    # when video gets too long, restart the video feed and double check that the available storage
    def restart_system(self):
        print("[DashCam] Looping Video. System will now restart")
        self.close_video_stream()
        # recall dashCam.py script from command line
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
    def track_frame_rate(self):
        duration = time.time() - self.start_time
        actualFps = np.ceil(self.frames / duration)
        print(self.frames)
        print(actualFps)


if __name__ == "__main__":
    # framerate runs fine during testing. RasPi is a little funky and needs an awkward framerate for operation
    dash = DashCam(8.4, clear_space=True, debug=False)

    # start video capture and video writer in seperate threads
    dash.start_vid_thread()
    dash.start_video()

    # power down system when car is off
    dash.graceful_shutdown()

