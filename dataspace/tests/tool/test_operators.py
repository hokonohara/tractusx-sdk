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
import json
import os
import sys
import time
import io
import datetime
import pytest
from datetime import timezone
from shutil import copyfile
from dataspace.tools import op

#------------TEST VARIABLES--------------------------

@pytest.fixture
def data_for_test(complex_json_for_test): #Simple data examples
    return {
        "empty_string": "",
        "bytes": bytes(),
        "bytearray": bytearray(),
        "string_whitespace": " ",
        "bytes_whitespace": bytes(" ", 'utf-8'),
        "bytearray_whitespace": bytearray(" ", 'utf-8'),   
        "int": 0,
        "boolean": False,
        "None": None,
        "array": [1, 2, 3],
        "empty_dict": {},
        "float": 0.0,
        "set": set(),
        "tuple": tuple(),
        "date": datetime.datetime.now(),
        "mixed_list": [1, "two", 3.0, True, None],
        "non_ASCII": "こんにちは",
        "utf-8_encoded": '{"saludo": "¡Hola, mundo!", "emoji": "😊"}',
        "iso-8859_encoded":'{"mensaje": "¡Olé! – ñandú"}',
        "non_string_key_dict": {1: "one", 2: "two"},
        "extra_comma" : '{"name": "John", "age": 30,}',
        "unquoted_key" : '{name: "John", age: 30}',
        "missing_bracket" : '{"name": "John", "age": 30',
        "mismatching_bracket" : '{"name": "John"} "age": 30}',
        "unescaped_special_characters" : '{"name": "John \n Doe"}',
        "complex_valid_string":  complex_json_for_test,
        "complex_valid_bytes": complex_json_for_test.encode('utf-8'), #converts empty_string version to bytes
        "complex_valid_bytearray": bytearray(complex_json_for_test, 'utf-8'), #converts empty_string version to bytearray
        "unicode_valid": '{"name": "Jöhn", "age": 30}',
    }
    
@pytest.fixture
def complex_json_for_test(): #Complete JSON with variances for testing purposes
    return """{
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
# -----------------TESTS-----------------------------

#Function 1 - json_string_to_object

@pytest.mark.parametrize("type", ["empty_string", "bytes", "bytearray", "string_whitespace", "bytes_whitespace", "bytearray_whitespace"])
def test_json_string_to_object_with_empty_valid_input_should_return_JSONDecodeError(type, data_for_test):
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(data_for_test[type]) 
        
@pytest.mark.parametrize("type", ["int", "boolean", "None", "array", "empty_dict", "float", "set", "tuple", "date"])
def test_json_string_to_object_with_invalid_input_should_return_TypeError(type, data_for_test):
    with pytest.raises(TypeError):
        op.json_string_to_object(data_for_test[type]) 
                             
@pytest.mark.parametrize("entries", ["extra_comma","unquoted_key","missing_bracket","unescaped_special_characters"])
def test_json_string_to_object_with_invalid_JSON_format_should_return_JSONDecodeError(entries,data_for_test):
    with pytest.raises(json.JSONDecodeError):
        op.json_string_to_object(data_for_test[entries])
        
@pytest.mark.parametrize("entries", ["complex_valid_string","complex_valid_bytes", "complex_valid_bytearray", "unicode_valid"])
def test_json_string_to_object_with_valid_format_should_return_valid_JSON(entries,data_for_test):
    expected = json.loads(data_for_test[entries])
    assert op.json_string_to_object(data_for_test[entries]) == expected

#Function 2 - to_json

@pytest.mark.parametrize("type", ["empty_string", "int", "float", "boolean", "None", "array", "tuple", "empty_dict", "non_string_key_dict"])
def test_to_json_with_serializable_input_should_return_valid_json(type,data_for_test):
    assert op.to_json(data_for_test[type]) == json.dumps(data_for_test[type])
    
@pytest.mark.parametrize("type", ["bytes", "bytearray", "set", "date"])
def test_to_json_with_non_serializable_input_should_return_TypeError(type,data_for_test):
    with pytest.raises(TypeError):
        op.to_json(data_for_test[type])

def test_to_json_with_complex_data_should_return_valid_json(complex_json_for_test):
    expected = json.dumps(complex_json_for_test)
    assert op.to_json(complex_json_for_test) == expected
        
def test_to_json_with_indent_parameter_should_return_indented_json(complex_json_for_test):
    expected = json.dumps(complex_json_for_test, indent=4)
    assert op.to_json(complex_json_for_test, indent=4) == expected

def test_to_json_with_non_ascii_characters_ensure_ascii_option_works(data_for_test): #Specific for this method
    assert "\\u3053" in op.to_json(data_for_test["non_ASCII"], ensure_ascii=True)
    assert "こんにちは" in op.to_json(data_for_test["non_ASCII"], ensure_ascii=False)

def test_to_json_with_special_numbers(): #Specific for this method
    assert "NaN" in op.to_json({"value":math.nan})
    assert "Infinity" in op.to_json({"value":math.inf})

def test_to_json_with_custom_object_should_raise_TypeError(): #Specific edge case for this method
    #Arange
    class Custom:
        pass
    source = Custom()
    #Assert
    with pytest.raises(TypeError):# Custom objects are not serializable by default.
        op.to_json(source)

#Function 3 - to_json_file

@pytest.mark.parametrize("entries", ["complex_valid_string", "unicode_valid", "mixed_list", "None", "empty_dict" ])
def test_to_json_file_with_valid_input_should_write_valid_json(tmp_path, entries, data_for_test):
    #Assert
    file_path = tmp_path / "test_file.json"
    expected = json.dumps(data_for_test[entries], indent=2)
    #Act
    op.to_json_file(source_object=data_for_test[entries], json_file_path=str(file_path), file_open_mode="w", indent=2)
    #Assert
    assert file_path.read_text() == expected
    
def test_to_json_file_with_append_mode_should_append_valid_json(tmp_path, data_for_test):
    #Arange
    file_path = tmp_path / "append.json"
    file_path.write_text(data_for_test["complex_valid_string"]) #Using complex formats to check all works
    expected = data_for_test["complex_valid_string"] + json.dumps(data_for_test["unicode_valid"], indent=2)
    #Act
    op.to_json_file(source_object=data_for_test["unicode_valid"], json_file_path=str(file_path), file_open_mode="a", indent=2)
    #Assert
    assert file_path.read_text() == expected #The JSON data should be appended after the initial content.

def test_to_json_file_with_invalid_file_mode_should_raise_ValueError(tmp_path):
    with pytest.raises(ValueError): #  An invalid file mode should trigger an exception when opening the file.
        op.to_json_file(source_object="", json_file_path=str(tmp_path), file_open_mode="invalid", indent=2)

@pytest.mark.parametrize("entries", ["bytes", "bytearray", "set", "date"])
def test_to_json_file_with_non_serializable_object_should_raise_TypeError(tmp_path, entries, data_for_test):
    with pytest.raises(TypeError):
        op.to_json_file(source_object=data_for_test[entries], json_file_path=str(tmp_path/"non_serializable.json"), file_open_mode="w", indent=2)

#Function 4 - read_json_file

@pytest.mark.parametrize("entries", ["complex_valid_string","mixed_list", "utf-8_encoded", "unicode_valid"])
def test_read_json_file_with_valid_input_should_return_dict(tmp_path, entries, data_for_test):
    #Arange
    file_path = tmp_path / "read_file_test.json"
    file_path.write_text(json.dumps(data_for_test[entries], indent=2), encoding="utf-8")
    #Assert
    assert op.read_json_file(str(file_path)) == data_for_test[entries]

def test_read_json_file_with_nonexistent_file_should_raise_FileNotFoundError(tmp_path):
    with pytest.raises(FileNotFoundError):
        op.read_json_file(str(tmp_path/"nonexistent.json"))

@pytest.mark.parametrize("entries", ["empty_string","unquoted_key","missing_bracket","mismatching_bracket","unescaped_special_characters"])
def test_read_json_file_with_invalid_json_should_raise_JsonDecodeError(tmp_path, entries, data_for_test):
    #Arange
    file_path = tmp_path / "invalid.json"
    file_path.write_text(data_for_test[entries], encoding="utf-8")
    #Assert
    with pytest.raises(json.JSONDecodeError):
        op.read_json_file(str(file_path))

def test_read_json_file_with_different_encoding_should_return_correct_data(tmp_path,data_for_test):
    #Arange
    file_path = tmp_path / "latin1.json"
    file_path.write_text(json.dumps(data_for_test["iso-8859_encoded"], indent=2), encoding="iso-8859-1")
    #Assert
    assert op.read_json_file(str(file_path), encoding="iso-8859-1") == data_for_test["iso-8859_encoded"]

#Function 5 - path_exists

def test_path_exists_file(tmp_path):
    """
    Test path_exists: Existing file returns True.
    """
    file = tmp_path / "existing.txt"
    file.write_text("Test content")
    assert op.path_exists(str(file)) is True

def test_path_exists_nonexistent(tmp_path):
    """
    Test path_exists: Nonexistent file returns False.
    """
    file = tmp_path / "nonexistent.txt"
    assert op.path_exists(str(file)) is False

def test_path_exists_directory(tmp_path):
    """
    Test path_exists: Existing directory returns True.
    """
    directory = tmp_path / "subdir"
    directory.mkdir()
    assert op.path_exists(str(directory)) is True

def test_path_exists_relative_path(tmp_path, monkeypatch):
    """
    Test path_exists: Relative path is handled correctly.
    """
    file = tmp_path / "relative.txt"
    file.write_text("Relative file content")
    monkeypatch.chdir(tmp_path)
    assert op.path_exists("relative.txt") is True

def test_path_exists_trailing_slash(tmp_path):
    """
    Test path_exists: Directory path with a trailing separator returns True.
    """
    directory = tmp_path / "dir_with_slash"
    directory.mkdir()
    path_with_slash = str(directory) + os.sep
    assert op.path_exists(path_with_slash) is True

def test_path_exists_with_none_should_raise_TypeError():
    """
    Test path_exists: Passing None as input should raise TypeError.
    """
    with pytest.raises(TypeError):
        op.path_exists(None)

def test_path_exists_with_symlink(tmp_path):
    """
    Test path_exists: Symbolic link to an existing file returns True.
    """
    target_file = tmp_path / "target.txt"
    target_file.write_text("Target content")
    symlink_file = tmp_path / "symlink.txt"
    try:
        os.symlink(str(target_file), str(symlink_file))
    except (AttributeError, NotImplementedError, OSError):
        pytest.skip("Symlink not supported or not enough privileges to execute test")
    assert op.path_exists(str(symlink_file)) is True

# Functions: make_dir and delete_dir

def test_create_and_delete_valid_directory_should_create_and_delete(tmp_path):
    """
    Test normal creation and deletion of a directory.
    """
    new_dir = tmp_path / "test_dir"
    # Ensure the directory does not exist yet.
    assert not new_dir.exists()
    # Create the directory using op.make_dir.
    result = op.make_dir(str(new_dir))
    assert new_dir.exists()
    # Delete the directory and verify deletion.
    deletion_result = op.delete_dir(str(new_dir))
    assert not new_dir.exists()

def test_make_dir_when_directory_already_exists(tmp_path):
    """
    Test that calling op.make_dir on an already existing directory works safely.
    """
    existing_dir = tmp_path / "existing_dir"
    existing_dir.mkdir()  # Pre-create the directory.
    result = op.make_dir(str(existing_dir))
    assert result is True
    assert existing_dir.exists()
    # Now delete the directory.
    deletion_result = op.delete_dir(str(existing_dir))
    assert deletion_result is True
    assert not existing_dir.exists()

def test_make_dir_invalid_input(tmp_path):
    """Edge case: op.make_dir should reject invalid inputs."""
    # An empty string should raise an error.
    with pytest.raises(Exception):
        op.make_dir("")
    # A non-string type (e.g., integer) should also raise an error.
    with pytest.raises(Exception):
        op.make_dir(123)

def test_delete_non_existing_directory(tmp_path):
    """Test that op.delete_dir returns False when the directory doesn't exist."""
    non_existing = tmp_path / "non_existing_dir"
    deletion_result = op.delete_dir(str(non_existing))
    assert deletion_result is False

def test_delete_directory_with_contents(tmp_path):
    """Test deletion of a non-empty directory (with files inside)."""
    dir_with_file = tmp_path / "dir_with_file"
    op.make_dir(str(dir_with_file))
    # Create a file inside the directory.
    file_inside = dir_with_file / "sample.txt"
    file_inside.write_text("sample content")
    assert file_inside.exists()
    # Delete the directory and ensure all contents are removed.
    deletion_result = op.delete_dir(str(dir_with_file))
    assert deletion_result is True
    assert not dir_with_file.exists()

def test_make_dir_with_trailing_slash(tmp_path):
    """Test that op.make_dir accepts a directory path with a trailing slash."""
    dir_with_slash = str(tmp_path / "trailing_dir") + "/"
    result = op.make_dir(dir_with_slash)
    assert result is True
    created_dir = tmp_path / "trailing_dir"
    assert created_dir.exists() and created_dir.is_dir()
    # Delete using the same input.
    deletion_result = op.delete_dir(dir_with_slash)
    assert deletion_result is True
    assert not created_dir.exists()

def test_chained_make_and_delete(tmp_path):
    """Test sequential operations: multiple calls to make_dir and delete_dir."""
    chain_dir = tmp_path / "chain_dir"
    # First creation.
    assert op.make_dir(str(chain_dir)) is True
    # A second call should not cause issues.
    assert op.make_dir(str(chain_dir)) is True
    # Deleting should remove the directory.
    assert op.delete_dir(str(chain_dir)) is True
    # A subsequent deletion call returns False.
    assert op.delete_dir(str(chain_dir)) is False

def test_make_dir_with_custom_permissions(tmp_path):
    """Test op.make_dir with a custom permission setting."""
    perm_dir = tmp_path / "perm_dir"
    op.make_dir(str(perm_dir), permits=0o700)
    # On POSIX systems, check that the directory permissions match.
    if os.name != "nt":
        mode = perm_dir.stat().st_mode & 0o777
        assert mode == 0o700
    # Clean up.
    op.delete_dir(str(perm_dir))

@pytest.mark.skipif(os.name == "nt", reason="Symlink tests not supported on Windows by default")
def test_delete_symlinked_directory(tmp_path):
    """Test op.delete_dir on a symlinked directory."""
    target_dir = tmp_path / "target_dir"
    target_dir.mkdir()
    symlink_dir = tmp_path / "symlink_dir"
    os.symlink(str(target_dir), str(symlink_dir))
    # Confirm that the symlink exists.
    assert os.path.islink(symlink_dir)
    deletion_result = op.delete_dir(str(symlink_dir))
    assert deletion_result is True
    # The symlink should be gone while the target remains.
    assert not os.path.exists(symlink_dir)
    # Clean up the target.
    op.delete_dir(str(target_dir))

def test_delete_dir_invalid_input():
    """Edge case: op.delete_dir should reject invalid inputs."""
    with pytest.raises(Exception):
        op.delete_dir(None)
    with pytest.raises(Exception):
        op.delete_dir(456)
        
def test_make_and_delete_dir(tmp_path):
    """
    Test make_dir: Create a directory when it doesn't exist, and
    delete_dir: Remove the directory correctly.
    """
    dir_path = tmp_path / "new_dir"
    # Ensure the directory does not exist
    if op.path_exists(str(dir_path)):
        op.delete_dir(str(dir_path))
    op.make_dir(str(dir_path))
    assert os.path.isdir(str(dir_path))
    # Delete the directory
    op.delete_dir(str(dir_path))
    assert not op.path_exists(str(dir_path))
    # Deleting a non-existent directory should return False
    assert op.delete_dir(str(dir_path)) is False


# Functions: copy_file and move_file - Just wrappers - Should be already tested by shutils
def test_copy_and_move_file(tmp_path):
    """
    Test copy_file: Copy a file correctly,
    and move_file: Move the file to the destination.
    """
    # Create original file
    original = tmp_path / "original.txt"
    original.write_text("Original content")
    # Copy the file
    copy_dest = tmp_path / "copy.txt"
    op.copy_file(str(original), str(copy_dest))
    assert op.path_exists(str(copy_dest)) is True
    assert original.read_text() == copy_dest.read_text()
    # Move the copied file
    move_dest = tmp_path / "moved.txt"
    op.move_file(str(copy_dest), str(move_dest))
    assert not op.path_exists(str(copy_dest))  # The original copy should no longer exist
    assert op.path_exists(str(move_dest)) is True
    assert original.read_text() == move_dest.read_text()

# Functions: to_string and load_file
def test_to_string_and_load_file(tmp_path):
    """
    Test to_string: Read file as string;
    load_file: Load file into a BytesIO buffer.
    """
    content = "Test file content."
    file_path = tmp_path / "text.txt"
    file_path.write_text(content, encoding="utf-8")
    # Test to_string
    assert op.to_string(str(file_path)) == content
    # Test load_file
    buffer = op.load_file(str(file_path))
    assert isinstance(buffer, io.BytesIO)
    assert buffer.getvalue() == content.encode("utf-8")

# Function: delete_file
def test_delete_file(tmp_path):
    """
    Test delete_file: Successfully delete an existing file,
    and return False if the file does not exist.
    """
    file_path = tmp_path / "to_delete.txt"
    file_path.write_text("Delete this file")
    # Delete the existing file
    assert op.delete_file(str(file_path)) is True
    # Trying to delete again should return False
    assert op.delete_file(str(file_path)) is False

# Function: write_to_file
def test_write_to_file(tmp_path):
    """
    Test write_to_file: Write data to a file.
    """
    file_path = tmp_path / "output.txt"
    data = "Data to be written."
    # Write valid data
    assert op.write_to_file(data, str(file_path), "w", end="END") is True
    assert file_path.read_text(encoding=sys.stdout.encoding) == data + "END"
    # Writing an empty string or None should return False
    assert op.write_to_file("", str(file_path)) is False
    assert op.write_to_file(None, str(file_path)) is False

# Functions: timestamp, get_filedatetime and get_filedate - Wrapper methods
def test_timestamp_and_file_date_functions():
    """
    Test timestamp: Returns a numeric value or string,
    get_filedatetime and get_filedate: Return strings in the expected format.
    """
    ts_numeric = op.timestamp(string=False)
    ts_string = op.timestamp(string=True)
    assert isinstance(ts_numeric, float)
    # The string should be convertible to float without error
    float(ts_string)
    file_dt = op.get_filedatetime()
    file_d = op.get_filedate()
    # Check basic length and format (YYYYMMDD and YYYYMMDD_HHMMSS)
    assert len(file_d) == 8
    assert len(file_dt) >= 15

def test_timestamp_and_file_date_unvalid_timezone_should_raise_TypeError():
    """
    Test get_filedatetime and get_filedate with unrecognized timezone: Should raise TypeError.
    """
    with pytest.raises(TypeError):
        op.get_filedatetime(timezone="invalid", string=False)
        op.get_filedatetime(timezone="invalid", string=True)
    with pytest.raises(TypeError):
        op.get_filedate(timezone="invalid", string=False)
        op.get_filedate(timezone="invalid", string=True)

# Function: get_path_without_file - Wrapper method 
def test_get_path_with_file_should_return_its_path(tmp_path):
    """
    Test get_path_without_file: Extracts the directory path from a file path.
    """
    file_path = tmp_path / "subdir" / "file.txt"
    expected_dir = os.path.dirname(str(file_path))
    assert op.get_path_without_file(str(file_path)) == expected_dir
    
# Function: wait - Wrapper method
def test_wait(monkeypatch):
    """
    Test wait: Delegates to time.sleep and returns None.
    Uses monkeypatch to avoid an actual delay.
    """
    called = False
    def fake_sleep(seconds):
        nonlocal called
        called = True
    monkeypatch.setattr(time, "sleep", fake_sleep)
    result = op.wait(0.1)
    assert called is True
    assert result is None

# Function: get_attribute
def test_get_attribute():
    """
    Test get_attribute: Retrieves nested attributes from a dictionary.
    """
    source = {
        "a": {
            "b": {
                "c": 123
            }
        }
    }
    # Successful case: existing attribute
    assert op.get_attribute(source, "a.b.c") == 123
    # Default value case: non-existent attribute or invalid data
    assert op.get_attribute(source, "a.x.c", default_value="default") == "default"
    assert op.get_attribute(None, "a.b", default_value="default") == "default"
    # Case with empty path separator should return default
    assert op.get_attribute(source, "a.b.c", default_value="default", path_sep="") == "default"