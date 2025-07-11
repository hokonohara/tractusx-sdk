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

from tractusx_sdk.dataspace.services.connector.service_factory import ServiceFactory


class TestBaseConsumerConnectorService(unittest.TestCase):
    def setUp(self):
        self.version = "jupiter"
        self.base_url = "http://consumer-control.plane.url"
        self.dma_path = "/management"
        self.headers = {"X-Api-Key": "api-key-secret", "Content-Type": "application/json"}

        self.service = ServiceFactory.get_connector_consumer_service(
            connector_version=self.version,
            base_url=self.base_url,
            dma_path=self.dma_path,
            headers=self.headers
        )

    def test_do_get_to_dtr(self):
        """Test the do_get method."""
        response = self.service.do_get(
            counter_party_address="http://provider-control.plane.url",
            counter_party_id="<provider-bpn>",
            filter_expression=[
                self.service.get_filter_expression(
                    key="'http://purl.org/dc/terms/type'.'@id'",
                    operator="=",
                    value="https://w3id.org/catenax/taxonomy#DigitalTwinRegistry"
                )
            ],
            path="/shell-descriptors",
            policies=[
                {
                    "odrl:permission": {
                        "odrl:action": {
                            "@id": "odrl:use"
                        },
                        "odrl:constraint": {
                            "odrl:and": [
                                {
                                    "odrl:leftOperand": {
                                        "@id": "cx-policy:FrameworkAgreement"
                                    },
                                    "odrl:operator": {
                                        "@id": "odrl:eq"
                                    },
                                    "odrl:rightOperand": "DataExchangeGovernance:1.0"
                                },
                                {
                                    "odrl:leftOperand": {
                                        "@id": "cx-policy:Membership"
                                    },
                                    "odrl:operator": {
                                        "@id": "odrl:eq"
                                    },
                                    "odrl:rightOperand": "active"
                                },
                                {
                                    "odrl:leftOperand": {
                                        "@id": "cx-policy:UsagePurpose"
                                    },
                                    "odrl:operator": {
                                        "@id": "odrl:eq"
                                    },
                                    "odrl:rightOperand": "cx.core.digitalTwinRegistry:1"
                                }
                            ]
                        }
                    },
                    "odrl:prohibition": [],
                    "odrl:obligation": []
                }
            ]
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
