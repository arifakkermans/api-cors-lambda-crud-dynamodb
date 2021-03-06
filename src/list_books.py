"""
This Lambda function returns all books in the DB.
"""
import json
import logging
import os

import boto3

import models


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "DEBUG"))
TABLE_NAME = os.environ.get('table')
dynamodb_client = boto3.client('dynamodb')
dynamodb_parser = models.DynamoParser()


def lambda_handler(event, context):
    logger.info("Looking for events")
    logger.info("- - - - - - - - - - - - - - - - - - -")
    logger.info(f'Incoming request is: {event}')
    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occured while fetching all books."
    }

    scan_result = dynamodb_client.scan(TableName=TABLE_NAME)['Items']

    books = []

    for item in scan_result:
        item = dynamodb_parser.unmarshal_dynamodb_json(item)
        books.append(item)

    response = {
        "statusCode": 200,
        "body": json.dumps(books)
    }

    # Return all books
    return response
