"""
This Lambda functions deletes an existing book by isbn.
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
