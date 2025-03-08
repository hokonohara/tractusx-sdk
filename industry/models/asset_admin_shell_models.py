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

from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
from pydantic import BaseModel, Field


class MultiLanguage(BaseModel):
    """Language-specific text entry."""

    language: str
    text: str


class AssetKind(str, Enum):
    """Enum for Asset kinds"""

    INSTANCE = "Instance"
    NOT_APPLICABLE = "NotApplicable"
    TYPE = "Type"


class ReferenceTypes(str, Enum):
    """Enum for reference types."""

    MODEL_REFERENCE = "ModelReference"
    EXTERNAL_REFERENCE = "ExternalReference"


class ReferenceKeyTypes(str, Enum):
    """Enum for reference key types."""

    ANNOTATED_RELATIONSHIP_ELEMENT = "AnnotatedRelationshipElement"
    ASSET_ADMINISTRATION_SHELL = "AssetAdministrationShell"
    BASIC_EVENT_ELEMENT = "BasicEventElement"
    BLOB = "Blob"
    CAPABILITY = "Capability"
    CONCEPT_DESCRIPTION = "ConceptDescription"
    DATA_ELEMENT = "DataElement"
    ENTITY = "Entity"
    EVENT_ELEMENT = "EventElement"
    FILE = "File"
    FRAGMENT_REFERENCE = "FragmentReference"
    GLOBAL_REFERENCE = "GlobalReference"
    IDENTIFIABLE = "Identifiable"
    MULTI_LANGUAGE_PROPERTY = "MultiLanguageProperty"
    OPERATION = "Operation"
    PROPERTY = "Property"
    RANGE = "Range"
    REFERABLE = "Referable"
    REFERENCE_ELEMENT = "ReferenceElement"
    RELATIONSHIP_ELEMENT = "RelationshipElement"
    SUBMODEL = "Submodel"
    SUBMODEL_ELEMENT = "SubmodelElement"
    SUBMODEL_ELEMENT_COLLECTION = "SubmodelElementCollection"
    SUBMODEL_ELEMENT_LIST = "SubmodelElementList"


class ReferenceKey(BaseModel):
    """Reference key"""

    type: ReferenceKeyTypes
    value: str = Field(min_length=1, max_length=2000)


class Reference(BaseModel):
    """External reference structure."""

    type: ReferenceTypes
    keys: List[ReferenceKey] = Field(default_factory=list)


class ProtocolInformationSecurityAttributesTypes(str, Enum):
    """Enum for security attributes types."""

    NONE = "NONE"
    RFC_TLSA = "RFC_TLSA"
    W3C_DID = "W3C_DID"


class ProtocolInformationSecurityAttributes(BaseModel):
    """Protocol information security for endpoints."""

    type: Optional[ProtocolInformationSecurityAttributesTypes]
    key: Optional[str]
    value: Optional[str]


class ProtocolInformation(BaseModel):
    """Protocol information for endpoints."""

    href: Optional[str] = None
    endpoint_protocol: Optional[str] = Field(None, alias="endpointProtocol")
    endpoint_protocol_version: Optional[List[str]] = Field(
        None, alias="endpointProtocolVersion"
    )
    subprotocol: Optional[str] = None
    subprotocol_body: Optional[str] = Field(None, alias="subprotocolBody")
    subprotocol_body_encoding: Optional[str] = Field(
        None, alias="subprotocolBodyEncoding"
    )
    security_attributes: Optional[List[ProtocolInformationSecurityAttributes]] = Field(
        default_factory=list, alias="securityAttributes"
    )


class EmbeddedDataSpecification(BaseModel):
    data_specification: Optional[Reference] = Field(None, alias="dataSpecification")
    dataSpecificationContent: Optional[Dict[str, Any]] = Field(
        None, alias="dataSpecificationContent"
    )


class AdministrativeInformation(BaseModel):
    embedded_data_specifications: Optional[EmbeddedDataSpecification] = Field(
        alias="embeddedDataSpecifications"
    )
    version: Optional[str] = Field(None, min_length=1, max_length=4)
    revision: Optional[str] = Field(None, min_length=1, max_length=4)
    creator: Optional[Reference]
    template_id: Optional[str] = Field(
        None, min_length=1, max_length=2000, alias="templateId"
    )


class Endpoint(BaseModel):
    """Class for endpoint information."""

    interface: str
    protocol_information: ProtocolInformation = Field(alias="protocolInformation")


class SubModelDescriptor(BaseModel):
    """Submodel descriptor for AAS."""

    description: List[MultiLanguage] = Field(default_factory=list)
    display_name: List[MultiLanguage] = Field(default_factory=list)
    administration: Optional[AdministrativeInformation] = None
    endpoints: List[Endpoint] = Field(default_factory=list)
    id_short: Optional[str] = Field(None, max_length=128)
    id: Optional[str] = Field(None, min_length=1, max_length=2000)
    semantic_id: Optional[Reference] = None
    supplemental_semantic_ids: Optional[List[Reference]] = Field(
        None, alias="supplementalSemanticIds"
    )

    def to_json_string(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True, by_alias=True)


class SpecificAssetId(BaseModel):
    """Model for specific asset identifiers."""

    name: str = Field(min_length=1, max_length=64)
    value: str = Field(min_length=1, max_length=2000)
    semantic_id: Optional[Reference] = Field(None, alias="semanticId")
    supplemental_semantic_ids: Optional[List[Reference]] = Field(
        None, alias="supplementalSemanticIds"
    )
    external_subject_id: Optional[Reference] = Field(None, alias="externalSubjectId")


class ShellDescriptor(BaseModel):
    """Asset Administration Shell (AAS) Descriptor."""

    description: List[MultiLanguage] = Field(default_factory=list)
    display_name: List[MultiLanguage] = Field(alias="displayName", default_factory=list)
    administration: Optional[AdministrativeInformation] = None
    id_short: Optional[str] = Field(None, alias="idShort", max_length=128)
    asset_kind: Optional[AssetKind] = Field(None, alias="assetKind")
    asset_type: Optional[str] = Field(None, alias="assetType")
    endpoints: List[Endpoint] = Field(default_factory=list)
    id: str = Field(default_factory=lambda: uuid.uuid4(), min_length=1, max_length=2000)
    global_asset_id: Optional[str] = Field(
        None,
        alias="globalAssetId",
        min_length=1,
        max_length=2000,
    )
    specific_asset_ids: List[SpecificAssetId] = Field(
        alias="specificAssetIds", default_factory=list
    )
    submodel_descriptors: List[SubModelDescriptor] = Field(
        alias="submodelDescriptors", default_factory=list
    )

    def add_description(self, text: str, language: str = "en") -> None:
        """Add a description in the specified language."""
        self.description.append(MultiLanguage(language=language, text=text))

    def add_display_name(self, text: str, language: str = "en") -> None:
        """Add a display name in the specified language."""
        self.display_name.append(MultiLanguage(language=language, text=text))

    def add_specific_asset_id(self, asset_id: SpecificAssetId) -> None:
        """Add a specific asset ID."""
        self.specific_asset_ids.append(asset_id)

    def add_submodel(self, submodel: SubModelDescriptor) -> None:
        """Add a submodel descriptor."""
        self.submodel_descriptors.append(submodel)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary representation."""
        return self.model_dump(exclude_none=True, by_alias=True)

    def to_json_string(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True, by_alias=True)


class PagingMetadata(BaseModel):
    """Paging metadata for the response."""

    cursor: Optional[str] = Field(None)


class BasePaginatedResponse(BaseModel):
    """Base class for paginated responses."""

    paging_metadata: Optional[PagingMetadata] = Field(None)


class GetAllShellDescriptorsResponse(BasePaginatedResponse):
    """Response model for the get_all_shell_descriptors method."""

    result: List[ShellDescriptor]


class GetSubmodelDescriptorsByAssResponse(BasePaginatedResponse):
    """Response model for the get_submodel_descriptors method."""

    result: List[SubModelDescriptor]
