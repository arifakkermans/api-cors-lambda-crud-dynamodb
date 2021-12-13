"""
This Lambda function deletes an existing book by isbn.
"""
import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

import models

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "DEBUG"))
TABLE_NAME = os.environ.get('table')
dynamodb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    logger.info("Looking for events")
    logger.info("- - - - - - - - - - - - - - - - - - -")
    logger.info(f'Incoming request is: {event}')
    # Set the default error response
    response = {
        "statusCode": 500,
        "body": f"An error occured while deleting book"
    }

    # Validate if query parameter is not empty
    if event['pathParameters'] is None:
        validation_error = models.InvalidUsage(
            message="no query param provided").create_response_body()
        return validation_error

    isbn = event['pathParameters']['isbn']

    # Validate if isbn consists of 13 digits
    if len(isbn) != 13 or not isbn.isdigit():
        validation_error = models.InvalidUsage(
            message=f"invalid isbn {isbn} must be a 13char digit"
        ).create_response_body()
        return validation_error

    try:
        res = dynamodb_client.delete_item(
            TableName=TABLE_NAME,
            ConditionExpression='attribute_exists(isbn)',
            Key={
                'isbn': {'S': isbn},
            })
    except ClientError as error:
        if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
            validation_error = models.InvalidUsage(
                message="Book does not exist", status_code=404
            ).create_response_body()
            return validation_error

    # If deletion is successful for post
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 204
        }

    # Return 204 deleted
    return response
