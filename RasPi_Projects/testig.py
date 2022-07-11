import cv2
import os
import datetime
import time

# print(os.getcwd())



outputPath = os.path.join(os.getcwd(), "dashCam")
outputPath = os.getcwd()
print(outputPath)
if not os.path.exists(outputPath):
    os.mkdir(outputPath)

# Get list of all files only in the given directory
list_of_files = filter(lambda x: os.path.isfile(os.path.join(outputPath, x)),
                       os.listdir())
# Sort list of files based on last modification time in ascending order
list_of_files = sorted(list_of_files,
                       key=lambda x: os.path.getmtime(os.path.join(outputPath, x))
                       )
# Iterate over sorted list of files and print file path
# along with last modification time of file
print(list_of_files)            # TO DO: DELETEE THE LAST THREE FILES I DIRECTORY. ITERATE to FILE 3

for file_name in list_of_files[0:3]:
    file_path = os.path.join(outputPath, file_name)
    timestamp_str = time.strftime('%m/%d/%Y :: %H:%M:%S',
                                  time.gmtime(os.path.getmtime(file_path)))
    print(timestamp_str, ' -->', file_name)


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