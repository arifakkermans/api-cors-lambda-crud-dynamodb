"""
Models and helper functions.
"""

import json
import logging
import datetime

from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


class InvalidUsage(Exception):
    """
    Create custom HTTP responses.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None, logger=None):
        """
        Args:
            self: str representation
            message: str response body 
            status_code: int (optional)
            payload: 

        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.logger = logger or logging

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
    """
    DynamoDB json parser to load and dump strings of Dynamodb 
    format to a Python object.
    """

    def __init__(self, logger=None):
        self.logger = logger or logging

    def unmarshal_dynamodb_json(self, node):
        """
        Cast data to dict and unmarshal value.

         Args:
            node: str representation in DynamoDB json format  

        Returns:
            dict of the DynamoDB type
        """
        data = dict({})
        data['M'] = node
        return self.__unmarshal_value(data)

    def __unmarshal_value(self, node):
        """
        Cast data to dict and unmarshal value.

         Args:
            node: dict representation in DynamoDB json format

        Returns:
            parsed dict
        """
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


def validate_releasedate(date):
    year, month, day = date.split('-')
    valid = True
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        valid = False

    return valid


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()

@dataclass
class BookRequestBody:
    name: str
    isbn: str
    authors: str
    languages: str
    countries: str
    number_of_pages: int
    release_date: str

    @staticmethod
    def from_dict(obj: Any) -> 'BookRequestBody':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        isbn = from_str(obj.get("isbn"))
        authors = from_str(obj.get("authors"))
        languages = from_str(obj.get("languages"))
        countries = from_str(obj.get("countries"))
        number_of_pages = from_str(obj.get("numberOfPages"))
        release_date = from_str(obj.get("releaseDate"))
        return BookRequestBody(name, isbn, authors, languages, countries, number_of_pages, release_date)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["isbn"] = from_str(self.isbn)
        result["authors"] = from_str(self.authors)
        result["languages"] = from_str(self.languages)
        result["countries"] = from_str(self.countries)
        result["numberOfPages"] = from_str(str(self.number_of_pages))
        result["releaseDate"] = from_str(self.release_date)
        return result


def book_request_body_from_dict(s: Any) -> BookRequestBody:
    return BookRequestBody.from_dict(s)


def book_request_body_to_dict(x: BookRequestBody) -> Any:
    return to_class(BookRequestBody, x)
