import simplejson as json
import logging
import boto3
import uuid
from datetime import datetime

from boto3.dynamodb.types import TypeSerializer
from decimal import Decimal
import six
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    # TODO implement
    logger.debug(f"[USER][EVENT] {event}")
    logger.debug(f"[USER][CONTEXT] {context}")
    
    
    if "question_id" in event.keys():
        table_name, prim_key = ("questions-db", "question_id")
    elif "answer_id" in event.keys():
        table_name, prim_key= ("answers-db", "answer_id")
    elif "review_id" in event.keys():
        table_name, prim_key = ("professor-reviews-db", "review_id")
    elif "comment_id" in event.keys():
        return {"status": 400,"message":"Bad request"}
    elif 'blog_id' in event.keys():
        table_name, prim_key= ("blogs-db", "blog_id")
    else:
        return {"status": 400,"message":"Bad request"}
        
    
    
    response = set_delete(event, table_name, prim_key)
    return response

def set_delete(event, tname, pkey):
    try:
        response = client.transact_write_items(
            TransactItems=[
                {
                    "Update":{
                        "TableName": tname,
                        "Key":{
                            pkey:{"S":event[pkey]}
                        },
                        "UpdateExpression": "SET deleted = :delete_bool",
                        "ExpressionAttributeValues":{
                            ":delete_bool": {"BOOL": False}
                        }
                        
                    }
                }
            ]
        )
    except Exception as e:
        logger.debug(f"[USER][EXCEPTION] {e}")
        return {"status": 400,"message":"Something unexpected happened"}
    
    return {"status": 200,"message":"Task completed"}
    
        
        
    
def json_serial(o):
    if isinstance(o, datetime):
        serial = o.strftime('%Y-%m-%dT%H:%M:%S.%f')
    elif isinstance(o, Decimal):
        if o % 1 > 0:
            serial = float(o)
        elif six.PY3:
            serial = int(o)
        elif o < sys.maxsize:
            serial = int(o)
        else:
            serial = long(o)
    elif isinstance(o, uuid.UUID):
        serial = str(o.hex)
    elif isinstance(o, set):
        serial = list(o)
    else:
        serial = o
    return serial


def dumps(dct, as_dict=False, **kwargs):
    """ Dump the dict to json in DynamoDB Format
        You can use any other simplejson or json options
        :param dct - the dict to dump
        :param as_dict - returns the result as python dict (useful for DynamoDB boto3 library) or as json sting
        :returns: DynamoDB json format.
        """

    result_ = TypeSerializer().serialize(json.loads(json.dumps(dct, default=json_serial),
                                                    use_decimal=True))
    if as_dict:
        return next(six.iteritems(result_))[1]
    else:
        return json.dumps(next(six.iteritems(result_))[1], **kwargs)