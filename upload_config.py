import boto3

s3 = boto3.resource('s3')
BUCKET = "bubble-config"

s3.Bucket(BUCKET).upload_file(f'config.json', f'config.json')
