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
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################


import pytest
from unittest import mock
from requests import HTTPError
from tractusx_sdk.dataspace.tools.validate_submodels import submodel_schema_finder

@pytest.fixture
def valid_semantic_id():
    # Format: urn:samm:namespace:version#aspect
    return "urn:samm:io.catenax.batch:3.0.0#Batch"

def test_submodel_schema_finder_success(valid_semantic_id):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"type": "object"}

    with mock.patch("tractusx_sdk.dataspace.tools.validate_submodels.get", return_value=mock_response) as mock_get:
        result = submodel_schema_finder(valid_semantic_id)
        assert result["status"] == "ok"
        assert result["schema"] == {"type": "object"}
        assert "Submodel validation schema retrieved successfully" in result["message"]
        # Check correct URL construction
        expected_url = (
            "https://raw.githubusercontent.com/eclipse-tractusx/sldt-semantic-models/main/"
            "io.catenax.batch/3.0.0/gen/Batch-schema.json"
        )
        mock_get.assert_called_once_with(expected_url)

def test_submodel_schema_finder_invalid_semantic_id():
    # Missing version or aspect name
    invalid_id = "urn:samm:io.catenax.batch"
    with pytest.raises(HTTPError) as excinfo:
        submodel_schema_finder(invalid_id)
    assert "does not follow the correct structure" in str(excinfo.value)

def test_submodel_schema_finder_schema_not_found(valid_semantic_id):
    mock_response = mock.Mock()
    mock_response.status_code = 404

    with mock.patch("tractusx_sdk.dataspace.tools.validate_submodels.get", return_value=mock_response):
        with pytest.raises(HTTPError) as excinfo:
            submodel_schema_finder(valid_semantic_id)
        assert "Failed to obtain the required schema" in str(excinfo.value)

def test_submodel_schema_finder_invalid_json(valid_semantic_id):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = Exception("Invalid JSON")

    with mock.patch("tractusx_sdk.dataspace.tools.validate_submodels.get", return_value=mock_response):
        with pytest.raises(HTTPError) as excinfo:
            submodel_schema_finder(valid_semantic_id)
        assert "not a valid json" in str(excinfo.value)

def test_submodel_schema_finder_custom_link_core(valid_semantic_id):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"type": "object"}
    custom_link_core = "https://example.com/models/"

    with mock.patch("tractusx_sdk.dataspace.tools.validate_submodels.get", return_value=mock_response) as mock_get:
        submodel_schema_finder(valid_semantic_id, link_core=custom_link_core)
        expected_url = (
            "https://example.com/models/io.catenax.batch/3.0.0/gen/Batch-schema.json"
        )
        mock_get.assert_called_once_with(expected_url)
