from camera import capture_image
from distance_sensor import measure_distance
from upload import upload_to_s3
import boto3
import os
from dotenv import load_dotenv
import time

load_dotenv()
BUCKET_NAME = os.getenv("BUCKET_NAME")

isOpen = False
prev_is_open = False

ARR_SIZE = 7
measureArr = [0] * ARR_SIZE
while True:
    # Update measurements
    measureArr.append(measure_distance())
    measureArr.pop(0)
    time.sleep(0.05)
    med_dist = sorted(measureArr)[ARR_SIZE//2]
    is_open = med_dist > 50

    # Trigger only on rising edge (closed -> open transition)
    if is_open and not prev_is_open:
        filename = capture_image()
        if filename:
            # Upload and clean up
            fileURL = upload_to_s3(filename, BUCKET_NAME)
            print("Sent image to:", fileURL)
            os.remove(filename)
            print("Deleted the image.")

    # Update previous state
    prev_is_open = is_open