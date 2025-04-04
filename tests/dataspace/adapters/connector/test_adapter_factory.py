import unittest
from enum import Enum
from unittest.mock import patch
from src.tractusx_sdk.dataspace.adapters.connector.adapter_factory import AdapterFactory, AdapterType


class TestAdapterFactory(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://example.com"
        self.headers = {"Authorization": "Bearer token"}
        self.dma_path = "/dma"

    def test_get_dma_adapter_success(self):
        adapter = AdapterFactory.get_dma_adapter(
            connector_version="v0_9_0",
            base_url=self.base_url,
            dma_path=self.dma_path,
            headers=self.headers
        )
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.base_url, f"{self.base_url}{self.dma_path}")
        self.assertIsNotNone(adapter.session)

    def test_get_adapter_unsupported_version(self):
        with self.assertRaises(ValueError):
            AdapterFactory.get_dma_adapter(
                connector_version="NonExistentVersion",
                base_url=self.base_url,
                dma_path=self.dma_path,
                headers=self.headers
            )

    def test_get_adapter_unsupported_type(self):
        with self.assertRaises(ImportError):
            adapter_type = Enum('AdapterType', { 'foo': 'bar' })
            AdapterFactory._get_adapter(
                adapter_type=adapter_type.foo,
                connector_version="v0_9_0",
                base_url=self.base_url,
                dma_path=self.dma_path,
                headers=self.headers
            )

    def test_get_adapter_import_error(self):
        with patch.object(AdapterFactory, "SUPPORTED_VERSIONS", new=["v0_0_0"]):
            with self.assertRaises(ImportError):
                AdapterFactory._get_adapter(
                    adapter_type=AdapterType.DMA_ADAPTER,
                    connector_version="v0_0_0",
                    base_url=self.base_url,
                    headers=self.headers
                )
