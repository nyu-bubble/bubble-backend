# bubble-backend

1. Create a bucket "bubble-code"
2. Run "upload_lambda.py"
3. Run "upload_layers.py"
4. Use cloudformation to create stack
    aws cloudformation create-stack --template-body file://cloudformation/bubble-cf-v2.yaml --capabilities CAPABILITY_IAM --stack-name bubble
5. Create a bucket "bubble-config"
6. Update file "config.json" with opensearch url, masteruser, masterpassword
7. Run "upload_config.py" 