# def bytes2human(n):
#     """
#     >>> bytes2human(10000)
#     '9K'
#     >>> bytes2human(100001221)
#     '95M'
#     """
#     symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
#     prefix = {}
#     for i, s in enumerate(symbols):
#         prefix[s] = 1 << (i + 1) * 10
#     for s in reversed(symbols):
#         if n >= prefix[s]:
#             value = int(float(n) / prefix[s])
#             return '%s%s' % (value, s)
#     return "%sB" % n


def bytes2human(n, fmt="{0:0.2f}"):
    symbols = [
        ("YB", 2 ** 80),
        ("ZB", 2 ** 70),
        ("EB", 2 ** 60),
        ("PB", 2 ** 50),
        ("TB", 2 ** 40),
        ("GB", 2 ** 30),
        ("MB", 2 ** 20),
        ("KB", 2 ** 10),
        ("B", 2 ** 0),
    ]

    for suffix, v in symbols:
        if n >= v:
            value = float(n) / v
            return fmt.format(value) + suffix
    return "{0}B".format(n)


def strip_whitespace(line):
    return "".join(line.split())


def is_line_commented(line_to_check, delimiter="#"):
    stripped_line = strip_whitespace(line_to_check)
    return stripped_line.startswith(delimiter)


def get_commented_line(line_to_change, delimiter="#"):
    stripped_line = strip_whitespace(line_to_change)
    commented_line = delimiter + stripped_line
    return commented_line


def get_uncommented_line(line_to_change, delimiter="#"):
    return line_to_change.replace(delimiter, "")


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text
