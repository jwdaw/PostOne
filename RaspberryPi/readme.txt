# Raspberry Pi Code
This section of the PostOne Application is responsible for monitoring the state of the ultrasonic sensor and capturing images. It then takes those images and uploads them to AWS S3. Before running the `main.py` you should have the AWS CLI configured and have a S3 bucket created with the bucket name stored as an environment variable.
