# Deprecated package routes

This directory allows for supporting the use of Python modules that have now been moved into this one.

| Deprecated Python Module | Deprecated Debian Package | Superceding Python Module | Superceding Debian Package |
| ------------------------ | ------------------------- |----- -------------------- | -------------------------- |
| `ptbuttons`              | `python3-pt-buttons`      | `pitop.miniscreen.buttons`| `python3-pitop`            |
| `ptoled`                 | `python3-pt-oled`         | `pitop.miniscreen.oled`   | `python3-pitop`            |
| `ptpma`                  | `python3-pt-pma`          | `pitop.pma`               | `python3-pitop`            |
| `ptprotoplus`            | `python3-pt-proto-plus`   | `pitop.protoplus`         | `python3-pitop`            |

The deprecated Debian packages are now provided from this source. They are dependent on `python3-pitop` and use it directly. In the future, these packages will be removed.
