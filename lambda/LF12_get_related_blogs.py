import logging
import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('blogs-db')

s3 = boto3.resource('s3')
obj = s3.Object('bubble-config', 'config.json')
data = json.load(obj.get()['Body'])
host = data['host']
master_user = data['masteruser']
master_password = data['masterpassword']

auth = (master_user, master_password)

def lambda_handler(event, context):
    '''
    A function to return related blogs 
    '''
    
    logger.debug(f"[USER][EVENT] {event}")
    logger.debug(f"[USER][CONTEXT] {context}")
    q = {'blog_id': event['blog_id']}
    logger.debug(f"[USER][QUERY] {q}")
    
    res = table.get_item(Key=q)['Item']
    title= res['blog_title']
    blog_id = res['blog_id']
    
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

    query = {
        'size' : 11,
        'query' : {
            'query_string' :{
                'default_field' : 'blog_title',
                'query': title
            }
        }
    }
    candidates_list = []
    index_name = 'blogs'
    response = client.search(body = query, index = index_name)
    if response['hits']['total']['value'] > 0:
        for cur_dict in response['hits']['hits']:
            id = cur_dict["_source"]['blog_id']
            if id == blog_id:
                continue
            q = {'blog_id': id}
            res = table.get_item(Key=q)['Item']
            vote_count = res['upvotes']
            blog_title = cur_dict["_source"]['blog_title']
            candidates_list.append({'blog_id':id, 'blog_title':blog_title,'vote_count':vote_count})
    
    return candidates_list