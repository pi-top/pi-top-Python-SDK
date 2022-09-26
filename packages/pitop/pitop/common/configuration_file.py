from pathlib import Path
from re import compile


def add_section(
    filename: str, title: str, description: str, content: str, notes: str = ""
) -> None:
    """Add a section to a configuration file with the following format:
# [<TITLE>] START
#
# <DESCRIPTION>
#
# Notes:
# <NOTES>
#
<CONTENT>
#
# [<APP_NAME>] END
    """
    text = f"""
# [{title}] START
#
# {description}
#
# Notes:
# {notes}
#
{content}
#
# [{title}] END"""
    with open(filename, "a") as f:
        f.write(text)


def remove_section(filename: str, title: str) -> None:
    """Removes a section of the provided title from the given filename.
    It assumes that the format of the block to remove is the following:
# [<TITLE>] START
#
# <DESCRIPTION>
#
# Notes:
# <NOTES>
#
<CONTENT>
#
# [<APP_NAME>] END
    """
    start_pattern = compile(rf"^(# \[{title}\] START)\n")
    finish_pattern = compile(rf"^(# \[{title}\] END)\n")
    delete_line = False

    with open(filename, "r") as fr:
        lines = fr.readlines()
        with open(filename, "w") as fw:
            for i, line in enumerate(lines):
                if (
                    line.strip() == ""
                    and i + 1 < len(lines)
                    and start_pattern.search(lines[i + 1]) is not None
                ):
                    delete_line = True
                if not delete_line:
                    fw.write(line)
                if finish_pattern.search(line) is not None:
                    delete_line = False


def has_section(filename: str, title: str) -> bool:
    """Checks if the provided file has a section with the given title."""
    if not Path(filename).exists():
        return False

    pattern = compile(rf"^(# \[{title}\] START)")

    with open(filename) as f:
        for line in f:
            if pattern.search(line) is not None:
                return True
    return False
