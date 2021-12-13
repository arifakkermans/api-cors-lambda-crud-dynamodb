"""
This Lambda function updates an existing book by isbn.
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
        "body": f"An error occured while updating book"
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

    # Validate if request body matches with our schema
    try:
        request_body = models.book_request_body_from_dict(
            json.loads(event["body"]))
    except AssertionError:
        validation_error = models.InvalidUsage(
            message="request body malformed"
        ).create_response_body()
        return validation_error

    # Validate if body is not empty
    if event['body'] is None:
        validation_error = models.InvalidUsage(
            message="no request body provided").create_response_body()
        return validation_error

    try:
        res = dynamodb_client.update_item(
            TableName=TABLE_NAME,
            Key={
                'isbn': {'S': isbn}
            },
            ConditionExpression='attribute_exists(isbn)',
            UpdateExpression="set book_name=:b, authors=:a, languages=:l, countries=:c, number_of_pages=:n, release_date=:r",
            ExpressionAttributeValues={
                ":b": {"S": request_body.name},
                ":a": {"S": request_body.authors},
                ":l": {"S": request_body.languages},
                ":c": {"S": request_body.countries},
                ":n": {"S": request_body.number_of_pages},
                ":r": {"S": request_body.release_date}

            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
            validation_error = models.InvalidUsage(
                message="Book does not exist", status_code=404
            ).create_response_body()
            return validation_error

    # Check if put is successful
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 201,
            "body": f"Location: /books/{isbn}"
        }
    else:
        validation_error = models.InvalidUsage(
            message=f"an error occurred putting isbn {isbn}"
        ).create_response_body()
        return validation_error  

    # Return 200 ok
    return response
