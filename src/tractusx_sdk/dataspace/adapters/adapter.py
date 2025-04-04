import requests

from fastapi.responses import JSONResponse
from src.tractusx_sdk.dataspace.tools import HttpTools


class Adapter:
    """
    Base adapter class
    """

    base_url: str = ""
    session = None

    def __init__(
            self,
            base_url: str,
            headers: dict = None
    ):
        """
        Create a new adapter instance

        :param base_url: The URL of the application to be requested
        :param headers: The headers (i.e.: API Key) of the application to be requested
        """

        self.base_url = base_url
        self.session = requests.Session()

        if headers:
            self.session.headers.update(headers)

    @staticmethod
    def concat_into_url(*args):
        """
        Joins given arguments into an url. Trailing and leading slashes are stripped for each argument.

        :param args: The parts of a URL to be concatenated into one
        :return: Complete URL
        """

        return "/".join(map(lambda x: str(x).strip("/"), args))

    @staticmethod
    def json_response(data, status_code: int = 200, headers: dict = None):
        response = JSONResponse(
            content=data,
            status_code=status_code,
            headers=headers
        )
        response.headers["Content-Type"] = 'application/json'
        return response

    def close(self):
        """
        Close the requests session
        """

        self.session.close()

    def get(self, url: str, **kwargs):
        """
        Perform a GET request

        :param url: Partial URL to append to the base adapter URL
        :param kwargs: Keyword arguments to include in the request

        :return: The response of the request
        """

        return self.request("get", url, **kwargs)

    def post(self, url: str, **kwargs):
        """
        Perform a POST request

        :param url: Partial URL to append to the base adapter URL
        :param kwargs: Keyword arguments to include in the request

        :return: The response of the request
        """

        return self.request("post", url, **kwargs)

    def put(self, url: str, **kwargs):
        """
        Perform a PUT request

        :param url: Partial URL to append to the base adapter URL
        :param kwargs: Keyword arguments to include in the request

        :return: The response of the request
        """

        return self.request("put", url, **kwargs)

    def delete(self, url: str, **kwargs):
        """
        Perform a DELETE request

        :param url: Partial URL to append to the base adapter URL
        :param kwargs: Keyword arguments to include in the request

        :return: The response of the request
        """

        return self.request("delete", url, **kwargs)

    def request(self, method: str, url: str, **kwargs):
        """
        Main method for performing requests

        :param method: HTTP method to use with requests
        :param url: Partial URL to append to the base adapter URL
        :param kwargs: Keyword arguments to include in the request

        :return: The response of the request
        """

        url = self.concat_into_url(self.base_url, url)

        response = self.session.request(
            method=method,
            url=url,
            **kwargs
        )

        return Adapter.json_response(
            data=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
