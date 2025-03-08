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

from typing import Optional
from industry.models import (
    AssetKind,
    ShellDescriptor,
    SubModelDescriptor,
    GetAllShellDescriptorsResponse,
    GetSubmodelDescriptorsByAssResponse,
)
from dataspace.tools import HttpTools
from industry.tools import encode_as_base64_url_safe


class DtrService:
    def __init__(
        self, dtr_base_url: str, dtr_base_lookup_url: str, dtr_api_endpoint: str
    ):
        self.dtr_base_url = dtr_base_url
        self.dtr_base_lookup_url = dtr_base_lookup_url
        self.dtr_api_endpoint = dtr_api_endpoint
        self.dtr_url = (
            f"{self.dtr_base_url.rstrip('/')}{self.dtr_api_endpoint.rstrip('/')}"
        )
        self.dtr_lookup_url = (
            f"{self.dtr_base_lookup_url.rstrip('/')}{self.dtr_api_endpoint.rstrip('/')}"
        )

    def get_all_asset_administration_shell_descriptors(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        asset_kind: Optional[AssetKind] = None,
        asset_type: Optional[str] = None,
        bpn: Optional[str] = None,
    ) -> GetAllShellDescriptorsResponse:
        """
        Retrieves all Asset Administration Shell (AAS) Descriptors from the Digital Twin Registry.
        
        This method allows querying the DTR for shell descriptors with optional filtering by
        asset kind and type, as well as pagination support.

        Args:
            limit (int, optional): The maximum number of shell descriptors to return in a single response. 
                Must be a positive integer if provided.
            cursor (str, optional): A server-generated identifier that specifies where to continue
                listing results for pagination purposes. Obtained from a previous response.
            asset_kind (AssetKind, optional): Filter by the Asset's kind (Instance, Type, or NotApplicable).
            asset_type (str, optional): Filter by the Asset's type. Will be UTF8-BASE64-URL-encoded automatically.
            bpn (str, optional): Business Partner Number for authorization purposes. 
                When provided, it is added as an Edc-Bpn header to the request.

        Returns:
            GetAllShellDescriptorsResponse: A response object containing:
                - A list of ShellDescriptor objects in the 'result' field
                - Pagination metadata in the 'paging_metadata' field

        Raises:
            ValueError: If the limit parameter is provided but is less than 1
            HTTPError: If the request to the DTR API fails
            ConnectionError: If there is a network connectivity issue
            TimeoutError: If the request times out
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
        return GetAllShellDescriptorsResponse(**response.json())

    def get_asset_administration_shell_descriptor_by_id(
        self, aas_identifier: str, bpn: Optional[str] = None
    ) -> ShellDescriptor:
        """
        Retrieves a specific Asset Administration Shell (AAS) Descriptor by its identifier.
        
        This method fetches a single AAS descriptor from the Digital Twin Registry using its unique ID.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            ShellDescriptor: The requested Asset Administration Shell Descriptor object.

        Raises:
            HTTPError: If the request fails
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
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
        return ShellDescriptor(**response.json())

    def get_submodel_descriptors_by_aas_id(
        self,
        aas_identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        bpn: Optional[str] = None,
    ) -> GetSubmodelDescriptorsByAssResponse:
        """
        Retrieves all Submodel Descriptors associated with a specific Asset Administration Shell (AAS).
        
        This method fetches all submodels belonging to a particular AAS from the Digital Twin Registry,
        with support for pagination.

        Args:
            aas_identifier (str): The unique identifier of the Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            limit (int, optional): The maximum number of submodel descriptors to return in a single response.
                Must be a positive integer if provided.
            cursor (str, optional): A server-generated identifier that specifies where to continue 
                listing results for pagination purposes. Obtained from a previous response.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            GetSubmodelDescriptorsByAssResponse: A response object containing:
                - A list of SubModelDescriptor objects in the 'result' field
                - Pagination metadata in the 'paging_metadata' field

        Raises:
            ValueError: If the limit parameter is provided but is less than 1.
            HTTPError: If the request fails
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
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
        return GetSubmodelDescriptorsByAssResponse(**response.json())

    def get_submodel_descriptor_by_ass_and_submodel_id(
        self, aas_identifier: str, submodel_identifier: str, bpn: Optional[str] = None
    ) -> SubModelDescriptor:
        """
        Retrieves a specific Submodel Descriptor by its identifier and parent AAS identifier.
        
        This method fetches a single Submodel descriptor from the Digital Twin Registry using 
        both the Asset Administration Shell ID and Submodel ID.

        Args:
            aas_identifier (str): The unique identifier of the parent Asset Administration Shell.
                This ID will be automatically encoded as URL-safe Base64.
            submodel_identifier (str): The unique identifier of the Submodel to retrieve.
                This ID will be automatically encoded as URL-safe Base64.
            bpn (str, optional): Business Partner Number for authorization purposes. When provided,
                it is added as an Edc-Bpn header to the request.

        Returns:
            SubModelDescriptor: The requested Submodel Descriptor object.
                If no matching Submodel is found, the server will typically return a 404 error.

        Raises:
            HTTPError: If the request fails
            ConnectionError: If there is a network connectivity issue.
            TimeoutError: If the request times out.
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
        return SubModelDescriptor(**response.json())
