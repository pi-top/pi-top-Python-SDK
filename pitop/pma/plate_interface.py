from threading import Lock, Thread
from time import sleep

from pitopcommon.smbus_device import SMBusDevice
from pitopcommon.logger import PTLogger
from pitopcommon.singleton import Singleton
from .common.plate_registers import PlateRegisters


@Singleton
class PlateInterface:

    def __init__(self):

        self._device_mcu = None
        self._mcu_connected = False
        self._mcu_thread_lock = Lock()
        self._heartbeat_thread = None

    def __del__(self):
        self._disconnect_mcu()

    def get_device_mcu(self):

        self._connect_mcu()

        # Return the SMBusDevice instance
        return self._device_mcu

    def _connect_mcu(self):
        if self._mcu_connected:
            PTLogger.debug("Already connected to MCU")
            return

        PTLogger.debug("Connecting to Plate MCU...")
        try:
            self._device_mcu = SMBusDevice(1, PlateRegisters.I2C_ADDRESS_PLATE_MCU)
            self._device_mcu.connect()
            self._mcu_connected = True
            self._send_heartbeat()
        except Exception:
            self._disconnect_mcu()
            raise

        self._heartbeat_thread = Thread(target=self._heartbeat_thread_loop, daemon=True)
        self._heartbeat_thread.start()

    def _disconnect_mcu(self):
        if self._mcu_connected is False:
            return

        PTLogger.debug("Disconnecting from MCU...")

        self._mcu_connected = False

        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join()
            self._heartbeat_thread = None

        if self._device_mcu is not None:
            self._device_mcu.disconnect()

    def _send_heartbeat(self):
        PTLogger.debug("Sending heartbeat")
        try:
            self._device_mcu.write_byte(PlateRegisters.REGISTER_HEARTBEAT,
                                        PlateRegisters.HEARTBEAT_SECONDS_BEFORE_SHUTDOWN)
        except OSError:
            self._mcu_connected = False
            raise IOError("Error communicating with Foundation/Expansion plate. Make sure it's connected to your pi-top.") from None

    def _heartbeat_thread_loop(self):
        while self._mcu_connected:

            with self._mcu_thread_lock:
                self._send_heartbeat()

            for _ in range(10):
                sleep(PlateRegisters.HEARTBEAT_SEND_INTERVAL_SECONDS / 10)
                if self._mcu_connected is False:
                    break

        PTLogger.debug("Exiting heartbeat loop")
