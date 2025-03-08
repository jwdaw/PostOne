import boto3

def upload_to_s3(file_path, bucket_name):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bucket_name, file_path.split("/")[-1])
    return f"https://{bucket_name}.s3.amazonaws.com/{file_path.split('/')[-1]}"