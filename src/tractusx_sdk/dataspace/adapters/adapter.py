import requests
import urllib.parse
from io import BytesIO
from fastapi.responses import JSONResponse, Response


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
    def get_host(url):
        return Adapter.explode_url(url=url).netloc

    @staticmethod
    def explode_url(url):
        return urllib.parse.urlparse(url=url)

    @staticmethod
    def transform_response_into_json_response(data: dict, status_code: int = 200, headers: dict =None) -> JSONResponse:
        response = JSONResponse(
            content=data,
            status_code=status_code,
            headers=headers
        )
        response.headers["Content-Type"] = 'application/json'
        return response

    @staticmethod
    def transform_response_into_fastapi_response(response: requests.Response) -> Response:
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get('content-type', 'application/json')
        )

    @staticmethod
    def empty_response(status=204):
        return Response(status_code=status)

    @staticmethod
    def file_response(buffer: BytesIO, filename: str, status=200, content_type='application/pdf'):
        headers = {'Content-Disposition': f'inline; filename="{filename}"'}
        return Response(buffer.getvalue(), status_code=status, headers=headers, media_type=content_type)

    # Generates a error response with message
    @staticmethod
    def get_error_response(message="It was not possible to process/execute this request!", status=500):
        return Adapter.transform_response_into_json_response({
            "message": message,
            "status": status
        }, status)

    @staticmethod
    async def get_body(request):
        return await request.json()

    @staticmethod
    def get_not_authorized():
        return Adapter.transform_response_into_json_response({
            "message": "Not Authorized",
            "status": 401
        }, 401)

    @staticmethod
    def concat_into_url(*args):
        """
        Joins given arguments into an url. Trailing and leading slashes are stripped for each argument.

        :param args: The parts of a URL to be concatenated into one
        :return: Complete URL
        """

        return "/".join(map(lambda x: str(x).strip("/"), args))

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

        return self.transform_response_into_json_response(
            data=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
