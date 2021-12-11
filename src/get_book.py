"""
This Lambda function returns a book by isbn.
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
        "body": "An error occured while getting book."
    }
    # Validate if event is not none
    if event['pathParameters'] is None:
        validation_error = models.InvalidUsage(
            message="no query param provided").create_response_body()
        return validation_error

    isbn = event['pathParameters']['id']

    # Validate if isbn consists of 13 digits
    if len(isbn) != 13 or not isbn.isdigit():
        validation_error = models.InvalidUsage(
            message=f"invalid isbn {isbn} must be a 13char digit"
        ).create_response_body()
        return validation_error

    # Query DynamoDB and use isbn as the partition key
    book_query = dynamodb_client.get_item(
        TableName=TABLE_NAME, Key={'isbn': {'S': isbn}})
    if 'Item' in book_query:
        book = book_query['Item']
        logger.info(f'Book is: {book}')
        response = {
            "statusCode": 200,
            "body": json.dumps(dynamodb_parser.unmarshal_dynamodb_json(book))
        }

    else:
        validation_error = models.InvalidUsage(
            message=f"no isbn found with id {isbn}", status_code=404
        ).create_response_body()
        return validation_error

    # Return the book
    return response
