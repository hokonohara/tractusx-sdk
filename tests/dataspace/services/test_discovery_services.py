#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################

import pytest
import time
from unittest import mock
from tractusx_sdk.dataspace.services.discovery.discovery_finder_service import DiscoveryFinderService, ConnectorDiscoveryService

@pytest.fixture
def mock_oauth():
    mock_oauth = mock.Mock()
    mock_oauth.connected = True
    mock_oauth.add_auth_header.side_effect = lambda headers: {**headers, "Authorization": "Bearer token"}
    return mock_oauth

@pytest.fixture
def connector_service(mock_oauth):
    with mock.patch.object(ConnectorDiscoveryService, '_get_or_update_discovery_url') as mock_update:
        mock_update.return_value = "https://connector-discovery.example.com"
        service = ConnectorDiscoveryService(
            oauth=mock_oauth,
            discovery_finder_url="https://discovery.example.com",
            connector_discovery_key="bpn",
            cache_timeout_seconds=10,
            endpoint_address_key="endpointAddress",
            types_key="types",
            endpoints_key="endpoints",
            return_type_key="type"
        )
        return service

class TestDiscoveryFinderService:
    
    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.HttpTools")
    def test_find_discovery_urls_success(self, mock_http, mock_oauth):
        """Test successful discovery URL finding."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "endpoints": [
                {"type": "bpn", "endpointAddress": "https://bpn-discovery.example.com"},
                {"type": "manufacturerPartId", "endpointAddress": "https://part-discovery.example.com"}
            ]
        }
        mock_http.do_post.return_value = mock_response
        
        result = DiscoveryFinderService.find_discovery_urls(
            url="https://discovery.example.com",
            oauth=mock_oauth,
            keys=["bpn", "manufacturerPartId"]
        )
        
        expected_body = {
            "types": ["bpn", "manufacturerPartId"]
        }
        
        mock_http.do_post.assert_called_once_with(
            url="https://discovery.example.com",
            headers={'Content-Type': 'application/json', "Authorization": "Bearer token"},
            json=expected_body
        )
        
        assert result == {
            "bpn": "https://bpn-discovery.example.com",
            "manufacturerPartId": "https://part-discovery.example.com"
        }

    def test_find_discovery_urls_not_connected(self, mock_oauth):
        """Test discovery URL finding when OAuth is not connected."""
        mock_oauth.connected = False
        
        with pytest.raises(ConnectionError, match="authentication service is not connected"):
            DiscoveryFinderService.find_discovery_urls(
                url="https://discovery.example.com",
                oauth=mock_oauth,
                keys=["bpn"]
            )

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.HttpTools")
    def test_find_discovery_urls_http_error(self, mock_http, mock_oauth):
        """Test discovery URL finding with HTTP error."""
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_http.do_post.return_value = mock_response
        
        with pytest.raises(Exception, match="response was not successful"):
            DiscoveryFinderService.find_discovery_urls(
                url="https://discovery.example.com",
                oauth=mock_oauth,
                keys=["bpn"]
            )

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.HttpTools")
    def test_find_discovery_urls_no_endpoints(self, mock_http, mock_oauth):
        """Test discovery URL finding when no endpoints are found."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"endpoints": []}
        mock_http.do_post.return_value = mock_response
        
        with pytest.raises(Exception, match="No endpoints were found"):
            DiscoveryFinderService.find_discovery_urls(
                url="https://discovery.example.com",
                oauth=mock_oauth,
                keys=["bpn"]
            )

class TestConnectorDiscoveryService:

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.DiscoveryFinderService")
    def test_get_connector_discovery_url_success(self, mock_finder, connector_service, mock_oauth):
        """Test successful connector discovery URL retrieval."""
        mock_finder.find_discovery_urls.return_value = {"bpn": "https://connector-discovery.example.com"}
        
        url = connector_service.get_connector_discovery_url(
            oauth=mock_oauth,
            discovery_finder_url="https://discovery.example.com",
            connector_discovery_key="bpn"
        )
        
        assert url == "https://connector-discovery.example.com"
        mock_finder.find_discovery_urls.assert_called_once_with(
            url="https://discovery.example.com",
            oauth=mock_oauth,
            keys=["bpn"],
            endpoint_address_key="endpointAddress",
            types_key="types",
            endpoints_key="endpoints",
            return_type_key="type"
        )

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.DiscoveryFinderService")
    def test_get_connector_discovery_url_not_found(self, mock_finder, connector_service, mock_oauth):
        """Test connector discovery URL retrieval when endpoint not found."""
        mock_finder.find_discovery_urls.return_value = {}
        
        with pytest.raises(Exception, match="Connector Discovery endpoint not found"):
            connector_service.get_connector_discovery_url(
                oauth=mock_oauth,
                discovery_finder_url="https://discovery.example.com",
                connector_discovery_key="bpn"
            )

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.HttpTools")
    def test_find_connector_by_bpn_success(self, mock_http, connector_service):
        """Test successful connector finding by BPN."""
        # Mock the discovery URL retrieval
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://connector-discovery.example.com",
                "timestamp": time.time()
            }
        }
        
        # Mock HTTP response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "bpn": "BPNL000000000001",
                "connectorEndpoint": [
                    "https://edc1.example.com/api/v1/dsp",
                    "https://edc2.example.com/api/v1/dsp"
                ]
            },
            {
                "bpn": "BPNL000000000002",
                "connectorEndpoint": [
                    "https://edc3.example.com/api/v1/dsp"
                ]
            }
        ]
        mock_http.do_post.return_value = mock_response
        
        result = connector_service.find_connector_by_bpn("BPNL000000000001")
        
        mock_http.do_post.assert_called_once_with(
            url="https://connector-discovery.example.com",
            headers={'Content-Type': 'application/json', "Authorization": "Bearer token"},
            json=["BPNL000000000001"]
        )
        
        assert result == [
            "https://edc1.example.com/api/v1/dsp",
            "https://edc2.example.com/api/v1/dsp"
        ]

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.HttpTools")
    def test_find_connector_by_bpn_not_found(self, mock_http, connector_service):
        """Test connector finding when BPN is not found."""
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://connector-discovery.example.com",
                "timestamp": time.time()
            }
        }
        
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "bpn": "BPNL000000000002",
                "connectorEndpoint": ["https://edc3.example.com/api/v1/dsp"]
            }
        ]
        mock_http.do_post.return_value = mock_response
        
        result = connector_service.find_connector_by_bpn("BPNL000000000001")
        
        assert result is None

    @mock.patch("tractusx_sdk.dataspace.services.discovery.discovery_services.HttpTools")
    def test_find_connector_by_bpn_http_error(self, mock_http, connector_service):
        """Test connector finding with HTTP error."""
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://connector-discovery.example.com",
                "timestamp": time.time()
            }
        }
        
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_http.do_post.return_value = mock_response
        
        with pytest.raises(Exception, match="response was not successful"):
            connector_service.find_connector_by_bpn("BPNL000000000001")

    def test_cache_functionality_expired(self, connector_service, mock_oauth):
        """Test cache functionality with expired entries."""
        # Set up initial cache entry that's expired
        old_timestamp = time.time() - 20  # 20 seconds ago, cache timeout is 10 seconds
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://old-connector-discovery.example.com",
                "timestamp": old_timestamp
            }
        }
        
        with mock.patch.object(connector_service, 'get_connector_discovery_url') as mock_get_url:
            mock_get_url.return_value = "https://new-connector-discovery.example.com"
            
            url = connector_service._get_or_update_discovery_url()
            
            # Should call get_connector_discovery_url because cache is expired
            mock_get_url.assert_called_once()
            assert url == "https://new-connector-discovery.example.com"
            
            # Cache should be updated
            assert connector_service.discovery_cache["bpn"]["url"] == "https://new-connector-discovery.example.com"

    def test_cache_functionality_valid(self, connector_service):
        """Test cache functionality with valid entries."""
        # Set up valid cache entry
        current_timestamp = time.time()
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://cached-connector-discovery.example.com",
                "timestamp": current_timestamp
            }
        }
        
        with mock.patch.object(connector_service, 'get_connector_discovery_url') as mock_get_url:
            url = connector_service._get_or_update_discovery_url()
            
            # Should not call get_connector_discovery_url because cache is valid
            mock_get_url.assert_not_called()
            assert url == "https://cached-connector-discovery.example.com"

    def test_initialization_with_custom_parameters(self, mock_oauth):
        """Test service initialization with custom parameters."""
        with mock.patch.object(ConnectorDiscoveryService, '_get_or_update_discovery_url') as mock_update:
            mock_update.return_value = "https://custom-discovery.example.com"
            
            service = ConnectorDiscoveryService(
                oauth=mock_oauth,
                discovery_finder_url="https://custom-discovery-finder.example.com",
                connector_discovery_key="customKey",
                cache_timeout_seconds=3600,  # 1 hour
                endpoint_address_key="customEndpointKey",
                types_key="customTypesKey",
                endpoints_key="customEndpointsKey",
                return_type_key="customReturnTypeKey"
            )
            
            assert service.discovery_finder_url == "https://custom-discovery-finder.example.com"
            assert service.connector_discovery_key == "customKey"
            assert service.cache_timeout_seconds == 3600
            assert service.endpoint_address_key == "customEndpointKey"
            assert service.types_key == "customTypesKey"
            assert service.endpoints_key == "customEndpointsKey"
            assert service.return_type_key == "customReturnTypeKey"

    def test_cache_safety_mechanism_with_existing_cache(self, connector_service, mock_oauth):
        """Test safety mechanism when refresh fails but cached URL exists."""
        # Set up expired cache entry
        old_timestamp = time.time() - 20  # 20 seconds ago, cache timeout is 10 seconds
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://cached-connector-discovery.example.com",
                "timestamp": old_timestamp
            }
        }
        
        with mock.patch.object(connector_service, 'get_connector_discovery_url') as mock_get_url:
            # Simulate connection failure during refresh
            mock_get_url.side_effect = ConnectionError("Connection timeout")
            
            # Should return cached URL despite refresh failure
            url = connector_service._get_or_update_discovery_url()
            
            # Should have attempted to refresh
            mock_get_url.assert_called_once()
            # Should return the cached URL as fallback
            assert url == "https://cached-connector-discovery.example.com"
            # Cache should still contain the old entry (not deleted)
            assert "bpn" in connector_service.discovery_cache
            assert connector_service.discovery_cache["bpn"]["url"] == "https://cached-connector-discovery.example.com"

    def test_cache_safety_mechanism_no_existing_cache(self, connector_service):
        """Test safety mechanism when refresh fails and no cached URL exists."""
        # No existing cache
        connector_service.discovery_cache = {}
        
        with mock.patch.object(connector_service, 'get_connector_discovery_url') as mock_get_url:
            # Simulate connection failure during initial discovery
            mock_get_url.side_effect = ConnectionError("Connection timeout")
            
            # Should raise the original exception since no fallback exists
            with pytest.raises(ConnectionError, match="Connection timeout"):
                connector_service._get_or_update_discovery_url()
            
            # Should have attempted to get URL
            mock_get_url.assert_called_once()
            # Cache should remain empty
            assert "bpn" not in connector_service.discovery_cache

    def test_cache_successful_refresh_after_failure(self, connector_service):
        """Test that cache is properly updated when refresh succeeds after previous failure."""
        # Set up expired cache entry
        old_timestamp = time.time() - 20
        connector_service.discovery_cache = {
            "bpn": {
                "url": "https://old-cached-connector-discovery.example.com",
                "timestamp": old_timestamp
            }
        }
        
        with mock.patch.object(connector_service, 'get_connector_discovery_url') as mock_get_url:
            # First call fails, should return cached URL
            mock_get_url.side_effect = ConnectionError("Connection timeout")
            url1 = connector_service._get_or_update_discovery_url()
            assert url1 == "https://old-cached-connector-discovery.example.com"
            
            # Second call succeeds, should update cache
            mock_get_url.side_effect = None
            mock_get_url.return_value = "https://new-refreshed-connector-discovery.example.com"
            
            # Force cache expiration for next call
            connector_service.discovery_cache["bpn"]["timestamp"] = time.time() - 30
            
            url2 = connector_service._get_or_update_discovery_url()
            assert url2 == "https://new-refreshed-connector-discovery.example.com"
            
            # Cache should be updated with new URL and timestamp
            assert connector_service.discovery_cache["bpn"]["url"] == "https://new-refreshed-connector-discovery.example.com"
            assert connector_service.discovery_cache["bpn"]["timestamp"] > old_timestamp
