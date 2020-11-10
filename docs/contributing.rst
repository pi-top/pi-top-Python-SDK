=====================================================
Contributing
=====================================================

Contributions to the SDK are welcome! There are several ways to contribute.

Report a Bug or Issues
=====================================================

Before reporting a bug or creating an issue, make sure you go through our `Knowledge Base <https://knowledgebase.pi-top.com/>`_ and Forum_.

To report a bug or write an issue, go to the issue_ section in the repository_, click on the **New issue** button, and read the instructions.

Pull Requests
=====================================================

Before opening a pull request, please read the following.

Check existing Issues and Pull Requests
-----------------------------------------------------

Check to see if there are any existing Issues_ and/or `Pull Requests <https://github.com/pi-top/pi-top-Python-SDK/pulls>`_ related to the topic.

Documentation
-----------------------------------------------------

The documentation source lives in the docs_ folder. Contributions to the documentation are welcome but should be easy to read and understand.
Please submit documentation changes by opening an issue_.

Commit Messages and Pull Requests
-----------------------------------------------------

Commit messages should be concise but descriptive, and in the form of a patch
description, i.e. instructional not past tense ("Add LED example" not "Added
LED example").

Commits which close (or intend to close) an issue should include the phrase "fix #123" or "close #123" where `#123` is the issue number, as well as
include a short description, for example: "Add LED example (close #123)", and
pull requests should aim to match or closely match the corresponding issue
title.

Backwards Compatibility
-----------------------------------------------------

Every effort should be made to ensure that backwards compatibility is maintained. If this is not possible, then it may be queued up for a future breaking-change release. It is our intention to maintain backwards-compatibility after this SDK reaches v1.

Python Version Support
-----------------------------------------------------

The library is specifically developed for use with Python 3. In particular, it is aimed at the version of Python 3 that ships with the latest stable version of Raspberry Pi OS/Debian.

Python 2 has now reached end-of-life_, and so is not supported.


.. _docs: https://github.com/pi-top/pi-top-Python-SDK/tree/master/docs
.. _end-of-life: http://legacy.python.org/dev/peps/pep-0373/
.. _Forum: https://forum.pi-top.com/c/pi-top-software
.. _Issues: https://github.com/pi-top/pi-top-Python-API/issues
.. _issue: https://github.com/pi-top/pi-top-Python-API/issues
.. _repository: https://github.com/pi-top/pi-top-Python-SDK/tree/master/docs
