# This script takes timelapse pictures with the Raspberry Pi camera module and uploads them to a server.
# Use crontab to run this script at the intervals of your choosing.
# Uploads the most recent image (e.g. picture.png), a copy to an archive folder (e.g. archive/20240521_2300.png), and date.txt with the most recent date and time.
# Folder write permissions required on the server.

# Configuration
hostname = 'yourserver.com'
port = 22
username = 'your_raspberrys_username_on_the_server'
password = 'your_password'
image_name = 'picture.png'
upside_down_camera = False   # set True to rotate the image 180 degrees in case the camera is mounted upside down




import os
import time
from datetime import datetime
import paramiko
from picamera2 import Picamera2
from PIL import Image

current_directory = os.path.dirname(os.path.abspath(__file__))
local_image_path = os.path.join(current_directory, image_name)
local_date_file_path = os.path.join(current_directory, 'date.txt')

remote_image_path = '/home/pi/timelapse/timelapse.png'
remote_date_path = '/home/pi/timelapse/date.txt'
remote_archive_dir = '/home/pi/timelapse/archive/'

# Initialize the camera and take the photo
camera = Picamera2()
camera_config = camera.create_still_configuration()
camera.configure(camera_config)
camera.start()
time.sleep(2)  # Wait for camera to adjust
camera.capture_file(local_image_path)
camera.stop()
if upside_down_camera:
    with Image.open(local_image_path) as img:
        rotated_img = img.rotate(180)
        rotated_img.save(local_image_path)

# Get the current date and time and set archive path accordingly
now = datetime.now()
date_str = now.strftime("%Y-%m-%d %H:%M")
datetime_str = now.strftime("%Y%m%d_%H%M")
archive_image_path = os.path.join(current_directory, f'{datetime_str}.png')
os.rename(local_image_path, archive_image_path)
with open(local_date_file_path, 'w') as date_file:
    date_file.write(date_str)

# Upload files via SSH
def upload_file(local_path, remote_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    sftp = ssh.open_sftp()

    remote_dir = os.path.dirname(remote_path)

    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print(f"Uploaded {remote_path}")

upload_file(archive_image_path, remote_image_path)
upload_file(local_date_file_path, remote_date_path)
upload_file(archive_image_path, os.path.join(remote_archive_dir, f'{datetime_str}.png'))
os.remove(archive_image_path)
os.remove(local_date_file_path)