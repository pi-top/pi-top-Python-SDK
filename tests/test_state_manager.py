import uuid
from pathlib import Path

import pytest

from pitop.common.state_manager import StateManager


@pytest.fixture
def state_manager():

    # Generate a random name for the state file to avoid conflicts with concurrent tests
    manager = StateManager(str(uuid.uuid4()))
    yield manager

    # Cleanup after tests
    state_file = Path(manager.path)
    if state_file.exists():
        state_file.unlink()
    if state_file.parent.exists():
        state_file.parent.rmdir()


def test_singleton_pattern():
    # Test that names refer to the same instance of state manager
    manager1 = StateManager("some_name")
    manager2 = StateManager("some_name")
    assert manager1 is manager2

    manager3 = StateManager("some_other_name")
    assert manager1 is not manager3

    # cleanup
    for manager in [manager1, manager3]:
        state_file = Path(manager.path)
        if state_file.exists():
            state_file.unlink()
        if state_file.parent.exists():
            state_file.parent.rmdir()


def test_state_file_creation(state_manager):
    # Test that the state file is created
    state_file = Path(state_manager.path)
    assert state_file.exists()
    assert state_file.is_file()


def test_set_and_get(state_manager):
    # Test that set() and get() work
    state_manager.set("test_section", "test_key", "test_value")
    assert state_manager.get("test_section", "test_key") == "test_value"


def test_get_with_fallback(state_manager):
    # Test that get() with a fallback value works
    fallback_value = "default"
    value = state_manager.get("nonexistent", "nonexistent", fallback_value)
    assert value == fallback_value


def test_get_nonexistent_raises(state_manager):
    # Test that get() with a nonexistent key raises an exception
    with pytest.raises(Exception):
        state_manager.get("nonexistent", "nonexistent")


def test_exists():
    # Test non-existent state
    assert StateManager.exists("nonexistent_package") is False

    # Create state and test again
    StateManager("some_package")
    assert StateManager.exists("some_package")


def test_folder(state_manager):
    assert StateManager.folder(state_manager.name) == f"/tmp/{state_manager.name}"


def test_persistence(state_manager):
    # Set a value
    state_manager.set("test_section", "test_key", "test_value")

    # Create a new instance for same name (should load existing state)
    new_manager = StateManager(state_manager.name)
    assert new_manager.get("test_section", "test_key") == "test_value"


def test_set_creates_section(state_manager):
    # Test that set() creates a new section if it doesn't exist
    state_manager.set("new_section", "key", "value")
    assert state_manager.get("new_section", "key") == "value"


def test_set_raises_on_invalid_section_type(state_manager):
    # Test that set() raises an exception when the section is not a string
    for data in [
        None,
        1,
        1.0,
        True,
        object(),
        [1, 2],
        {"hey": "ho"},
        "",
        b"somedata",
    ]:
        with pytest.raises(ValueError):
            state_manager.set(data, "some_key", "value")


def test_set_raises_on_invalid_key_type(state_manager):
    # Test that set() raises an exception when the key is not a string
    for data in [
        None,
        1,
        1.0,
        True,
        object(),
        [1, 2],
        {"hey": "ho"},
        "",
        b"somedata",
    ]:
        with pytest.raises(ValueError):
            state_manager.set("some_section", data, "value")


def test_multiple_values_in_section(state_manager):
    # Test handling multiple key-value pairs in the same section
    state_manager.set("test_section", "key1", "value1")
    state_manager.set("test_section", "key2", "value2")
    assert state_manager.get("test_section", "key1") == "value1"
    assert state_manager.get("test_section", "key2") == "value2"


def test_remove_key_raises_on_nonexistent_key(state_manager):
    # Test that remove_key() raises an exception on nonexistent key
    state_manager.set("section", "key", "value")
    with pytest.raises(ValueError):
        state_manager.remove_key("section", "nonexistent_key")


def test_remove_key_raises_on_nonexistent_section(state_manager):
    # Test that remove_key() raises an exception on nonexistent section
    with pytest.raises(ValueError):
        state_manager.remove_key("nonexistent_section", "nonexistent_key")


def test_remove_section_raises_on_nonexistent_section(state_manager):
    # Test that remove_section() raises an exception on nonexistent section
    with pytest.raises(ValueError):
        state_manager.remove_section("nonexistent_section")


def test_remove_section_removes_all_keys(state_manager):
    # Test that remove_section() removes all keys in the section

    # Create section with two keys
    state_manager.set("test_section", "key1", "value1")
    state_manager.set("test_section", "key2", "value2")

    # Check that values are set
    assert state_manager.get("test_section", "key1") == "value1"
    assert state_manager.get("test_section", "key2") == "value2"

    # Remove section
    state_manager.remove_section("test_section")

    # Check that both keys are removed
    with pytest.raises(Exception):
        state_manager.get("test_section", "key1")
    with pytest.raises(Exception):
        state_manager.get("test_section", "key2")


def test_remove_key_removes_key_from_section(state_manager):
    # Test that remove_key() removes a key

    # Create section with two keys
    state_manager.set("test_section", "key1", "value1")
    state_manager.set("test_section", "key2", "value2")

    # Check that both keys are set
    assert state_manager.get("test_section", "key1") == "value1"
    assert state_manager.get("test_section", "key2") == "value2"

    # Remove key1
    state_manager.remove_key("test_section", "key1")

    # Check that key1 is removed
    with pytest.raises(Exception):
        state_manager.get("test_section", "key1")

    # Check that key2 is still set
    assert state_manager.get("test_section", "key2") == "value2"
