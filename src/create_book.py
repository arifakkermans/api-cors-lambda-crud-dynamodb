"""
This Lambda function creates a new book.
"""
import datetime
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
        "body": "An error occured while creating the book."
    }

    # Validate if body is not empty
    if event['body'] is None:
        validation_error = models.InvalidUsage(
            message="no request body provided").create_response_body()
        return validation_error

    # Validate if request body matches with our schema
    try:
        request_body = models.book_request_body_from_dict(
            json.loads(event["body"]))
        # Validate if releasedate matches the ISO 8601 standard
        valid = models.validate_releasedate(request_body.release_date)
        if not valid:
            validation_error = models.InvalidUsage(
                message="releasedate does not match YYYY-MM-DD (ISO 8601)"
            ).create_response_body()
            return validation_error
    except AssertionError:
        validation_error = models.InvalidUsage(
            message="request body malformed"
        ).create_response_body()
        return validation_error

    # Validate if isbn consists of 13 digits
    if len(request_body.isbn) != 13 or not request_body.isbn.isdigit():
        validation_error = models.InvalidUsage(
            message=f"invalid isbn {request_body.isbn} must be a 13char digit"
        ).create_response_body()
        return validation_error

    try:
        res = dynamodb_client.put_item(
            TableName=TABLE_NAME,
            Item={
                "isbn": {"S": request_body.isbn},
                "book_name": {"S": request_body.name},
                "authors": {"S": request_body.authors},
                "languages": {"S": request_body.languages},
                "countries": {"S": request_body.countries},
                "number_of_pages": {"S": request_body.number_of_pages},
                "release_date": {"S": request_body.release_date}
            },
            ConditionExpression='attribute_not_exists(isbn)'
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
            validation_error = models.InvalidUsage(
                message="Book already exist", status_code=403
            ).create_response_body()
            return validation_error

    # Check if post is successful
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 201,
            "body": f"Location: /books/{request_body.isbn}"
        }
    else:
        validation_error = models.InvalidUsage(
            message=f"an error occurred putting isbn {request_body.isbn}"
        ).create_response_body()
        return validation_error

    # Return 201 created with the location of the book
    return response
