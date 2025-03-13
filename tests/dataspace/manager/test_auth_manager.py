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

import unittest
from unittest.mock import Mock
from fastapi import Request
from starlette.datastructures import Headers
from tractusx_sdk.dataspace.managers.auth_manager import AuthManager

class TestAuthManager(unittest.TestCase):

    def setUp(self):
        """Set up default values for testing."""
        self.auth_manager = AuthManager(
            configured_api_key="test_key",
            api_key_header="X-Api-Key",
            auth_enabled=True
        )

    def test_auth_disabled_always_returns_true(self):
        """Test when authentication is disabled, it always returns True."""
        self.auth_manager.auth_enabled = False
        mock_request = Mock(spec=Request)
        self.assertTrue(self.auth_manager.is_authenticated(mock_request))

    def test_missing_api_key_header_returns_false(self):
        """Test when the API key header is missing, it returns False."""
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({})  # Empty headers
        self.assertFalse(self.auth_manager.is_authenticated(mock_request))

    def test_invalid_api_key_returns_false(self):
        """Test when an incorrect API key is provided, it returns False."""
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({"X-Api-Key": "wrong_key"})
        self.assertFalse(self.auth_manager.is_authenticated(mock_request))

    def test_valid_api_key_returns_true(self):
        """Test when the correct API key is provided, it returns True."""
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers({"X-Api-Key": "test_key"})
        self.assertTrue(self.auth_manager.is_authenticated(mock_request))


if __name__ == "__main__":
    unittest.main()
