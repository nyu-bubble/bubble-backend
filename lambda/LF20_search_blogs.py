import boto3
import logging
import json
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dynamodb = boto3.resource("dynamodb")

s3 = boto3.resource('s3')
obj = s3.Object('bubble-config', 'config.json')
data = json.load(obj.get()['Body'])
host = data['host']
master_user = data['masteruser']
master_password = data['masterpassword']


port = 5000
auth = (master_user, master_password)

def lambda_handler(event, context):

    logger.debug(f"[USER][EVENT] {event}")
    logger.debug(f"[USER][CONTEXT] {context}")
    client = OpenSearch(
        hosts = [{
            'host': host, 
            'port': '443'
        }],
        http_auth = auth, 
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
        )

    search_string = event['search_string']
    query = {
        'size' : 15,
        'query' : {
            'query_string' :{
                'default_field' : 'blog_title',
                'query': search_string
            }
        }
    }

    candidates_list = []

    index_name = 'blogs'
    response = client.search(body = query, index = index_name)
    if response['hits']['total']['value'] > 0:
        for cur_dict in response['hits']['hits']:
            print(cur_dict)
            id = cur_dict["_id"]
            score = cur_dict["_score"]
            index_type = 'blogs'
            candidates_list.append([score, id, index_type])

    candidates_list.sort(key=lambda x:x[0], reverse=True)

    responses = []
    blogs_table = dynamodb.Table('blogs-db')

    for i in range(min(15, len(candidates_list))):
        new_record = {}
        _id = candidates_list[i][1]
        _type = candidates_list[i][2]
        if _type == 'blogs':
            table = blogs_table
            q = {'blog_id': _id}
            response = table.get_item(Key=q)["Item"]
            read_time = max(1, response["read_time"])
            comment_count = 0
            if "comment_ids" in response.keys():
                comment_count = len(response["comment_ids"])
            cur_response = {
                "blog_id": response["blog_id"],
                "blog_title": response["blog_title"],
                "short_blog_description": response["blog_short_description"],
                "vote_count": response["upvotes"],
                "comment_count": comment_count,
                "timestamp": response["timestamp"],
                "read_time": read_time ,
                "username": response["username"]
            }
            responses.append(cur_response)

    return {
        'statusCode': 200,
        'body': responses
    } 