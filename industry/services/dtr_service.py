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

from typing import Dict, Optional, Any
from industry.models import AssetKind
from dataspace.tools import HttpTools
from industry.tools import encode_as_base64_url_safe


class DtrService:
    def __init__(self, dtr_base_url: str, dtr_base_lookup_url: str, dtr_api_endpoint: str):
        self.dtr_base_url = dtr_base_url
        self.dtr_base_lookup_url = dtr_base_lookup_url
        self.dtr_api_endpoint = dtr_api_endpoint
        self.dtr_url = (
            f"{self.dtr_base_url.rstrip('/')}{self.dtr_api_endpoint.rstrip('/')}"
        )
        self.dtr_lookup_url = (
            f"{self.dtr_base_lookup_url.rstrip('/')}{self.dtr_api_endpoint.rstrip('/')}"
        )

    def get_all_ass_descriptors(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        asset_kind: Optional[AssetKind] = None,
        asset_type: Optional[str] = None,
        bpn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns all Asset Administration Shell Descriptors.

        Args:
            limit (int, optional): The maximum number of elements in the response array
            cursor (str, optional): A server-generated identifier that specifies where to continue listing results
            asset_kind (AssetKind, optional): The Asset's kind (Instance, Type, or NotApplicable)
            asset_type (str, optional): The Asset's type (UTF8-BASE64-URL-encoded)
            bpn (str, optional): External subject ID / BPN for authorization

        Returns:
            dict: A dictionary containing the paging metadata and the list of Asset Administration Shell Descriptors

        Raises:
            HTTPError: If the request to the AAS Registry API fails
            ValueError: If the provided parameters are invalid
        """
        # Validate parameters
        if limit is not None and limit < 1:
            raise ValueError("Limit must be a positive integer")

        # Construct query parameters
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        if asset_kind:
            params["assetKind"] = asset_kind.value
        if asset_type:
            encoded_asset_type = encode_as_base64_url_safe(asset_type)
            params["assetType"] = encoded_asset_type

        # Construct headers
        headers = {"Accept": "application/json"}
        if bpn:
            headers["Edc-Bpn"] = bpn

        # Make the request using HttpTools
        url = f"{self.dtr_url}/shell-descriptors"
        response = HttpTools.do_get(
            url=url, params=params, headers=headers, verify=False
        )

        # Check for errors
        response.raise_for_status()

        # Return the parsed response
        return response.json()

    def get_aas_descriptor_by_id(
        self,
        aas_identifier: str,
        bpn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Returns a specific Asset Administration Shell Descriptor.

        Args:
            aas_identifier (str): The Asset Administration Shell's unique id
            bpn (str, optional): External subject ID / BPN for authorization

        Returns:
            dict: The requested Asset Administration Shell Descriptor

        Raises:
            HTTPError: If the request to the AAS Registry API fails
        """
        # Construct headers
        headers = {"Accept": "application/json"}
        if bpn:
            headers["Edc-Bpn"] = bpn

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.dtr_url}/shell-descriptors/{encoded_identifier}"
        response = HttpTools.do_get(url=url, headers=headers, verify=False)

        # Check for errors
        response.raise_for_status()

        # Return the parsed response
        return response.json()

    def get_submodel_descriptors_by_aas(
        self,
        aas_identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        bpn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns all Submodel Descriptors for a specific AAS.

        Args:
            aas_identifier (str): The Asset Administration Shell's unique id
            limit (int, optional): The maximum number of elements in the response array
            cursor (str, optional): A server-generated identifier for pagination
            bpn (str, optional): External subject ID / BPN for authorization

        Returns:
            dict: A dictionary containing the submodel descriptors

        Raises:
            HTTPError: If the request to the AAS Registry API fails
        """
        # Validate parameters
        if limit is not None and limit < 1:
            raise ValueError("Limit must be a positive integer")

        # Construct query parameters
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor

        # Construct headers
        headers = {"Accept": "application/json"}
        if bpn:
            headers["Edc-Bpn"] = bpn

        # Properly encode the AAS identifier as URL-safe Base64
        encoded_identifier = encode_as_base64_url_safe(aas_identifier)

        # Make the request
        url = f"{self.dtr_url}/shell-descriptors/{encoded_identifier}/submodel-descriptors"
        response = HttpTools.do_get(
            url=url, params=params, headers=headers, verify=False
        )

        # Check for errors
        response.raise_for_status()

        # Return the parsed response
        return response.json()

    def get_submodel_descriptor(
        self, aas_identifier: str, submodel_identifier: str, bpn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Returns a specific Submodel Descriptor.

        Args:
            aas_identifier (str): The Asset Administration Shell's unique id
            submodel_identifier (str): The Submodel's unique id
            bpn (str, optional): External subject ID / BPN for authorization

        Returns:
            dict: The requested Submodel Descriptor

        Raises:
            HTTPError: If the request to the AAS Registry API fails
        """
        # Construct headers
        headers = {"Accept": "application/json"}
        if bpn:
            headers["Edc-Bpn"] = bpn

        # Properly encode the AAS and Submodel identifiers as URL-safe Base64
        encoded_aas_identifier = encode_as_base64_url_safe(aas_identifier)
        encoded_submodel_identifier = encode_as_base64_url_safe(submodel_identifier)

        # Make the request
        url = f"{self.dtr_url}/shell-descriptors/{encoded_aas_identifier}/submodel-descriptors/{encoded_submodel_identifier}"
        response = HttpTools.do_get(url=url, headers=headers, verify=False)

        # Check for errors
        response.raise_for_status()

        # Return the parsed response
        return response.json()
