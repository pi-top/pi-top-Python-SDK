#!/bin/bash -e

# Add the path for sphinx-apidoc to PATH if on Jenkins
if [[ -d "/var/lib/jenkins/.local/bin" ]]; then
	PATH="$PATH:/var/lib/jenkins/.local/bin/"
fi

# Change the script directory
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "${CURRENT_DIR}" || exit 1

pip3 install gpiozero

# Note that all parameters after the source <path> arg are for EXCLUDING files from doc generation
sphinx-apidoc -M -T --implicit-namespaces -o source ../src/ptpma/ 2>&1 | tee /tmp/sphinx-output.txt
make html 2>&1 | tee -a /tmp/sphinx-output.txt

if grep "WARNING: autodoc" '/tmp/sphinx-output.txt' >/dev/null; then
	echo "FAIL: autodoc warnings encountered"
	exit 1
else
	echo "SUCCESS: No autodoc warnings encountered"
fi
