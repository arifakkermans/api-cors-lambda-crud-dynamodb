"""
This Lambda function updates an existing book by isbn.
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
        "body": f"An error occured while updating book"
    }

    # Validate if query parameter is not empty
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

    # Validate if body is not empty
    if event['body'] is None:
        validation_error = models.InvalidUsage(
            message="no request body provided").create_response_body()
        return validation_error

    book_str = event['body']
    book = json.loads(book_str)

    res = dynamodb_client.update_item(
        TableName=TABLE_NAME,
        Key={
            'isbn': {'S': isbn}
        },
        UpdateExpression="set authors=:a, languages=:l, countries=:c, number_of_pages=:n, release_date=:r",
        ExpressionAttributeValues={
            ":a": {"S": book['authors']},
            ":l": {"S": book['languages']},
            ":c": {"S": book['countries']},
            ":n": {"S": book['numberOfPages']},
            ":r": {"S": book['releaseDate']}

        },
        ReturnValues="UPDATED_NEW"
    )

    # If update is successful for post
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 200,
        }

    # Return 200 ok
    return response
