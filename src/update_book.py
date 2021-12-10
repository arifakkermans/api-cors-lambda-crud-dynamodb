"""
This Lambda functions updates an existing book by isbn.
"""
import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "DEBUG"))
dynamodb_client = boto3.client('dynamodb')
TABLE_NAME = os.env['table']


def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
