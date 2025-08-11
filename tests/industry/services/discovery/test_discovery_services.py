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
from tractusx_sdk.industry.services.discovery.bpn_discovery_service import BpnDiscoveryService

@pytest.fixture
def mock_oauth():
    mock_oauth = mock.Mock()
    mock_oauth.add_auth_header.side_effect = lambda headers: {**headers, "Authorization": "Bearer token"}
    return mock_oauth

@pytest.fixture
def service(mock_oauth):
    return BpnDiscoveryService(
        oauth=mock_oauth,
        discovery_finder_url="https://discovery.example.com",
        cache_timeout_seconds=10,
        endpoint_address_key="endpointAddress",
        types_key="types",
        endpoints_key="endpoints",
        return_type_key="type"
    )

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.DiscoveryFinderService")
def test_get_bpn_discovery_url_success(mock_finder, service, mock_oauth):
    """Test successful BPN discovery URL retrieval."""
    mock_finder.find_discovery_urls.return_value = {"manufacturerPartId": "https://bpn.example.com"}
    url = service.get_bpn_discovery_url(mock_oauth, "https://discovery.example.com")
    assert url == "https://bpn.example.com"
    mock_finder.find_discovery_urls.assert_called_once_with(
        url="https://discovery.example.com",
        oauth=mock_oauth,
        keys=["manufacturerPartId"],
        types_key="types",
        endpoints_key="endpoints",
        endpoint_address_key="endpointAddress",
        return_type_key="type"
    )

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.DiscoveryFinderService")
def test_get_bpn_discovery_url_not_found(mock_finder, service, mock_oauth):
    """Test BPN discovery URL retrieval when endpoint not found."""
    mock_finder.find_discovery_urls.return_value = {}
    with pytest.raises(Exception, match="Connector Discovery endpoint not found"):
        service.get_bpn_discovery_url(mock_oauth, "https://discovery.example.com")

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
def test_search_bpns_success(mock_http, service):
    """Test successful BPN search."""
    # Mock the discovery URL retrieval
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://bpn.example.com",
            "timestamp": time.time()
        }
    }
    
    # Mock HTTP response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "bpns": [
            {"value": "BPNL000000000001"},
            {"value": "BPNL000000000002"}
        ]
    }
    mock_http.do_post_with_session.return_value = mock_response
    
    result = service.search_bpns(keys=["part123", "part456"])
    
    expected_body = {
        "searchFilter": [
            {
                "type": "manufacturerPartId",
                "keys": ["part123", "part456"]
            }
        ]
    }
    
    mock_http.do_post_with_session.assert_called_once_with(
        url="https://bpn.example.com",
        headers={'Content-Type': 'application/json', "Authorization": "Bearer token"},
        json=expected_body,
        session=service.session
    )
    
    assert result == {
        "bpns": [
            {"value": "BPNL000000000001"},
            {"value": "BPNL000000000002"}
        ]
    }

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
def test_search_bpns_unauthorized(mock_http, service):
    """Test BPN search with unauthorized response."""
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://bpn.example.com",
            "timestamp": time.time()
        }
    }
    
    mock_response = mock.Mock()
    mock_response.status_code = 401
    mock_http.do_post_with_session.return_value = mock_response
    
    with pytest.raises(Exception, match="Unauthorized access"):
        service.search_bpns(keys=["part123"])

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
def test_search_bpns_no_response(mock_http, service):
    """Test BPN search with no response."""
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://bpn.example.com",
            "timestamp": time.time()
        }
    }
    
    mock_http.do_post_with_session.return_value = None
    
    with pytest.raises(Exception, match="No response received"):
        service.search_bpns(keys=["part123"])

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.op")
def test_find_bpns_success(mock_op, service):
    """Test successful BPN finding."""
    # Mock search_bpns method
    service.search_bpns = mock.Mock(return_value={
        "bpns": [
            {"value": "BPNL000000000001"},
            {"value": "BPNL000000000002"},
            {"value": "BPNL000000000001"}  # Duplicate
        ]
    })
    
    mock_op.extract_dict_values.return_value = ["BPNL000000000001", "BPNL000000000002", "BPNL000000000001"]
    
    result = service.find_bpns(keys=["part123", "part456"])
    
    service.search_bpns.assert_called_once_with(keys=["part123", "part456"], identifier_type="manufacturerPartId")
    mock_op.extract_dict_values.assert_called_once_with(
        array=[
            {"value": "BPNL000000000001"},
            {"value": "BPNL000000000002"},
            {"value": "BPNL000000000001"}
        ],
        key="value"
    )
    
    # Should return unique BPNs
    assert set(result) == {"BPNL000000000001", "BPNL000000000002"}

def test_find_bpns_no_results(service):
    """Test BPN finding with no results."""
    service.search_bpns = mock.Mock(return_value={"bpns": []})
    
    result = service.find_bpns(keys=["nonexistent"])
    
    assert result is None

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
def test_set_identifier_success(mock_http, service):
    """Test successful identifier setting."""
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://bpn.example.com",
            "timestamp": time.time()
        }
    }
    
    mock_response = mock.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"resourceId": "12345", "key": "part123"}
    mock_http.do_post_with_session.return_value = mock_response
    
    result = service.set_identifier("part123")
    
    expected_body = {
        "type": "manufacturerPartId",
        "key": "part123"
    }
    
    mock_http.do_post_with_session.assert_called_once_with(
        url="https://bpn.example.com",
        headers={'Content-Type': 'application/json', "Authorization": "Bearer token"},
        json=expected_body,
        session=service.session
    )
    
    assert result == {"resourceId": "12345", "key": "part123"}

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
def test_set_multiple_identifiers_success(mock_http, service):
    """Test successful multiple identifiers setting."""
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://bpn.example.com",
            "timestamp": time.time()
        }
    }
    
    mock_response = mock.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = [
        {"resourceId": "12345", "key": "part123"},
        {"resourceId": "12346", "key": "part456"}
    ]
    mock_http.do_post_with_session.return_value = mock_response
    
    result = service.set_multiple_identifiers(["part123", "part456"])
    
    expected_body = [
        {"type": "manufacturerPartId", "key": "part123"},
        {"type": "manufacturerPartId", "key": "part456"}
    ]
    
    mock_http.do_post_with_session.assert_called_once_with(
        url="https://bpn.example.com/batch",
        headers={'Content-Type': 'application/json', "Authorization": "Bearer token"},
        json=expected_body,
        session=service.session
    )
    
    assert len(result) == 2

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
def test_delete_bpn_identifier_success(mock_http, service):
    """Test successful BPN identifier deletion."""
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://bpn.example.com",
            "timestamp": time.time()
        }
    }
    
    mock_response = mock.Mock()
    mock_response.status_code = 204
    mock_http.do_delete_with_session.return_value = mock_response
    
    # Should not raise an exception
    service.delete_bpn_identifier_by_id("12345")
    
    mock_http.do_delete_with_session.assert_called_once_with(
        url="https://bpn.example.com/12345",
        headers={'Content-Type': 'application/json', "Authorization": "Bearer token"},
        session=service.session
    )

def test_cache_functionality(service, mock_oauth):
    """Test cache functionality with expired entries."""
    # Set up initial cache entry that's expired
    old_timestamp = time.time() - 20  # 20 seconds ago, cache timeout is 10 seconds
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://old-bpn.example.com",
            "timestamp": old_timestamp
        }
    }
    
    with mock.patch.object(service, 'get_bpn_discovery_url') as mock_get_url:
        mock_get_url.return_value = "https://new-bpn.example.com"
        
        url = service._get_or_update_discovery_url()
        
        # Should call get_bpn_discovery_url because cache is expired
        mock_get_url.assert_called_once()
        assert url == "https://new-bpn.example.com"
        
        # Cache should be updated
        assert service.bpn_discoveries["manufacturerPartId"]["url"] == "https://new-bpn.example.com"

def test_cache_valid_entry(service):
    """Test cache functionality with valid entries."""
    # Set up valid cache entry
    current_timestamp = time.time()
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://cached-bpn.example.com",
            "timestamp": current_timestamp
        }
    }
    
    with mock.patch.object(service, 'get_bpn_discovery_url') as mock_get_url:
        url = service._get_or_update_discovery_url()
        
        # Should not call get_bpn_discovery_url because cache is valid
        mock_get_url.assert_not_called()
        assert url == "https://cached-bpn.example.com"

def test_cache_safety_mechanism_with_existing_cache(service, mock_oauth):
    """Test safety mechanism when refresh fails but cached URL exists."""
    # Set up expired cache entry
    old_timestamp = time.time() - 20  # 20 seconds ago, cache timeout is 10 seconds
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://cached-bpn.example.com",
            "timestamp": old_timestamp
        }
    }
    
    with mock.patch.object(service, 'get_bpn_discovery_url') as mock_get_url:
        # Simulate connection failure during refresh
        mock_get_url.side_effect = ConnectionError("Connection timeout")
        
        # Should return cached URL despite refresh failure
        url = service._get_or_update_discovery_url()
        
        # Should have attempted to refresh
        mock_get_url.assert_called_once()
        # Should return the cached URL as fallback
        assert url == "https://cached-bpn.example.com"
        # Cache should still contain the old entry (not deleted)
        assert "manufacturerPartId" in service.bpn_discoveries
        assert service.bpn_discoveries["manufacturerPartId"]["url"] == "https://cached-bpn.example.com"

def test_cache_safety_mechanism_no_existing_cache(service):
    """Test safety mechanism when refresh fails and no cached URL exists."""
    # No existing cache
    service.bpn_discoveries = {}
    
    with mock.patch.object(service, 'get_bpn_discovery_url') as mock_get_url:
        # Simulate connection failure during initial discovery
        mock_get_url.side_effect = ConnectionError("Connection timeout")
        
        # Should raise the original exception since no fallback exists
        with pytest.raises(ConnectionError, match="Connection timeout"):
            service._get_or_update_discovery_url()
        
        # Should have attempted to get URL
        mock_get_url.assert_called_once()
        # Cache should remain empty
        assert "manufacturerPartId" not in service.bpn_discoveries

def test_cache_successful_refresh_after_failure(service):
    """Test that cache is properly updated when refresh succeeds after previous failure."""
    # Set up expired cache entry
    old_timestamp = time.time() - 20
    service.bpn_discoveries = {
        "manufacturerPartId": {
            "url": "https://old-cached-bpn.example.com",
            "timestamp": old_timestamp
        }
    }
    
    with mock.patch.object(service, 'get_bpn_discovery_url') as mock_get_url:
        # First call fails, should return cached URL
        mock_get_url.side_effect = ConnectionError("Connection timeout")
        url1 = service._get_or_update_discovery_url()
        assert url1 == "https://old-cached-bpn.example.com"
        
        # Second call succeeds, should update cache
        mock_get_url.side_effect = None
        mock_get_url.return_value = "https://new-refreshed-bpn.example.com"
        
        # Force cache expiration for next call
        service.bpn_discoveries["manufacturerPartId"]["timestamp"] = time.time() - 30
        
        url2 = service._get_or_update_discovery_url()
        assert url2 == "https://new-refreshed-bpn.example.com"
        
        # Cache should be updated with new URL and timestamp
        assert service.bpn_discoveries["manufacturerPartId"]["url"] == "https://new-refreshed-bpn.example.com"
        assert service.bpn_discoveries["manufacturerPartId"]["timestamp"] > old_timestamp
