import cv2
import os
import datetime
import time

# print(os.getcwd())

outputPath = os.path.join(os.getcwd(), "dashCam")
print(outputPath)
if not os.path.exists(outputPath):
    os.mkdir(outputPath)

now = time.time()
print(now)

# clear old videos
for f in os.listdir(outputPath):
    f = os.path.join(outputPath, f)
    print(f)
    print(os.stat(f).st_mtime)
    if os.stat(f).st_mtime < now - 20:
        # if os.path.isfile(f):
        os.rmdir(os.path.join(outputPath, f))

statvfs = os.statvfs('/Users/alexlewis/')
print((statvfs.f_frsize * statvfs.f_blocks)/10**9)
print((statvfs.f_frsize * statvfs.f_bfree)/10**9)
print((statvfs.f_frsize * statvfs.f_bavail)/10**9)