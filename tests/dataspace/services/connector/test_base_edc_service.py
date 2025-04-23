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
from unittest.mock import patch, MagicMock, Mock

from tractusx_sdk.dataspace.adapters.connector.base_dma_adapter import BaseDmaAdapter
from tractusx_sdk.dataspace.controllers.connector.base_dma_controller import BaseDmaController
from tractusx_sdk.dataspace.services.connector.base_edc_service import BaseEdcService


class TestBaseEdcService(unittest.TestCase):
    def setUp(self):
        self.version = "v0_9_0"
        self.base_url = "https://example.com"
        self.dma_path = "/dma"
        self.headers = {"Authorization": "Bearer token"}

    def test_initialization_creates_controllers(self):
        service = BaseEdcService(
            version=self.version,
            base_url=self.base_url,
            dma_path=self.dma_path,
            headers=self.headers,
        )

        self.assertIsInstance(service._asset_controller, BaseDmaController)
        self.assertIsNotNone(service._asset_controller)

        self.assertIsInstance(service._catalog_controller, BaseDmaController)
        self.assertIsNotNone(service._catalog_controller)

        self.assertIsInstance(service._contract_agreement_controller, BaseDmaController)
        self.assertIsNotNone(service._contract_agreement_controller)

        self.assertIsInstance(service._contract_definition_controller, BaseDmaController)
        self.assertIsNotNone(service._contract_definition_controller)

        self.assertIsInstance(service._contract_negotiation_controller, BaseDmaController)
        self.assertIsNotNone(service._contract_negotiation_controller)

        self.assertIsInstance(service._edr_controller, BaseDmaController)
        self.assertIsNotNone(service._edr_controller)

        self.assertIsInstance(service._policy_controller, BaseDmaController)
        self.assertIsNotNone(service._policy_controller)

        self.assertIsInstance(service._transfer_process_controller, BaseDmaController)
        self.assertIsNotNone(service._transfer_process_controller)

    def test_builder_sets_dma_path(self):
        builder = BaseEdcService.builder()
        builder.dma_path(self.dma_path)
        self.assertEqual(builder._data["dma_path"], self.dma_path)
