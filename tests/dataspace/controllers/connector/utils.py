from src.tractusx_sdk.dataspace.adapters.adapter import Adapter
from src.tractusx_sdk.dataspace.controllers.connector.decorators import controller_method
from src.tractusx_sdk.dataspace.controllers.controller import Controller

ENDPOINT_URL = "/some/endpoint"


def generic_controller_setup(obj) -> None:
    obj.adapter = Adapter("https://example.com")
    obj.endpoint_url = ENDPOINT_URL

    return obj


class SampleController(Controller):
    """
    A very basic, template-like class inheriting Controller
    """

    endpoint_url = ENDPOINT_URL

    @controller_method
    def func(self):
        return "Hello world!"


class ControllerPropertiesMixin:
    adapter = None
    endpoint_url = None
