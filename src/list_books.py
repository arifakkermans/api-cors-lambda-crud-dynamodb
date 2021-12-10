"""
This Lambda functions returns all books in the DB.
"""
import json
import logging
import os

import boto3


def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
