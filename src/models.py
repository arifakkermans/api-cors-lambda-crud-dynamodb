"""
Models and helper functions.
"""

import json
import logging

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

class DynamoParser:
    def __init__(self,logger=None):
        self.logger = logger or logging

    def unmarshal_dynamodb_json(self, node):
        data = dict({})
        data['M'] = node
        return self.__unmarshal_value(data)
    
    def __unmarshal_value(self, node):
        if type(node) is not dict:
            return node
    
        for key, value in node.items():
            # S – String - return string
            # N – Number - return int or float (if includes '.')
            # B – Binary - not handled
            # BOOL – Boolean - return Bool
            # NULL – Null - return None
            # M – Map - return a dict
            # L – List - return a list
            # SS – String Set - not handled
            # NN – Number Set - not handled
            # BB – Binary Set - not handled
            key = key.lower()
            if key == 'bool':
                return value
            if key == 'null':
                return None
            if key == 's':
                return value
            if key == 'n':
                if '.' in str(value):
                    return float(value)
                return int(value)
            if key in ['m', 'l']:
                if key == 'm':
                    data = {}
                    for key1, value1 in value.items():
                        if key1.lower() == 'l':
                            data = [self.__unmarshal_value(n) for n in value1]
                        else:
                            if type(value1) is not dict:
                                return self.__unmarshal_value(value)
                            data[key1] = self.__unmarshal_value(value1)
                    return data
                data = []
                for item in value:
                    data.append(self.__unmarshal_value(item))
                return data