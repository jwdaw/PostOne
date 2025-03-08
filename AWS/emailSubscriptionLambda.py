# Original testing file for SNS to subscribe
# emails and send test email.

import json
import boto3

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body['email']

        sns = boto3.client('sns')
        topic_arn = 'arn:aws:sns:us-east-1:598087621063:EmailTest' 

        response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"message": "Confirmation email sent. Please check your inbox."})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"message": f"An error occurred: {str(e)}"})
        }