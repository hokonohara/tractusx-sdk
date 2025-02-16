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

import math
import pytest
import json
from tools import op

#------------TEST VARIABLES--------------------------

# print(op.json_string_to_object(""))
# -----------------TESTS-----------------------------

#Function 1 - json_string_to_object
def test_json_string_to_object_with_empty_input_should_return_JSONDecodeError():
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

def test_json_string_to_object_with_invalid_type_syntax_should_return_TypeError():
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
                             
def test_json_string_to_object_with_invalid_JSON_format_should_return_JSONDecodeError():
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
        
def test_json_string_to_object_with_string_should_return_valid_JSON():
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
        
def test_json_string_to_object_with_bytes_should_return_valid_JSON():
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
    
def test_json_string_to_object_with_bytearray_should_return_valid_JSON():
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

def test_json_string_to_object_with_unicode_characters_should_return_valid_JSON():
    #Arange
    unicode_string:str = '{"name": "Jöhn", "age": 30}'
    #Act
    result = op.json_string_to_object(unicode_string)
    #Assert
    assert result["name"][1] == 'ö'

#Function 2 - to_json

def test_to_json_with_empty_dict_should_return_empty_object():
    #Arange
    source = {}
    expected = "{}"
    #Act
    result = op.to_json(source)
    #Assert
    assert result == expected
    
def test_to_json_with_simple_input_should_return_valid_json():
    #Arange
    source_dict = {"name": "John", "age": 30}
    source_list = [1, 2, 3]
    #Act
    result_dict = op.to_json(source_dict)
    result_list = op.to_json(source_list)
    #Assert
    assert json.loads(result_dict) == source_dict
    assert json.loads(result_list) == source_list

def test_to_json_with_none_input_should_return_null():
    #Arange
    source = None
    expected = "null"
    #Act
    result = op.to_json(source)
    #Assert
    assert result == expected

def test_to_json_with_boolean_should_return_true_or_false():
    #Arange
    source_true = True
    expected_true = "true"
    source_false = False
    expected_false = "false"
    #Act
    result_true = op.to_json(source_true)
    result_false = op.to_json(source_false)
    #Assert
    assert result_true == expected_true
    assert result_false == expected_false

def test_to_json_with_complex_data_should_return_valid_json():
    # Arrange
    source = {
        "company": "TechCorp",
        "founded": 1995,
        "active": True,
        "address": {
            "street": "123 Tech Lane",
            "city": "San Francisco",
            "zip": "94122",
            "geo": {"lat": 37.7749, "lng": -122.4194}
        },
        "employees": [
            {
                "id": 1,
                "name": "John Doe",
                "age": 35,
                "department": "Engineering",
                "skills": ["Python", "Java", "Docker"],
                "projects": ["Alpha", "Beta"]
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "age": 28,
                "department": "Design",
                "skills": ["UI/UX", "Sketch", "Photoshop"],
                "projects": ["Gamma"]
            }
        ],
        "products": ("Software A", "Software B", "Software C"),
        "partners": None
    }

    # Act
    result = op.to_json(source)
    parsed_result = json.loads(result)

    # Assert
    assert isinstance(parsed_result, dict)
    assert parsed_result["company"] == "TechCorp"
    assert parsed_result["founded"] == 1995
    assert parsed_result["active"] is True
    
        # Check nested 
    assert parsed_result["address"]["street"] == "123 Tech Lane"
    assert parsed_result["address"]["geo"]["lat"] == pytest.approx(37.7749)
    
        # Check array
    assert len(parsed_result["employees"]) == 2
    assert parsed_result["employees"][0]["name"] == "John Doe"
    assert "Python" in parsed_result["employees"][0]["skills"]
    assert parsed_result["employees"][1]["department"] == "Design"
    
        # Check conversion of tuple to list
    assert isinstance(parsed_result["products"], list)
    assert parsed_result["products"] == ["Software A", "Software B", "Software C"]
    
        # Check None value
    assert parsed_result["partners"] is None

        # Verify the entire structure matches
    assert parsed_result == {**source, "products": list(source["products"])} #Tuples will becomes list after serialzation
    
def test_to_json_with_indent_parameter_should_return_indented_json():
    #Arange
    source = {"name": "John", "age": 30}
    #Act
    result = op.to_json(source, indent=4)
    #Assert
    assert "\n" in result
    assert json.loads(result) == source

def test_to_json_with_non_ascii_characters_ensure_ascii_true_should_escape_characters():
    #Arange
    source = {"greeting": "こんにちは"}
    #Act
    result = op.to_json(source, ensure_ascii=True)
    # Assert
    assert "\\u3053" in result #checks non ascii works correctly

def test_to_json_with_non_ascii_characters_ensure_ascii_false_should_not_escape_characters():
    # Arange
    source = {"greeting": "こんにちは"}
    # Act
    result = op.to_json(source, ensure_ascii=False)
    # Assert
    assert "こんにちは" in result # When ensure_ascii is False, non-ASCII characters appear as is.

def test_to_json_with_float_nan_should_return_NaN():
    #Arange
    source = {"value": math.nan}
    #Act
    result = op.to_json(source)
    # Assert
    assert "NaN" in result #json.dumps should not quote NaNs

def test_to_json_with_float_inf_should_return_Infinity():
    #Arange
    source = {"value": math.inf}
    #Act
    result = op.to_json(source)
    #Assert
    assert "Infinity" in result

#Test shows error as indent def value is 0 so output adds newline before each element
#None as default is suggested to fix the indent issue if not intended
def test_to_json_with_tuple_should_convert_to_list():
    #Arange
    source = (1, 2, 3)
    expected = "[1, 2, 3]" # Tuples are serialized as lists.
    #Act
    result = op.to_json(source)
    #Assert
    assert result == expected

def test_to_json_with_non_string_dict_keys_should_convert_keys_to_strings():
    #Arange
    source = {1: "one", 2: "two"}
    #Act
    result = op.to_json(source)
    #Assert
    assert json.loads(result) == {"1": "one", "2": "two"}# JSON forces dictionary keys to be strings.

def test_to_json_with_custom_object_should_raise_TypeError():
    #Arange
    class Custom:
        pass
    source = Custom()
    #Act
    
    #Assert
    with pytest.raises(TypeError):# Custom objects are not serializable by default.
        op.to_json(source)

#Function 3 - to_json_file

#All fail due to mismatch of write_to_file parameter (filePath), should be file_path 

def test_to_json_file_with_simple_dict_should_write_valid_json(tmp_path):
    #Arange
    source = {"name": "Alice", "age": 30}
    file_path = tmp_path / "simple_dict.json"
    expected = json.dumps(source, indent=2)
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert
    content = file_path.read_text()
    assert content == expected

def test_to_json_file_with_list_should_write_valid_json(tmp_path):
    #Arange
    source = [1, "two", 3.0, True, None]
    file_path = tmp_path / "list.json"
    expected = json.dumps(source, indent=2)
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert.
    content = file_path.read_text()
    assert content == expected

def test_to_json_file_with_none_should_write_valid_json(tmp_path):
    #Arange
    source = None
    file_path = tmp_path / "none.json"
    expected = json.dumps(source, indent=2) # "null"
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert
    content = file_path.read_text()
    assert content == expected

def test_to_json_file_with_nested_data_should_write_valid_json(tmp_path):
    #Arange
    source = {
        "company": "TechCorp",
        "founded": 1995,
        "active": True,
        "address": {
            "street": "123 Tech Lane",
            "city": "San Francisco",
            "zip": "94122",
            "geo": {"lat": 37.7749, "lng": -122.4194}
        },
        "employees": [
            {
                "id": 1,
                "name": "John Doe",
                "age": 35,
                "department": "Engineering",
                "skills": ["Python", "Java", "Docker"],
                "projects": ["Alpha", "Beta"]
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "age": 28,
                "department": "Design",
                "skills": ["UI/UX", "Sketch", "Photoshop"],
                "projects": ["Gamma"]
            }
        ],
        "products": ("Software A", "Software B", "Software C"), # tuple, will be serialized as a JSON array (list)
        "partners": None
    }
    file_path = tmp_path / "nested.json"
    expected = json.dumps(source, indent=2)
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert
    content = file_path.read_text()
    assert json.loads(content) == json.loads(expected)

def test_to_json_file_with_empty_dict_should_write_valid_json(tmp_path):
    #Arange
    source = {}
    file_path = tmp_path / "empty_dict.json"
    expected = json.dumps(source, indent=2)
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert: An empty dictionary is correctly serialized.
    content = file_path.read_text()
    assert content == expected

def test_to_json_file_with_non_ascii_characters_should_write_valid_json(tmp_path):
    #Arange
    source = {"greeting": "こんにちは"} # Non-ASCII text
    file_path = tmp_path / "non_ascii.json"
    expected = json.dumps(source, indent=2)
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert
    content = file_path.read_text()
    assert content == expected #Ensure non-ASCII characters are serialized as expected (escaped if ensure_ascii is True).

def test_to_json_file_with_append_mode_should_append_valid_json(tmp_path):
    #Arange
    source = {"appended": True}
    file_path = tmp_path / "append.json"
    initial_content = "Existing Content\n"
    file_path.write_text(initial_content)
    expected = initial_content + json.dumps(source, indent=2)
    #Act
    op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="a", indent=2)
    #Assert
    content = file_path.read_text()
    assert content == expected #The JSON data should be appended after the initial content.

def test_to_json_file_with_invalid_file_mode_should_raise_exception(tmp_path):
    #Arange
    source = {"error": "test"}
    file_path = tmp_path / "invalid_mode.json"
    #Act
    
    # Assert
    with pytest.raises(ValueError): #  An invalid file mode should trigger an exception when opening the file.
        op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="invalid", indent=2)

def test_to_json_file_with_non_serializable_object_should_raise_type_error(tmp_path):
    #Arange
    source = {"non_serializable": lambda x: x} # Lambda functions cannot be JSON serialized.
    file_path = tmp_path / "non_serializable.json"
    #Act
    
    #Assert
    with pytest.raises(TypeError):
        op.to_json_file(source_object=source, json_file_path=str(file_path), file_open_mode="w", indent=2)

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