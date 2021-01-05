#### <a name="details-stages"></a> Stages
* Header
	* Shows pt-diagnostics version, if installed via package
	* Shows timestamp
* Setup
	* Creates temporary folder to store logs
* Upgrades
	* Copies `/var/log/apt/term.log` and `/var/log/apt/history.log`
* OS
	* Gets current machine and the operating system from `uname`
	* Copies `/boot/config.txt` and `/boot/cmdline.txt`
	* Gets startup messages from kernel (`dmesg`)
	* Gets settings from `raspi-config`
	* Gets running processes (`ps aux`)
* Network
	* Copies `/etc/network/interfaces`
* Installed Software
	* Get apt sources (`/etc/apt/sources.list.d/*`)
	* Get installed software (`apt list --installed`)
* pi-top Software Info
	* Get log information for installed packages, if available
		* pt-os-dashboard
		* pt-device-manager
		* pt-notifications
	* Get status of all pi-top systemd services
* pi-top Hardware Info
	* Reads all values from pi-topHUB v2, if possible
* Finalise
	* Zip
	* Encrypt, if desired
	* Upload, if desired
