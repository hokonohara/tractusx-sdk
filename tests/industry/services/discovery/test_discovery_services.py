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
from unittest import mock
from tractusx_sdk.industry.services.discovery.discovery_services import BpnDiscoveryService

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
        cache_timeout_seconds=10
    )

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.DiscoveryFinderService")
def test_get_connector_discovery_url_success(mock_finder, service, mock_oauth):
    mock_finder.find_discovery_urls.return_value = {"manufacturerPartId": "https://bpn.example.com"}
    url = service.get_connector_discovery_url(mock_oauth, "https://discovery.example.com")
    assert url == "https://bpn.example.com"

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.DiscoveryFinderService")
def test_get_connector_discovery_url_not_found(mock_finder, service, mock_oauth):
    mock_finder.find_discovery_urls.return_value = {}
    with pytest.raises(Exception, match="Connector Discovery endpoint not found"):
        service.get_connector_discovery_url(mock_oauth, "https://discovery.example.com")
