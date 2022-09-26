import shutil
import tempfile
from os import path

from pitop.common.configuration_file import add_section, has_section, remove_section
from tests.utils import file_content_is_identical

ASSETS_FOLDER = f"{path.dirname(path.realpath(__file__))}/assets/configuration_file/"


def test_has_section():
    file_without_section = f"{ASSETS_FOLDER}/original.txt"
    file_with_section = f"{ASSETS_FOLDER}/one_section.txt"

    assert has_section("/tmp/this-file-doesnt-exist.asd", title="any-title") is False
    assert has_section(file_without_section, "any") is False
    assert has_section(file_with_section, "any") is False
    assert has_section(file_with_section, "test-add-section") is True


def test_add_section():
    original_file = f"{ASSETS_FOLDER}/original.txt"
    expected_file = f"{ASSETS_FOLDER}/one_section.txt"

    with tempfile.NamedTemporaryFile("w+t") as tmp_file:
        shutil.copy2(original_file, tmp_file.name)

        add_section(
            filename=tmp_file.name,
            title="test-add-section",
            description="This is a description",
            notes="this is a note",
            content="""
A=1
B=2
C=3
""",
        )
        assert file_content_is_identical(tmp_file.name, expected_file) is True


def test_remove_section():
    file_without_section = f"{ASSETS_FOLDER}/original.txt"
    file_with_section = f"{ASSETS_FOLDER}/one_section.txt"

    with tempfile.NamedTemporaryFile("w+t") as tmp_file:
        shutil.copy2(file_with_section, tmp_file.name)

        # Remove an existing section
        remove_section(
            filename=tmp_file.name,
            title="test-add-section",
        )
        assert file_content_is_identical(tmp_file.name, file_without_section) is True

        # Removing a non-existant-section doesn't modify the file
        remove_section(
            filename=tmp_file.name,
            title="non-existant-section",
        )
        assert file_content_is_identical(tmp_file.name, file_without_section) is True


def test_remove_section_on_file_with_several_sections():
    file_with_two_sections = f"{ASSETS_FOLDER}/two_sections.txt"
    file_with_one_section = f"{ASSETS_FOLDER}/one_section.txt"

    with tempfile.NamedTemporaryFile("w+t") as tmp_file:
        shutil.copy2(file_with_two_sections, tmp_file.name)

        remove_section(
            filename=tmp_file.name,
            title="test-add-section-2",
        )
        assert (
            file_content_is_identical(
                tmp_file.name, file_with_one_section, match_eof=False
            )
            is True
        )
