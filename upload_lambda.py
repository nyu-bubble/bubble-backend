import boto3
import os
import shutil


s3 = boto3.resource('s3')
BUCKET = "bubble-code"

if not os.path.exists('temp'):
    os.mkdir('temp')

# Uploading python function
for name in os.listdir("lambda"):
    fn_name = name.split('.')[0]
    shutil.make_archive(f'temp/{fn_name}', 'zip', 'lambda', name)
    s3.Bucket(BUCKET).upload_file(f'temp/{fn_name}.zip', f'lambda/{fn_name}.zip')


shutil.rmtree('temp')
