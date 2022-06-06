import subprocess
import shutil
import os
import boto3

s3 = boto3.resource('s3')
BUCKET = "bubble-code"

req_libraries = {
    'req_simp':['requests', 'simplejson'], 
    'opensearch':['opensearch-py'], 
    'bs4':['beautifulsoup4']
    }

if not os.path.exists('temp'):
    os.mkdir('temp')
if not os.path.exists('layers'):
    os.mkdir('layers')

for name, libs in req_libraries.items():
    print(name)
    lib_str = ' '.join(libs)
    p = subprocess.Popen(f'pip install {lib_str} -t temp/python', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     for line in p.stdout.readlines():
#         print(line.decode())
    retval = p.wait()
    shutil.make_archive(f'layers/{name}', 'zip', f'temp')
    shutil.rmtree('temp/python')

# Uploading layers
for name in os.listdir("layers"):
    filepath = f'layers/{name}'
    s3.Bucket(BUCKET).upload_file(filepath, filepath)

shutil.rmtree('temp')
shutil.rmtree('layers')


