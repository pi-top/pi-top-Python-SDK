from os import get_terminal_size


class StdoutFormat:
    BLUE = "\033[94m"
    BOLD = '\033[1m'
    DIM = "\033[2m"
    ENDC = '\033[0m'
    GREEN = '\033[92m'
    RED = "\033[91m"
    UNDERLINE = "\033[4m"
    WHITE = "\033[97m"
    YELLOW = "\033[93m"

    @classmethod
    def bold(cls, text):
        return f"{cls.BOLD}{text}{cls.ENDC}"

    @classmethod
    def dim(cls, text):
        return f"{cls.DIM}{text}{cls.ENDC}"

    @classmethod
    def underline(cls, text):
        return f"{cls.UNDERLINE}{text}{cls.ENDC}"

    @classmethod
    def print_header(cls, header):
        print(f"{'='*(get_terminal_size().columns)}")
        print(f"{cls.bold(header)}")
        print(f"{'='*(get_terminal_size().columns)}")

    @classmethod
    def print_section(cls, section):
        print(f"= {cls.dim(section)} {'='*(get_terminal_size().columns - len(section) - 3)}")

    @classmethod
    def print_subsection(cls, section):
        print(f"- {cls.dim(section)} {'-'*(get_terminal_size().columns - len(section) - 3)}")

    @classmethod
    def print_line(cls, content, level=1):
        indentation_level = "  "*level
        print(f"{indentation_level}{cls.DIM}└{cls.ENDC} {content}")

    @classmethod
    def clickable_text(cls, text, url):
        return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"

    @classmethod
    def print_checkbox_line(cls, title, text, url, status):
        print(f"[ {cls.GREEN}{'✓' if status else ' '}{cls.ENDC} ]", end=" ")
        print(f"{cls.bold(title)}: {text}\n\t{cls.clickable_text(url, url) if status else url}", end=" ")
        print("")
