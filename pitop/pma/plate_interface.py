from threading import Lock, Thread
from time import sleep

from pitop.core.smbus_device import SMBusDevice
from pitop.core.logger import PTLogger
from pitop.core.singleton import Singleton
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

        with self._mcu_thread_lock:

            if self._mcu_connected:
                PTLogger.debug("Already connected to MCU")
                return

            PTLogger.debug("Connecting to Plate MCU...")

            try:
                self._device_mcu = SMBusDevice(1, PlateRegisters.I2C_ADDRESS_PLATE_MCU)
                self._device_mcu.connect()

                self._mcu_connected = True

                self._heartbeat_thread = Thread(target=self._heartbeat_thread_loop, daemon=True)
                self._heartbeat_thread.start()

            except Exception as e:
                self._disconnect_mcu()
                raise IOError("Unable to connect to plate (over I2C). " + str(e)) from None

    def _disconnect_mcu(self):

        with self._mcu_thread_lock:
            if self._mcu_connected is False:
                return

            PTLogger.debug("Disconnecting from MCU...")

            self._mcu_connected = False

            self._heartbeat_thread.join()
            self._heartbeat_thread = None

            if self._device_mcu is not None:
                self._device_mcu.disconnect()

    def _heartbeat_thread_loop(self):

        while self._mcu_connected:

            with self._mcu_thread_lock:
                if self._mcu_connected:
                    PTLogger.debug("Sending heartbeat")
                    self._device_mcu.write_byte(PlateRegisters.REGISTER_HEARTBEAT,
                                                PlateRegisters.HEARTBEAT_SECONDS_BEFORE_SHUTDOWN)

            for _ in range(10):
                sleep(PlateRegisters.HEARTBEAT_SEND_INTERVAL_SECONDS / 10)
                if self._mcu_connected is False:
                    break

        PTLogger.debug("Exiting heartbeat loop")
