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

# -----------------IMPORTS---------------------------

import pytest
import json
from tools import op

#------------TEST VARIABLES--------------------------

# print(op.json_string_to_object(""))
# -----------------TESTS-----------------------------

#Function 1 - json_string_to_object
def test_json_string_to_object_empty_input_should_return_JSONDecodeError():
    #Arange
    empty_string: str = "" 
    empty_bytes: bytes = bytes() 
    empty_bytearray:bytearray  = bytearray()
    whitespace_string:str = " "
    whitespace_bytes:bytes = bytes(" ",'utf-8')
    whitespace_bytearray:bytearray= bytearray(" ",'utf-8')
    #Act
    
    #Assert
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(empty_string)    
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(empty_bytes) 
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(empty_bytearray) 
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(whitespace_string) 
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(whitespace_bytes) 
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(whitespace_bytearray) 

def test_json_string_to_object_invalid_type_syntax_should_return_TypeError():
    #Arange
    invalid_type_none = None
    invalid_type_int:int = 42
    invalid_type_float: float = 3.14
    invalid_type_list: list = [1, 2, 3]
    invalid_type_dict: dict = {"name": "John", "age": 30}
    invalid_type_tuple: tuple = (1, 2, 3)
    invalid_type_set: set = {1, 2, 3}
    invalid_type_boolean: bool = True
    #Act
    
    #Assert
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_none)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_int)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_float)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_list)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_dict)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_tuple)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_set)
        
    with pytest.raises(TypeError):
        op.json_string_to_object(invalid_type_boolean)
                             
def test_json_string_to_object_invalid_JSON_format_should_return_JSONDecodeError():
    #Arange
    extra_comma:str = '{"name": "John", "age": 30,}'
    unquoted_key:str = '{name: "John", age: 30}'
    missing_bracket:str = '{"name": "John", "age": 30'
    mismatching_bracket:str = '{"name": "John"} "age": 30}'
    unescaped_special_characters:str = '{"name": "John \n Doe"}'
    #Act
    
    #Assert
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(extra_comma)    
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(unquoted_key) 
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(missing_bracket) 
    
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(mismatching_bracket)
        
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(unescaped_special_characters)
        
def test_json_string_to_object_string_should_return_valid_JSON():
    #Arange
    string: str = """{
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com",
            "is_active": true,
            "tags": ["developer", "python", "tester"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": null,
                "postal_code": "12345"
            },
            "history": [
                {"year": 2010, "event": "Started first job"},
                {"year": 2015, "event": "Moved to a new city"},
                {"year": 2020, "event": "Started a new project"}
            ]
            }
            """ 
            
    #Act
    result = op.json_string_to_object(string)
    #Assert
        # Basic fields
    assert result["name"] == "John Doe"
    assert result["age"] == 30
    assert result["email"] == "john.doe@example.com"
    assert result["is_active"] is True  
    assert result["tags"] == ["developer", "python", "tester"]
    
        # Nested "address" fields
    assert result["address"]["street"] == "123 Main St"
    assert result["address"]["city"] == "Anytown"
    assert result["address"]["state"] == None
    assert result["address"]["postal_code"] == "12345"
    
        # History list assertions
    assert len(result["history"]) == 3 
    assert result["history"][0]["year"] == 2010
    assert result["history"][0]["event"] == "Started first job"
    assert result["history"][1]["year"] == 2015
    assert result["history"][1]["event"] == "Moved to a new city"
    assert result["history"][2]["year"] == 2020
    assert result["history"][2]["event"] == "Started a new project"    
        
def test_json_string_to_object_bytes_should_return_valid_JSON():
    #Arange
    bytes_input: bytes = b"""{
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com",
            "is_active": true,
            "tags": ["developer", "python", "tester"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "AN",
                "postal_code": "12345"
            },
            "history": [
                {"year": 2010, "event": "Started first job"},
                {"year": 2015, "event": "Moved to a new city"},
                {"year": 2020, "event": "Started a new project"}
            ]
            }
            """ 
            
    #Act
    result = op.json_string_to_object(bytes_input)
    #Assert
        # Basic fields
    assert result["name"] == "John Doe"
    assert result["age"] == 30
    assert result["email"] == "john.doe@example.com"
    assert result["is_active"] is True  
    assert result["tags"] == ["developer", "python", "tester"]
    
        # Nested "address" fields
    assert result["address"]["street"] == "123 Main St"
    assert result["address"]["city"] == "Anytown"
    assert result["address"]["state"] == "AN"
    assert result["address"]["postal_code"] == "12345"
    
        # History list assertions
    assert len(result["history"]) == 3 
    assert result["history"][0]["year"] == 2010
    assert result["history"][0]["event"] == "Started first job"
    assert result["history"][1]["year"] == 2015
    assert result["history"][1]["event"] == "Moved to a new city"
    assert result["history"][2]["year"] == 2020
    assert result["history"][2]["event"] == "Started a new project"
    
def test_json_string_to_object_bytearray_should_return_valid_JSON():
    #Arange
    bytearray_input: bytearray = bytearray("""{
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com",
            "is_active": true,
            "tags": ["developer", "python", "tester"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "AN",
                "postal_code": "12345"
            },
            "history": [
                {"year": 2010, "event": "Started first job"},
                {"year": 2015, "event": "Moved to a new city"},
                {"year": 2020, "event": "Started a new project"}
            ]
            }
            """, 'utf-8' )
            
    #Act
    result = op.json_string_to_object(bytearray_input)
    #Assert
        # Basic fields
    assert result["name"] == "John Doe"
    assert result["age"] == 30
    assert result["email"] == "john.doe@example.com"
    assert result["is_active"] is True  
    assert result["tags"] == ["developer", "python", "tester"]
    
        # Nested "address" fields
    assert result["address"]["street"] == "123 Main St"
    assert result["address"]["city"] == "Anytown"
    assert result["address"]["state"] == "AN"
    assert result["address"]["postal_code"] == "12345"
    
        # History list assertions
    assert len(result["history"]) == 3 
    assert result["history"][0]["year"] == 2010
    assert result["history"][0]["event"] == "Started first job"
    assert result["history"][1]["year"] == 2015
    assert result["history"][1]["event"] == "Moved to a new city"
    assert result["history"][2]["year"] == 2020
    assert result["history"][2]["event"] == "Started a new project"

def test_json_string_to_object_unicode_characters_should_return_valid_JSON():
    #Arange
    unicode_string:str = '{"name": "Jöhn", "age": 30}'
    #Act
    result = op.json_string_to_object(unicode_string)
    #Assert
    assert result["name"][1] == 'ö'

#Function 2 - to_json



#Function 3 - to_json_file



#Function 4 - read_json_file



#Function 5 - path_exists



#Function 6 - make_dir



#Function 7 - delete_dir



#Function 8 - copy_file



#Function 9 - move_file



#Function 10 - to_string



#Function 11 - load_file



#Function 12 - delete_file



#Function 13 - timestamp



#Function 14 - get_filedatetime



#Function 15 - get_filedate



#Function 16 - get_path_without_file



#Function 17 - write_to_file



#Function 18 - wait



#Function 19 - get_attribute