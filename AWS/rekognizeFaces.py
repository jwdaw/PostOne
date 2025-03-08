# Final code for our prototype to analyze
# uploaded image and send an email to the user

import boto3
from decimal import Decimal
import json
import urllib.request
import urllib.parse
import urllib.error

print('Loading function')

rekognition = boto3.client('rekognition')  # initialize rekognition client 
s3_client = boto3.client("s3")  # Initialize s3 client
ses = boto3.client('ses')  # Initialize SES client

# Replace these with your verified email addresses
SES_SENDER_EMAIL = "jwd2464@gmail.com"  # Your verified sender
SES_RECIPIENT_EMAIL = "jwd2464@gmail.com"  # Your recipient

def generate_presigned_url(bucket, key, expiration=3600):
    """Generate a pre-signed URL for the S3 object (valid for 1 hour)."""
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiration
    )
    return url

def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    try:
        # First detect all faces
        face_detection_response = detect_faces(bucket, key)
        face_count = len(face_detection_response.get('FaceDetails', []))
        
        # Then search for known faces
        name = "An Unrecognized Person"
        try:
            search_response = rekognition.search_faces_by_image(
                CollectionId='known-faces',
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                FaceMatchThreshold=85
            )
            
            if search_response['FaceMatches']:
                # Known face detected
                for match in search_response['FaceMatches']:
                    print(f"Found {match['Face']['ExternalImageId']} ({match['Similarity']}%)")
                    name = " ".join(match['Face']['ExternalImageId'].split("-"))
            else:
                print("No known faces detected")
        except Exception as search_error:
            print(f"Error searching for faces: {search_error}")
              
        # Generate Image URL
        image_url = generate_presigned_url(bucket, key)

        # Create an HTML message with inline styling
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mailbox Alert</title>
</head>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #2E86C1; margin-bottom: 20px;">📸 {name} Is At Your Mailbox!</h2>
    <div style="margin-bottom: 20px;">
        <img src="{image_url}" alt="Mailbox Image" style="max-width: 100%; border-radius: 5px; border: 1px solid #ddd;">
    </div>
    <p style="font-size: 14px; line-height: 1.5;">We detected motion at your mailbox!</p>
    <p style="font-size: 14px; line-height: 1.5;">Take a look below and check if you recognize the following person or motion disturbance.</p>
    <p style="font-size: 14px; line-height: 1.5;"><strong>Faces Detected:</strong> {face_count}</p>
    <p style="margin-top: 20px;">
        <a href="{image_url}" style="background-color: #2E86C1; color: white; padding: 10px 15px; border-radius: 4px; text-decoration: none; font-weight: bold; display: inline-block;">View Full Image</a>
    </p>
</body>
</html>
"""

        plain_text_message = f"""
{name} is at your mailbox!
Image: {key}
Bucket: {bucket}
Faces Detected: {face_count}
View Image: {image_url}
"""

        # Send email via SES
        response_ses = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={
                'ToAddresses': [SES_RECIPIENT_EMAIL]
            },
            Message={
                'Subject': {
                    'Data': f'{name} Is At Your Mailbox',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': plain_text_message,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_message,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print(f"Email sent! Message ID: {response_ses['MessageId']}")
        return {"statusCode": 200, "body": "Email sent successfully"}
        
    except Exception as e:
        print(e)
        print(f"Error processing object {key} from bucket {bucket}.")
        raise e