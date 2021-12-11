"""
This Lambda functions deletes an existing book by isbn.
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


def lambda_handler(event, context):
    logger.info(f'Incoming request is: {event}')

    # Set the default error response
    response = {
        "statusCode": 500,
        "body": f"An error occured while deleting book"
    }
    if event['pathParameters'] is None:
        validation_error = models.InvalidUsage(
            message="no query param provided").create_response_body()
        return validation_error

    isbn = event['pathParameters']['id']

    if not isbn:
        validation_error = models.InvalidUsage(
            message="no query param provided").create_response_body()
        return validation_error

    if len(isbn) != 13 or not isbn.isdigit():
        validation_error = models.InvalidUsage(
            message=f"invalid isbn {isbn} must be a 13char digit"
        ).create_response_body()
        return validation_error
        
    logger.info(f'Incoming request is: {event}')

    res = dynamodb_client.delete_item(TableName=TABLE_NAME, Key={
        'isbn': {'S': isbn}})

    # If deletion is successful for post
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 204
        }
    return response
