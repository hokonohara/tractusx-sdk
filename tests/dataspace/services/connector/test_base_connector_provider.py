#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 LKS NEXT
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
from tractusx_sdk.dataspace.connector import BaseConnectorProviderService

@pytest.fixture
def mock_base_connector_service():
    mock_service = mock.Mock()
    mock_assets = mock_service.provider.assets
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}
    mock_assets.create.return_value = mock_response
    return mock_service

@pytest.fixture
def mock_logger():
    return mock.Mock()

@pytest.fixture
def mock_model_factory(monkeypatch):
    mock_factory = mock.Mock()
    monkeypatch.setattr(dataspace_shortcuts.ModelFactory, "get_asset_model", mock_factory)
    return mock_factory

@pytest.fixture
def mock_contract_definitions(mock_base_connector_service):
    mock_contract_defs = mock_base_connector_service.provider.contract_definitions
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"contract": "created"}
    mock_contract_defs.create.return_value = mock_response
    return mock_contract_defs

@pytest.fixture
def mock_contract_model_factory(monkeypatch):
    mock_factory = mock.Mock()
    monkeypatch.setattr(dataspace_shortcuts.ModelFactory, "get_contract_definition_model", mock_factory)
    return mock_factory

@pytest.fixture
def mock_policies(mock_base_connector_service):
    mock_policies = mock_base_connector_service.provider.policies
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"policy": "created"}
    mock_policies.create.return_value = mock_response
    return mock_policies

@pytest.fixture
def mock_policy_model_factory(monkeypatch):
    mock_factory = mock.Mock()
    monkeypatch.setattr(dataspace_shortcuts.ModelFactory, "get_policy_model", mock_factory)
    return mock_factory

def test_create_asset_success(
    mock_base_connector_service, mock_logger, mock_model_factory
):
    asset_id = "asset-123"
    base_url = "http://example.com"
    dct_type = "test-type"
    version = "1.0"
    semantic_id = "sem-id"
    proxy_params = {"proxyQueryParams": "true"}
    headers = {"Authorization": "Bearer token"}
    private_properties = {"foo": "bar"}
    connector_version = "jupiter"

    mock_model_factory.return_value = {"mock": "asset"}

    result = dataspace_shortcuts.create_asset(
        asset_id=asset_id,
        base_url=base_url,
        dct_type=dct_type,
        version=version,
        semantic_id=semantic_id,
        proxy_params=proxy_params,
        headers=headers,
        private_properties=private_properties,
        connector_version=connector_version,
        base_connector_service=mock_base_connector_service,
        logger=mock_logger,
    )

    # ModelFactory.get_asset_model called with correct args
    mock_model_factory.assert_called_once()
    # Asset creation called
    mock_base_connector_service.provider.assets.create.assert_called_once_with(obj={"mock": "asset"})
    # Returns correct response
    assert result == {"result": "success"}

def test_create_asset_failure_logs_and_raises(
    mock_base_connector_service, mock_logger, mock_model_factory
):
    # Simulate failed response
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_base_connector_service.provider.assets.create.return_value = mock_response
    mock_model_factory.return_value = {"mock": "asset"}

    with pytest.raises(ValueError) as exc:
        dataspace_shortcuts.create_asset(
            asset_id="fail-asset",
            base_url="http://fail.com",
            dct_type="fail-type",
            base_connector_service=mock_base_connector_service,
            logger=mock_logger,
        )
    assert "Failed to create asset" in str(exc.value)
    mock_logger.error.assert_called_once_with("Bad Request")

def test_create_asset_with_minimal_args(
    mock_base_connector_service, mock_logger, mock_model_factory
):
    mock_model_factory.return_value = {"mock": "asset"}
    result = dataspace_shortcuts.create_asset(
        asset_id="minimal",
        base_url="http://minimal.com",
        dct_type="minimal-type",
        base_connector_service=mock_base_connector_service,
        logger=mock_logger,
    )
    assert result == {"result": "success"}
    mock_model_factory.assert_called_once()
    mock_base_connector_service.provider.assets.create.assert_called_once()

def test_create_asset_with_headers_and_proxy_params(
    mock_base_connector_service, mock_logger, mock_model_factory
):
    mock_model_factory.return_value = {"mock": "asset"}
    headers = {"X-Test": "value"}
    proxy_params = {"proxyPath": "false"}
    dataspace_shortcuts.create_asset(
        asset_id="header-proxy",
        base_url="http://header.com",
        dct_type="header-type",
        headers=headers,
        proxy_params=proxy_params,
        base_connector_service=mock_base_connector_service,
        logger=mock_logger,
    )
    # Check that ModelFactory.get_asset_model received a data_address with header and proxy params
    _, kwargs = mock_model_factory.call_args
    data_address = kwargs["data_address"]
    assert data_address["header:X-Test"] == "value"
    assert data_address["proxyPath"] == "false"

def test_create_contract_success(
    mock_base_connector_service, mock_logger, mock_contract_model_factory, mock_contract_definitions
):
    contract_id = "contract-1"
    usage_policy_id = "usage-1"
    access_policy_id = "access-1"
    asset_id = "asset-1"
    connector_version = "jupiter"
    mock_contract_model_factory.return_value = {"mock": "contract"}

    result = dataspace_shortcuts.create_contract(
        contract_id=contract_id,
        usage_policy_id=usage_policy_id,
        access_policy_id=access_policy_id,
        asset_id=asset_id,
        connector_version=connector_version,
        base_connector_service=mock_base_connector_service,
        logger=mock_logger,
    )

    mock_contract_model_factory.assert_called_once_with(
        context={"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
        connector_version=connector_version,
        oid=contract_id,
        assets_selector=[
            {
                "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
                "operator": "=",
                "operandRight": asset_id
            }
        ],
        contract_policy_id=usage_policy_id,
        access_policy_id=access_policy_id
    )
    mock_logger.info.assert_any_call(f"Creating new contract with ID {contract_id}.")
    mock_logger.info.assert_any_call(f"Contract {contract_id} created successfully.")
    mock_base_connector_service.provider.contract_definitions.create.assert_called_once_with(obj={"mock": "contract"})
    assert result == {"contract": "created"}

def test_create_contract_failure_raises(
    mock_base_connector_service, mock_logger, mock_contract_model_factory, mock_contract_definitions
):
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "bad request"}
    mock_base_connector_service.provider.contract_definitions.create.return_value = mock_response
    mock_contract_model_factory.return_value = {"mock": "contract"}

    with pytest.raises(ValueError) as exc:
        dataspace_shortcuts.create_contract(
            contract_id="fail-contract",
            usage_policy_id="fail-usage",
            access_policy_id="fail-access",
            asset_id="fail-asset",
            base_connector_service=mock_base_connector_service,
            logger=mock_logger,
        )
    assert "Failed to create contract" in str(exc.value)

def test_create_policy_success(
    mock_base_connector_service, mock_logger, mock_policy_model_factory, mock_policies
):
    policy_id = "policy-1"
    context = {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"}
    permissions = [{"action": "USE"}]
    prohibitions = []
    obligations = []
    connector_version = "jupiter"
    mock_policy_model_factory.return_value = {"mock": "policy"}

    result = dataspace_shortcuts.create_policy(
        policy_id=policy_id,
        context=context,
        permissions=permissions,
        prohibitions=prohibitions,
        obligations=obligations,
        connector_version=connector_version,
        base_connector_service=mock_base_connector_service,
        logger=mock_logger,
    )

    mock_policy_model_factory.assert_called_once_with(
        connector_version=connector_version,
        oid=policy_id,
        context=context,
        permissions=permissions,
        prohibitions=prohibitions,
        obligations=obligations
    )
    mock_logger.info.assert_any_call(f"Creating new policy with ID {policy_id}.")
    mock_logger.info.assert_any_call(f"Policy {policy_id} created successfully.")
    mock_base_connector_service.provider.policies.create.assert_called_once_with(obj={"mock": "policy"})
    assert result == {"policy": "created"}

def test_create_policy_failure_raises(
    mock_base_connector_service, mock_logger, mock_policy_model_factory, mock_policies
):
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "bad request"}
    mock_base_connector_service.policies.create.return_value = mock_response
    mock_policy_model_factory.return_value = {"mock": "policy"}

    with pytest.raises(ValueError) as exc:
        dataspace_shortcuts.create_policy(
            policy_id="fail-policy",
            context={},
            permissions=[],
            prohibitions=[],
            obligations=[],
            base_connector_service=mock_base_connector_service,
            logger=mock_logger,
        )
    assert "Failed to create policy" in str(exc.value)

def test_create_policy_with_minimal_args(
    mock_base_connector_service, mock_logger, mock_policy_model_factory, mock_policies
):
    mock_policy_model_factory.return_value = {"mock": "policy"}
    result = dataspace_shortcuts.create_policy(
        policy_id="minimal-policy",
        base_connector_service=mock_base_connector_service,
        logger=mock_logger,
    )
    assert result == {"policy": "created"}
    mock_policy_model_factory.assert_called_once()
    mock_base_connector_service.provider.policies.create.assert_called_once()
