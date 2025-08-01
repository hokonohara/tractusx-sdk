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

import traceback
import logging
from tractusx_sdk.dataspace.tools import op
import copy

class SammSchemaContextTranslator:
    def __init__(self, logger=logging.logger=None, verbose:bool=False):
        self.baseSchema = {}
        self.rootRef = "#"
        self.refKey = "$ref"
        self.pathSep = "#/"
        self.actualPathSep = "/-/"
        self.refPathSep = "/"
        self.propertiesKey = "properties"
        self.logger = logger
        self.verbose = verbose
        self.itemKey = "items"
        self.schemaPrefix = "schema"
        self.aspectPrefix = "aspect"
        self.contextPrefix = "@context"
        self.recursionDepth = 2
        self.depht = 0
        self.initialJsonLd = {
            "@version": 1.1,
            self.schemaPrefix: "https://schema.org/"
        }
        self.contextTemplate = {
            "@version": 1.1,
            "id": "@id",
            "type": "@type"
        }

    def schema_to_jsonld(self, semanticId, schema, aspectPrefix="aspect"):
        try:
            self.baseSchema = schema.copy()
            parts = semanticId.split(self.rootRef)
            if len(parts) < 2 or not parts[1]:
                raise Exception("Invalid semantic id, missing the model reference!")
            if aspectPrefix:
                self.aspectPrefix = aspectPrefix

            node = self.create_node(schema)
            if not node:
                raise Exception("It was not possible to generated the json-ld!")

            ctx = self.initialJsonLd.copy()
            semanticPath, aspectName = parts
            ctx[self.aspectPrefix] = semanticPath + self.rootRef
            node["@id"] = f"{self.aspectPrefix}:{aspectName}"
            ctx[aspectName] = node
            if "description" in schema:
                ctx[aspectName].setdefault("@context", {})["@definition"] = schema["description"]
            return {"@context": ctx}
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create jsonld schema")

    def expand_node(self, ref, actualref, key=None):
        try:
            if not ref: return None
            node = self.get_schema_ref(ref, actualref)
            if not node: return None
            return self.create_node(node, actualref=self.actualPathSep.join([actualref, ref]), key=key)
        except:
            traceback.print_exc()
            raise Exception("It was not possible to get schema reference")

    def create_node(self, property, actualref="", key=None):
        try:
            if not property or "type" not in property: return None
            node = self.create_simple_node(property, key)
            if not node: return None

            if property["type"] == "object":
                return self.create_object_node(property, node, actualref)
            if property["type"] == "array":
                return self.create_array_node(property, node, actualref)
            return self.create_value_node(property, node)
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the node")

    def create_value_node(self, property, node):
        try:
            if "type" not in property: return None
            node["@type"] = f"{self.schemaPrefix}:{property['type']}"
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create value node")

    def create_object_node(self, property, node, actualref):
        try:
            if self.propertiesKey not in property: return None
            node[self.contextPrefix] = self.create_properties_context(property[self.propertiesKey], actualref)
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create object node")

    def create_array_node(self, property, node, actualref):
        try:
            if self.itemKey not in property: return None
            item = property[self.itemKey]
            node["@container"] = "@list"
            if isinstance(item, list): return node
            if self.refKey not in item:
                return self.create_value_node(item, node)
            node[self.contextPrefix] = self.create_item_context(item, actualref)
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the array node")

    def filter_key(self, key):
        return key.replace("@", "").replace(" ", "-")

    def create_properties_context(self, properties, actualref):
        try:
            if not isinstance(properties, dict) or not properties: return None
            context = self.contextTemplate.copy()
            for propKey, prop in properties.items():
                key = self.filter_key(propKey)
                node = self.create_node_property(key, prop, actualref)
                if node: context[key] = node
            return context
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create properties context")

    def create_item_context(self, item, actualref):
        try:
            if not item: return None
            context = self.contextTemplate.copy()
            node = self.expand_node(item[self.refKey], actualref)
            if not node: return None
            context.update(node)
            if "description" in item:
                context.setdefault("@context", {})["@definition"] = item["description"]
            return context
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the item context")

    def create_node_property(self, key, node, actualref):
        try:
            if not key or not node or self.refKey not in node: return None
            propNode = self.expand_node(node[self.refKey], actualref, key)
            if not propNode: return None
            if "description" in node:
                propNode.setdefault("@context", {})["@definition"] = node["description"]
            return propNode
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create node property")

    def create_simple_node(self, property, key=None):
        try:
            if not property: return None
            node = {"@id": f"{self.aspectPrefix}:{key}"} if key else {}
            if "description" in property:
                node.setdefault("@context", {})["@definition"] = property["description"]
            return node
        except:
            traceback.print_exc()
            raise Exception("It was not possible to create the simple node")

    def get_schema_ref(self, ref, actualref):
        try:
            if not isinstance(ref, str): return None
            if ref in actualref:
                if self.depht >= self.recursionDepth:
                    if(self.verbose and (self.logger not None)):
                        self.logger.warning(f"[WARNING] Infinite recursion detected: ref[{ref}], refPath[{actualref}]")
                    self.depht = 0
                    return None
                self.depht += 1
            path = ref.removeprefix(self.pathSep)
            return op.get_attribute(self.baseSchema, path, self.refPathSep)
        except:
            traceback.print_exc()
            raise Exception("It was not possible to get schema reference")