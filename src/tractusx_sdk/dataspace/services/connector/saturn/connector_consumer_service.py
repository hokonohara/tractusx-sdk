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

from ..base_connector_consumer import BaseConnectorConsumerService
from ....managers.connection.base_connection_manager import BaseConnectionManager
import logging
from ....models.connector.model_factory import ModelFactory
from ....adapters.connector.adapter_factory import AdapterFactory
from ....controllers.connector.base_dma_controller import BaseDmaController
from ....controllers.connector.controller_factory import ControllerType, ControllerFactory
from ....models.connector.saturn.catalog_model import CatalogModel

from requests import Response
class ConnectorConsumerService(BaseConnectorConsumerService):
    
    DEFAULT_CONTEXT:dict = {"edc": "https://w3id.org/edc/v0.0.1/ns/","odrl": "http://www.w3.org/ns/odrl/2/","dct": "https://purl.org/dc/terms/"}
    _connector_discovery_controller: BaseDmaController
    
    def __init__(self, dataspace_version: str, base_url: str, dma_path: str, headers: dict = None,
                 connection_manager: BaseConnectionManager = None, verbose: bool = True, logger: logging.Logger = None):
        # Backwards compatibility: if verbose is True and no logger provided, use default logger
        if self.verbose and self.logger is None:
            self.logger = logging.getLogger(__name__)

        self.dma_adapter = AdapterFactory.get_dma_adapter(
            dataspace_version=dataspace_version,
            base_url=base_url,
            dma_path=dma_path,
            headers=headers
        )

        self.controllers = ControllerFactory.get_dma_controllers_for_version(
            dataspace_version=dataspace_version,
            adapter=self.dma_adapter,
            controller_types=[
                ControllerType.CATALOG,
                ControllerType.EDR,
                ControllerType.CONTRACT_NEGOTIATION,
                ControllerType.TRANSFER_PROCESS,
                ControllerType.CONNECTOR_DISCOVERY
            ]
        )
        self._connector_discovery_controller = self.controllers.get(ControllerType.CONNECTOR_DISCOVERY)
        super().__init__(
            dataspace_version=dataspace_version,
            base_url=base_url,
            dma_path=dma_path,
            headers=headers,
            connection_manager=connection_manager,
            verbose=verbose,
            logger=logger
        )
        
    @property
    def connector_discovery(self):
        return self._connector_discovery_controller

    def discover_connector_protocol(self, bpnl: str, counter_party_address: str = None) -> dict | None:

        response: Response = self.connector_discovery.get_discover(
            ModelFactory.get_connector_discovery_model(dataspace_version=self.dataspace_version,
                                                       bpnl=bpnl,
                                                       counter_party_address=counter_party_address)
        )
        if response is None or response.status_code != 200:
            raise ConnectionError(
                f"Connector Service It was not possible to get the catalog from the EDC provider! Response code: [{response.status_code}]")
        return response.json()

    def get_catalog_with_bpnl(self, bpnl: str, counter_party_address: str = None, namespace: str = "https://w3id.org/edc/v0.0.1/ns/", context=DEFAULT_CONTEXT) -> dict | None:
        """
        Retrieves the EDC DCAT catalog using the BPNL to discover the connector protocol and address.

        Parameters:
        bpnl (str): The Business Partner Number (BPN) of the counterparty.
        counter_party_address (str, optional): The URL of the EDC provider. If not provided, it will be discovered using the BPNL.

        Returns:
        dict | None: The EDC catalog as a dictionary, or None if the request fails.
        """
        discovery_info = self.discover_connector_protocol(bpnl=bpnl, counter_party_address=counter_party_address)
        counter_party_address = discovery_info[f"{namespace}counterPartyAddress"]
        protocol = discovery_info[f"{namespace}protocol"]
        counter_party_id = discovery_info[f"{namespace}counterPartyId"]

        if self.verbose and self.logger is None:
            self.logger.debug(f"[Connector Service] Executing catalog request to {counter_party_address} with {counter_party_id} using protocol {protocol}.")
        request = self.get_catalog_request(counter_party_id=counter_party_id,
                                    counter_party_address=counter_party_address, protocol=protocol, context=context)
        # Assuming counter_party_id can be derived from BPNL or is not strictly required
        return self.get_catalog(request=request)

    def get_catalog_request(self, counter_party_id: str, counter_party_address: str, protocol: str = "dataspace-protocol-http:2025-1", context=DEFAULT_CONTEXT) -> CatalogModel:
        return ModelFactory.get_catalog_model(
            dataspace_version=self.dataspace_version,
            context=context,
            counter_party_id=counter_party_id,  ## bpn of the provider
            counter_party_address=counter_party_address,  ## dsp url from the provider,
            protocol=protocol
        )