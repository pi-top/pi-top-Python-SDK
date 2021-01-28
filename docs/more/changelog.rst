=====================================================
Changelog
=====================================================

Release v0.14.1 (2021/01/28)
------------------------------

- Add PiTop & AlexRobot docs
- Reorganise api_core elements subsections

Release v0.14.0 (2021/01/25)
------------------------------

- Buttons can only be used by a single process
- Suppress ultrasonic sensor warning messages
- Increase ultrasonic sensor detection range

Release v0.13.3 (2021/01/24)
------------------------------

- Convert image to array before checking dimensional size for RGB conversion

Release v0.13.2 (2021/01/24)
------------------------------

- Use 'ImageFunctions' to handle all image conversion
- Clarify when/why it is able to do channel conversion

Release v0.13.1 (2021/01/24)
------------------------------

- Set line detector default image format to 'PIL'

Release v0.13.0 (2021/01/23)
------------------------------

- Add initial 'PiTop' and 'RobotAlex' top-level objects
- Support line-following with 'RobotAlex'
- Add ImageFunctions module in pitop.core for globally useful functions
- Camera now manages its format as a property. Deprecated format parameter
  in functions

Release v0.12.1 (2021/01/18)
------------------------------

- Fix broken reference to OLED's internal canvas

Release v0.12.0 (2021/01/18)
------------------------------

- Use common lib singleton metaclass
- Upgrade on installing from docs/requirements.txt
- Clean up battery component
- Always use 2 leading underscores for private functions and member variables
- Fix motor examples to match robot configuration ports and params
- Fix changelog formatting

Release v0.11.0 (2021/01/13)
------------------------------

- Monitor OLED lock files using inotify to add events for user using the OLED
- Improve miniscreen button importing to speed miniscreen imports
- Handle Ctrl+C in OLED CLI
- CLI main function returns exit code for entry point script
- Drop '_set_exclusive_mode' for miniscreen objects in favour of constructor
  argument
- Move 'miniscreen.buttons.buttons' to 'miniscreen.buttons'
- Move 'miniscreen.oled.oled' to 'miniscreen.oled'

Release v0.10.1 (2021/01/12)
------------------------------

- Fix recursion issue when resetting OLED

Release v0.10.0 (2021/01/11)
------------------------------

- Use parameters property, not function
- Remove unused zmq dependency (handled in common lib)
- OLED uses controller class
- Add additional top-level OLED properties for size and mode
- Add additional top-level OLED functions for contrast
- Canvas and FPS regulators are now private
- Add 'pi-top oled spi' command for changing SPI bus
- Fix test imports
- Some misc syntax fixes

Release v0.9.0 (2021/01/07)
------------------------------

- Migrate deprecated CLIs to python3-pitop-migr

Release v0.8.1 (2021/01/04)
------------------------------

- Update GitHub CI - only build on master; publish to PyPI on release

Release v0.8.0 (2020/12/30)
------------------------------

- Rename 'help' CLI to 'support'

Release v0.7.0 (2020/12/22)
------------------------------

- Fix detection of legacy peripherals

Release v0.6.2 (2020/12/17)
------------------------------

- Set DISPLAY environment variable to plot IMU data

Release v0.6.1 (2020/12/17)
------------------------------

- Add missing init file

Release v0.6.0 (2020/12/17)
------------------------------

- Add IMU CLI

Release v0.5.1 (2020/12/17)
------------------------------

- Update docs links

Release v0.5.0 (2020/12/17)
------------------------------

- Update servo motor classes to latest firmware specification
- Add new servo functionality
- Replace '.format' with f-strings
- Flake8 uses per-file ignores
- Ignore RPi.GPIO RuntimeError when running tests
- Update package to specify 3.7 and above

Release v0.4.2 (2020/12/17)
------------------------------

- Initial IMU implementation

Release v0.4.1 (2020/12/16)
------------------------------

- 'pi-top Keyboard' --> 'Keyboard Input'
- 'pi-top Camera' --> 'USB Camera'
- Move to "helpers" section in the docs
- Add events to PMA Ultrasonic Sensor example

Release v0.4.0 (2020/12/16)
------------------------------

- Add missing pages to docs
- Update examples and mocking in docs as necessary
- Add pt-project-files as recommended dependency
- Remove TODOs

Release v0.3.9 (2020/12/16)
------------------------------

- Reorganize examples in docs

Release v0.3.8 (2020/12/15)
------------------------------

- Update docs - add overview page, add placeholders for all API subsystems

Release v0.3.7 (2020/12/15)
------------------------------

- Fix display callback API

Release v0.3.6 (2020/12/15)
------------------------------

- Remove pi-topPULSE config methods
- Fix common lib mocking to support inclusion of Singleton internal methods

Release v0.3.5 (2020/12/14)
------------------------------

- Add missing return statement in OLED API

Release v0.3.4 (2020/12/15)
------------------------------

- Supplement 'Breaks' with 'Replaces'

Release v0.3.3 (2020/12/14)
------------------------------

- Breaks with python3-pt-oled (<< 2.0.0)

Release v0.3.2 (2020/12/14)
------------------------------

- Breaks with python3-pt-oled (pt-oled)

Release v0.3.1 (2020/12/14)
------------------------------

- Breaks with pt-device-manager << 4.0.0 (CLI utils)

Release v0.3.0 (2020/12/14)
------------------------------

- Do not break python3-pt-oled

Release v0.2.6 (2020/12/14)
------------------------------

- Set default OLED CLI force argument to False

Release v0.2.5 (2020/12/14)
------------------------------

- Fix battery API

Release v0.2.4 (2020/12/14)
------------------------------

- Check for available displays before opening browser in help CLI

Release v0.2.3 (2020/12/14)
------------------------------

- Add help section to CLI, including support for opening a browser directing
  to the first recommended available docs URL

Release v0.2.2 (2020/12/14)
------------------------------

- Make miniscreen buttons top-level object a singleton, to ensure that
  pt-sys-oled can correctly set 'exclusive mode' for the application scope

Release v0.2.1 (2020/12/13)
------------------------------

- Fix changelog date

Release v0.2.0 (2020/12/13)
------------------------------

- Move support for deprecated user libs to python3-pitop-depr (to be dropped
  at a later date)

Release v0.1.0 (2020/11/04)
------------------------------

- Initial release of package
