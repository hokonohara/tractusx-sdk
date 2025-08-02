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
## Code created partially using a LLM (Claude Sonnet 4) and reviewed by a human committer

import pytest
import logging
from unittest.mock import Mock, patch
from tractusx_sdk.extensions.semantics.schema_to_context_translator import SammSchemaContextTranslator


@pytest.fixture
def translator():
    """Create a basic translator instance for testing."""
    return SammSchemaContextTranslator()


@pytest.fixture
def translator_with_logger():
    """Create a translator instance with a logger for verbose testing."""
    logger = Mock(spec=logging.Logger)
    return SammSchemaContextTranslator(logger=logger, verbose=True)


@pytest.fixture
def simple_schema():
    """A simple string schema for testing."""
    return {
        "type": "string",
        "description": "A simple string property"
    }


@pytest.fixture
def object_schema():
    """A simple object schema for testing."""
    return {
        "type": "object",
        "description": "A simple object",
        "properties": {
            "name": {
                "$ref": "#/components/schemas/StringProperty"
            },
            "age": {
                "$ref": "#/components/schemas/NumberProperty"
            }
        }
    }


@pytest.fixture
def array_schema():
    """A simple array schema for testing."""
    return {
        "type": "array",
        "description": "An array of strings",
        "items": {
            "$ref": "#/components/schemas/StringProperty"
        }
    }


@pytest.fixture
def complex_schema():
    """A complex schema with nested references."""
    return {
        "type": "object",
        "description": "Complex nested schema",
        "properties": {
            "basicInfo": {
                "$ref": "#/components/schemas/BasicInfo"
            },
            "items": {
                "$ref": "#/components/schemas/ItemList"
            }
        },
        "components": {
            "schemas": {
                "BasicInfo": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "$ref": "#/components/schemas/StringProperty"
                        }
                    }
                },
                "ItemList": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/StringProperty"
                    }
                },
                "StringProperty": {
                    "type": "string"
                },
                "NumberProperty": {
                    "type": "number"
                }
            }
        }
    }


class TestSammSchemaContextTranslatorInit:
    """Test initialization and basic properties."""

    def test_init_default(self):
        """Test default initialization."""
        translator = SammSchemaContextTranslator()
        
        assert translator.baseSchema == {}
        assert translator.rootRef == "#"
        assert translator.refKey == "$ref"
        assert translator.path_sep == "#/"
        assert translator.actualPathSep == "/-/"
        assert translator.refPathSep == "/"
        assert translator.propertiesKey == "properties"
        assert translator.logger is None
        assert translator.verbose is False
        assert translator.itemKey == "items"
        assert translator.schemaPrefix == "schema"
        assert translator.aspectPrefix == "aspect"
        assert translator.contextPrefix == "@context"
        assert translator.recursionDepth == 2
        assert translator.depht == 0

    def test_init_with_logger_and_verbose(self):
        """Test initialization with logger and verbose mode."""
        logger = Mock(spec=logging.Logger)
        translator = SammSchemaContextTranslator(logger=logger, verbose=True)
        
        assert translator.logger == logger
        assert translator.verbose is True

    def test_initial_jsonld_structure(self, translator):
        """Test the initial JSON-LD structure."""
        expected = {
            "@version": 1.1,
            "schema": "https://schema.org/"
        }
        assert translator.initialJsonLd == expected

    def test_context_template_structure(self, translator):
        """Test the context template structure."""
        expected = {
            "@version": 1.1,
            "id": "@id",
            "type": "@type"
        }
        assert translator.contextTemplate == expected


class TestSchemaToJsonLD:
    """Test the main schema_to_jsonld method."""

    def test_schema_to_jsonld_simple_string(self, translator):
        """Test converting a simple string schema to JSON-LD (flattened)."""
        semantic_id = "urn:samm:example:1.0.0#TestAspect"
        schema = {
            "type": "string",
            "description": "Test string property"
        }
        
        result = translator.schema_to_jsonld(semantic_id, schema)
        
        assert "@context" in result
        context = result["@context"]
        assert "@version" in context
        assert context["@version"] == 1.1
        assert "schema" in context
        assert context["schema"] == "https://schema.org/"
        assert "TestAspect" in context
        assert context["TestAspect"] == "urn:samm:example:1.0.0#"
        assert "@definition" in context
        assert context["@definition"] == "Test string property"

    def test_schema_to_jsonld_with_custom_aspect_prefix(self, translator):
        """Test with nested schema method which supports custom aspect prefix."""
        semantic_id = "urn:samm:example:1.0.0#TestAspect"
        schema = {"type": "string"}
        
        result = translator.schema_to_jsonld_nested(semantic_id, schema, aspectPrefix="custom")
        
        context = result["@context"]
        assert "custom" in context
        assert context["custom"] == "urn:samm:example:1.0.0#"

    def test_schema_to_jsonld_invalid_semantic_id(self, translator):
        """Test with invalid semantic ID."""
        invalid_ids = [
            "invalid_semantic_id",
            "urn:samm:example:1.0.0",
            "urn:samm:example:1.0.0#",
            ""
        ]
        schema = {"type": "string"}
        
        for invalid_id in invalid_ids:
            with pytest.raises(Exception, match="It was not possible to create flattened jsonld schema"):
                translator.schema_to_jsonld(invalid_id, schema)

    def test_schema_to_jsonld_with_description(self, translator):
        """Test schema with description (flattened context)."""
        semantic_id = "urn:samm:example:1.0.0#TestAspect"
        schema = {
            "type": "string",
            "description": "Test description"
        }
        
        result = translator.schema_to_jsonld(semantic_id, schema)
        context = result["@context"]
        
        assert "TestAspect" in context
        assert context["TestAspect"] == "urn:samm:example:1.0.0#"
        assert "@definition" in context
        assert context["@definition"] == "Test description"


class TestCreateNode:
    """Test the create_node method and its variations."""

    def test_create_node_string_type(self, translator):
        """Test creating a node for string type."""
        property_def = {"type": "string"}
        result = translator.create_node(property_def)
        
        assert result is not None
        assert "@type" in result
        assert result["@type"] == "schema:string"

    def test_create_node_number_type(self, translator):
        """Test creating a node for number type."""
        property_def = {"type": "number"}
        result = translator.create_node(property_def)
        
        assert result is not None
        assert "@type" in result
        assert result["@type"] == "schema:number"

    def test_create_node_no_type(self, translator):
        """Test creating a node without type returns None."""
        property_def = {"description": "No type property"}
        result = translator.create_node(property_def)
        
        assert result is None

    def test_create_node_empty_property(self, translator):
        """Test creating a node with empty property returns None."""
        result = translator.create_node(None)
        assert result is None
        
        result = translator.create_node({})
        assert result is None


class TestCreateValueNode:
    """Test the create_value_node method."""

    def test_create_value_node_string(self, translator):
        """Test creating a value node for string."""
        property_def = {"type": "string"}
        node = {}
        result = translator.create_value_node(property_def, node)
        
        assert result is not None
        assert "@type" in result
        assert result["@type"] == "schema:string"

    def test_create_value_node_boolean(self, translator):
        """Test creating a value node for boolean."""
        property_def = {"type": "boolean"}
        node = {}
        result = translator.create_value_node(property_def, node)
        
        assert result is not None
        assert "@type" in result
        assert result["@type"] == "schema:boolean"

    def test_create_value_node_no_type(self, translator):
        """Test creating a value node without type returns None."""
        property_def = {"description": "No type"}
        node = {}
        result = translator.create_value_node(property_def, node)
        
        assert result is None


class TestCreateObjectNode:
    """Test the create_object_node method."""

    @patch.object(SammSchemaContextTranslator, 'create_properties_context')
    def test_create_object_node_with_properties(self, mock_create_properties, translator):
        """Test creating an object node with properties."""
        mock_create_properties.return_value = {"test": "context"}
        
        property_def = {
            "type": "object",
            "properties": {
                "name": {"$ref": "#/components/schemas/StringProperty"}
            }
        }
        node = {}
        
        result = translator.create_object_node(property_def, node, "test/ref")
        
        assert result is not None
        assert "@context" in result
        assert result["@context"] == {"test": "context"}
        mock_create_properties.assert_called_once()

    def test_create_object_node_no_properties(self, translator):
        """Test creating an object node without properties returns None."""
        property_def = {"type": "object"}
        node = {}
        
        result = translator.create_object_node(property_def, node, "test/ref")
        assert result is None


class TestCreateArrayNode:
    """Test the create_array_node method."""

    def test_create_array_node_with_simple_items(self, translator):
        """Test creating an array node with simple items."""
        property_def = {
            "type": "array",
            "items": {"type": "string"}
        }
        node = {}
        
        result = translator.create_array_node(property_def, node, "test/ref")
        
        assert result is not None
        assert "@container" in result
        assert result["@container"] == "@list"
        assert "@type" in result
        assert result["@type"] == "schema:string"

    def test_create_array_node_with_list_items(self, translator):
        """Test creating an array node with list items."""
        property_def = {
            "type": "array",
            "items": []
        }
        node = {}
        
        result = translator.create_array_node(property_def, node, "test/ref")
        
        assert result is not None
        assert "@container" in result
        assert result["@container"] == "@list"

    @patch.object(SammSchemaContextTranslator, 'create_item_context')
    def test_create_array_node_with_ref_items(self, mock_create_item, translator):
        """Test creating an array node with reference items."""
        mock_create_item.return_value = {"test": "context"}
        
        property_def = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/StringProperty"}
        }
        node = {}
        
        result = translator.create_array_node(property_def, node, "test/ref")
        
        assert result is not None
        assert "@container" in result
        assert result["@container"] == "@list"
        assert "@context" in result
        assert result["@context"] == {"test": "context"}

    def test_create_array_node_no_items(self, translator):
        """Test creating an array node without items returns None."""
        property_def = {"type": "array"}
        node = {}
        
        result = translator.create_array_node(property_def, node, "test/ref")
        assert result is None


class TestFilterKey:
    """Test the filter_key method."""

    def test_filter_key_with_at_symbol(self, translator):
        """Test filtering key with @ symbol."""
        result = translator.filter_key("@type")
        assert result == "type"

    def test_filter_key_with_spaces(self, translator):
        """Test filtering key with spaces."""
        result = translator.filter_key("my property")
        assert result == "my-property"

    def test_filter_key_with_both(self, translator):
        """Test filtering key with both @ and spaces."""
        result = translator.filter_key("@my property")
        assert result == "my-property"

    def test_filter_key_normal(self, translator):
        """Test filtering normal key."""
        result = translator.filter_key("normalKey")
        assert result == "normalKey"


class TestCreatePropertiesContext:
    """Test the create_properties_context method."""

    @patch.object(SammSchemaContextTranslator, 'create_node_property')
    def test_create_properties_context_valid(self, mock_create_node_property, translator):
        """Test creating properties context with valid properties."""
        mock_create_node_property.return_value = {"@id": "aspect:testProp"}
        
        properties = {
            "testProp": {"$ref": "#/components/schemas/StringProperty"}
        }
        
        result = translator.create_properties_context(properties, "test/ref")
        
        assert result is not None
        assert "@version" in result
        assert result["@version"] == 1.1
        assert "id" in result
        assert "type" in result
        assert "testProp" in result
        assert result["testProp"] == {"@id": "aspect:testProp"}

    def test_create_properties_context_empty(self, translator):
        """Test creating properties context with empty properties returns None."""
        result = translator.create_properties_context({}, "test/ref")
        assert result is None
        
        result = translator.create_properties_context(None, "test/ref")
        assert result is None

    def test_create_properties_context_invalid_type(self, translator):
        """Test creating properties context with invalid type returns None."""
        result = translator.create_properties_context("not_a_dict", "test/ref")
        assert result is None


class TestCreateSimpleNode:
    """Test the create_simple_node method."""

    def test_create_simple_node_with_key(self, translator):
        """Test creating simple node with key."""
        property_def = {"description": "Test property"}
        result = translator.create_simple_node(property_def, "testKey")
        
        assert result is not None
        assert "@id" in result
        assert result["@id"] == "aspect:testKey"
        assert "@context" in result
        assert "@definition" in result["@context"]
        assert result["@context"]["@definition"] == "Test property"

    def test_create_simple_node_without_key(self, translator):
        """Test creating simple node without key."""
        property_def = {"description": "Test property"}
        result = translator.create_simple_node(property_def)
        
        assert result is not None
        assert "@id" not in result
        assert "@context" in result
        assert "@definition" in result["@context"]
        assert result["@context"]["@definition"] == "Test property"

    def test_create_simple_node_no_description(self, translator):
        """Test creating simple node without description."""
        property_def = {"type": "string"}
        result = translator.create_simple_node(property_def, "testKey")
        
        assert result is not None
        assert "@id" in result
        assert result["@id"] == "aspect:testKey"
        assert "@context" not in result

    def test_create_simple_node_empty_property(self, translator):
        """Test creating simple node with empty property returns None."""
        result = translator.create_simple_node(None)
        assert result is None


class TestGetSchemaRef:
    """Test the get_schema_ref method with mocked op.get_attribute."""

    @patch('tractusx_sdk.extensions.semantics.schema_to_context_translator.op.get_attribute')
    def test_get_schema_ref_valid(self, mock_get_attribute, translator):
        """Test getting schema reference with valid path."""
        mock_get_attribute.return_value = {"type": "string"}
        translator.baseSchema = {"components": {"schemas": {"StringProperty": {"type": "string"}}}}
        
        result = translator.get_schema_ref("#/components/schemas/StringProperty", "test/ref")
        
        assert result == {"type": "string"}
        mock_get_attribute.assert_called_once_with(
            translator.baseSchema, 
            attr_path="components/schemas/StringProperty", 
            path_sep="/",
            default_value=None
        )

    def test_get_schema_ref_invalid_type(self, translator):
        """Test getting schema reference with invalid type returns None."""
        result = translator.get_schema_ref(123, "test/ref")
        assert result is None

    @patch('tractusx_sdk.extensions.semantics.schema_to_context_translator.op.get_attribute')
    def test_get_schema_ref_recursion_detection(self, mock_get_attribute, translator_with_logger):
        """Test recursion detection in get_schema_ref."""
        mock_get_attribute.return_value = {"type": "string"}
        translator_with_logger.baseSchema = {"test": "schema"}
        
        # First call should work
        result1 = translator_with_logger.get_schema_ref("test/ref", "some/other/test/ref")
        assert result1 == {"type": "string"}
        
        # Second call with same ref in actualref should increment depth
        result2 = translator_with_logger.get_schema_ref("test/ref", "some/other/test/ref/more")
        assert result2 == {"type": "string"}
        
        # Third call should trigger recursion limit
        translator_with_logger.depht = 2  # Set to limit
        result3 = translator_with_logger.get_schema_ref("test/ref", "some/other/test/ref/even/more")
        assert result3 is None
        
        # Check that warning was logged
        translator_with_logger.logger.warning.assert_called()


class TestExpandNode:
    """Test the expand_node method."""

    @patch.object(SammSchemaContextTranslator, 'get_schema_ref')
    @patch.object(SammSchemaContextTranslator, 'create_node')
    def test_expand_node_valid(self, mock_create_node, mock_get_schema_ref, translator):
        """Test expanding a valid node reference."""
        mock_get_schema_ref.return_value = {"type": "string"}
        mock_create_node.return_value = {"@type": "schema:string"}
        
        result = translator.expand_node("#/components/schemas/StringProperty", "test/ref", "testKey")
        
        assert result == {"@type": "schema:string"}
        mock_get_schema_ref.assert_called_once_with(ref="#/components/schemas/StringProperty", actualref="test/ref")
        mock_create_node.assert_called_once()

    def test_expand_node_empty_ref(self, translator):
        """Test expanding empty reference returns None."""
        result = translator.expand_node("", "test/ref")
        assert result is None
        
        result = translator.expand_node(None, "test/ref")
        assert result is None

    @patch.object(SammSchemaContextTranslator, 'get_schema_ref')
    def test_expand_node_no_schema_found(self, mock_get_schema_ref, translator):
        """Test expanding node when no schema is found returns None."""
        mock_get_schema_ref.return_value = None
        
        result = translator.expand_node("#/components/schemas/MissingProperty", "test/ref")
        assert result is None


class TestIntegration:
    """Integration tests using complex schemas."""

    def test_complex_schema_integration(self, translator, complex_schema):
        """Test with a complex nested schema (flattened context)."""
        semantic_id = "urn:samm:example:1.0.0#ComplexAspect"
        
        result = translator.schema_to_jsonld(semantic_id, complex_schema)
        
        assert "@context" in result
        context = result["@context"]
        assert "ComplexAspect" in context
        assert context["ComplexAspect"] == "urn:samm:example:1.0.0#"
        assert "@definition" in context
        assert context["@definition"] == "Complex nested schema"

    def test_error_handling_in_main_method(self, translator):
        """Test error handling in main schema_to_jsonld method."""
        # Test with schema that will cause an error in create_node
        semantic_id = "urn:samm:example:1.0.0#TestAspect"
        invalid_schema = {"invalid": "schema"}  # No "type" field
        
        with pytest.raises(Exception, match="It was not possible to create flattened jsonld schema"):
            translator.schema_to_jsonld(semantic_id, invalid_schema)


