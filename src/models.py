"""
Models and helper functions.
"""

import json

class InvalidUsage(Exception):
    """
    Create custom HTTP responses.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """
        Constructor.

        Args:
            self: str representation
            message: str 
            status_code: int (optional)
            payload: 

        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def create_response_body(self):
        """
        Create a custom response body.

        Args:
            self: str representation

        Returns:
            JSON with HTTP status code and a custom message
        """
        rb = {
            "statusCode": self.status_code,
            "body": json.dumps({"Reason": self.message}),
            "headers": {"Content-Type": "application/json"},
        }
        return rb
