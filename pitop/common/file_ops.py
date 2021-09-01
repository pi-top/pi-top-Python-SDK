from os import close, utime
from re import compile
from shutil import copystat, move
from tempfile import NamedTemporaryFile, mkstemp


def sed_inplace(filename, pattern, repl):
    """Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`."""
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = compile(pattern)

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    # Overwrite the original file with the munged temporary file in a
    # manner preserving file attributes (e.g., permissions).
    copystat(filename, tmp_file.name)
    move(tmp_file.name, filename)


def touch_file(fname, times=None):
    with open(fname, "a"):
        utime(fname, times)


def create_temp_file():
    temp_file_tuple = mkstemp()
    close(temp_file_tuple[0])

    return temp_file_tuple[1]
