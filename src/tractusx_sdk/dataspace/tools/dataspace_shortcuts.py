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

## Code originally beloging to Industry Core Hub: 
# https://github.com/eclipse-tractusx/industry-core-hub

from tractusx_sdk.dataspace.models.connector.model_factory import ModelFactory
from tractusx_sdk.dataspace.services.connector.base_connector_service import BaseConnectorService
import logging

@staticmethod
def create_asset(
    asset_id: str, 
    base_url: str, 
    dct_type:str, 
    version:str="3.0", 
    semantic_id:str=None, 
    proxy_params:dict={ 
                "proxyQueryParams": "false",
                "proxyPath": "true",
                "proxyMethod": "true",
                "proxyBody": "false"
                }, 
    headers:dict=None,
    private_properties:dict=None,
    connector_version:str="jupiter",
    base_connector_service: BaseConnectorService=None,
    logger: logging.Logger=None
):

    context =  {
        "edc": "https://w3id.org/edc/v0.0.1/ns/",
        "cx-common": "https://w3id.org/catenax/ontology/common#",
        "cx-taxo": "https://w3id.org/catenax/taxonomy#",
        "dct": "http://purl.org/dc/terms/"
    }

    data_address = { 
            "@type": "DataAddress",
            "type": "HttpData",
            "baseUrl": base_url
        }

    if(proxy_params is not None):
        data_address.update(proxy_params)

    if headers is not None:
        for key, value in headers.items():
            data_address["header:"+key] = value

    properties:dict = {
            "dct:type": {
                "@id": dct_type
            }
        }

    if(version is not None):
        properties["cx-common:version"] = version

    if(semantic_id is not None):
        context["aas-semantics"] = "https://admin-shell.io/aas/3/0/HasSemantics/"
        properties["aas-semantics:semanticId"] = { "@id": semantic_id }

    asset = ModelFactory.get_asset_model(
        connector_version=connector_version,
        context=context,
        oid=asset_id,
        properties=properties,
        private_properties=private_properties,
        data_address=data_address
    )

    asset_response = base_connector_service.provider.assets.create(obj=asset)

    if asset_response.status_code != 200:
        logger.error(asset_response.text)
        raise ValueError(f"Failed to create asset {asset_id}. Status code: {asset_response.status_code}")

    return asset_response.json()

@staticmethod
def create_contract(
    contract_id:str,
    usage_policy_id:str,
    access_policy_id:str,
    asset_id:str,
    connector_version:str="jupiter",
    base_connector_service: BaseConnectorService=None,
    logger: logging.Logger = None
) -> dict:
    context =  {
        "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
    }
    
    asset_selector = [
        {
            "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
            "operator": "=",
            "operandRight": asset_id
        }
    ]
    
    contract = ModelFactory.get_contract_definition_model(
        context=context,
        connector_version=connector_version,
        oid=contract_id,
        assets_selector=asset_selector,
        contract_policy_id=usage_policy_id,
        access_policy_id=access_policy_id
    )
    
    # If it doesn't exist, create it
    logger.info(f"Creating new contract with ID {contract_id}.")
    created_contract = base_connector_service.provider.contract_definitions.create(obj=contract)
    
    if created_contract.status_code != 200:
        raise ValueError(f"Failed to create contract {contract_id}. Status code: {created_contract.status_code}")
    
    logger.info(f"Contract {contract_id} created successfully.")
    return created_contract.json()

@staticmethod
def create_policy(
    policy_id: str,
    context: dict | list[dict] = {},
    permissions: dict | list[dict] = [],
    prohibitions: dict | list[dict] = [],
    obligations: dict | list[dict] = [],
    connector_version:str="jupiter",
    base_connector_service: BaseConnectorService=None,
    logger: logging.Logger = None
) -> dict:
    policy = ModelFactory.get_policy_model(
            connector_version=connector_version,
            oid=policy_id,
            context=context,
            permissions=permissions,
            prohibitions=prohibitions,
            obligations=obligations
    )
    # If it doesn't exist, create it
    logger.info(f"Creating new policy with ID {policy_id}.")
    created_policy = base_connector_service.provider.policies.create(obj=policy)
    
    if created_policy.status_code != 200:
        raise ValueError(f"Failed to create policy {policy_id}. Status code: {created_policy.status_code}")
    
    logger.info(f"Policy {policy_id} created successfully.")
    return created_policy.json()
