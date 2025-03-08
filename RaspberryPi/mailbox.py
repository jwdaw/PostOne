import RPi.GPIO as GPIO
import time
import subprocess
import boto3
from datetime import datetime

# Configuration
TRIG = 23
ECHO = 24
SENSOR_THRESHOLD = 10  # Distance in cm (adjust based on your mailbox)
BUCKET_NAME = 'your-mailbox-bucket'
SNS_TOPIC_ARN = 'arn:aws:sns:your-region:your-account-id:MailboxAlert'

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.5)
    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to cm
    return round(distance, 2)

def capture_image():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"/home/pi/mailbox_images/{timestamp}.jpg"
    subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", filename])
    return filename

def upload_to_s3(file_path):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, BUCKET_NAME, file_path.split("/")[-1])
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_path.split('/')[-1]}"

def send_sns(message, image_url):
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"{message}\nView image: {image_url}",
        Subject='New Mail Alert!'
    )

def main():
    # Configure AWS credentials
    boto3.setup_default_session(
        aws_access_key_id='YOUR_ACCESS_KEY',
        aws_secret_access_key='YOUR_SECRET_KEY',
        region_name='your-region'
    )
    
    try:
        while True:
            dist = measure_distance()
            print(f"Distance: {dist} cm")
            
            if dist < SENSOR_THRESHOLD:
                print("Mail detected!")
                image_path = capture_image()
                image_url = upload_to_s3(image_path)
                send_sns("New mail arrived!", image_url)
                time.sleep(60)  # Prevent multiple alerts
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()