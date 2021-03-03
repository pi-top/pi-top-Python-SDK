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


class StdoutTable:
    def __init__(self, column_separation=5, indent_level=1):
        self.longest_values_arr = []
        self.column_separation = column_separation
        self.indent_level = indent_level
        self.print_data_dict = {}
        self.title_format = StdoutFormat.print_section

    def clear(self):
        self.longest_values_arr = []
        self.print_data_dict = {}

    def add_section(self, title, data_arr):
        self.analyze_data(data_arr)
        self.print_data_dict[title] = data_arr

    def analyze_data(self, data_arr):
        while len(self.longest_values_arr) < len(data_arr):
            self.longest_values_arr.append(0)

        for data in data_arr:
            for i, value in enumerate(data):
                if len(str(value)) > self.longest_values_arr[i]:
                    self.longest_values_arr[i] = len(str(value))

    def print_data(self, data_arr):
        self.title_format = None
        self.add_section("", data_arr)
        self.print()

    def print(self):
        for title, data_arr in self.print_data_dict.items():
            if self.title_format:
                self.title_format(title)

            for data in data_arr:
                line = ""
                for i, value in enumerate(data):
                    string_length = self.longest_values_arr[i] + self.column_separation
                    if i == len(data) - 1:
                        string_length = self.longest_values_arr[i]
                    line += f"{value.ljust(string_length)}"

                StdoutFormat.print_line(line, level=self.indent_level)
