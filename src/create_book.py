"""
This Lambda functions creates a new book.
"""
import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "DEBUG"))
TABLE_NAME = os.environ.get('table')
dynamodb_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
