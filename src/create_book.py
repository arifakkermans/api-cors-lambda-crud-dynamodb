"""
This Lambda function creates a new book.
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
    logger.info("Looking for events")
    logger.info("- - - - - - - - - - - - - - - - - - -")
    logger.info(f'Incoming request is: {event}')

    # Set the default error response
    response = {
        "statusCode": 500,
        "body": "An error occured while creating the book."
    }

    # Validate if query parameter is not empty
    if event['pathParameters'] is None:
        validation_error = models.InvalidUsage(
            message="no query param provided").create_response_body()

        return validation_error

    # Validate if body is not empty
    if event['body'] is None:
        validation_error = models.InvalidUsage(
            message="no request body provided").create_response_body()
        return validation_error
    
    book_str = event['body']
    book = json.loads(book_str)
    isbn = book['isbn']

    # Validate if isbn consists of 13 digits
    if len(isbn) != 13 or not isbn.isdigit():
        validation_error = models.InvalidUsage(
            message=f"invalid isbn {isbn} must be a 13char digit"
        ).create_response_body()
        return validation_error

    res = dynamodb_client.put_item(
        TableName=TABLE_NAME,
        Item={
            "isbn": {"S": book['isbn']},
            "authors": {"S": book['authors']},
            "languages": {"S": book['languages']},
            "countries": {"S": book['countries']},
            "number_of_pages": {"S": book['numberOfPages']},
            "release_date": {"S": book['releaseDate']}
        }
    )

    # If creation is successful
    if res['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = {
            "statusCode": 201,
            "body": f"Location: /books/{book['isbn']}"
        }

    # Return 201 created with the location of the book
    return response
