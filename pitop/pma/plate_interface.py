from threading import Lock, Thread
from time import sleep

from pitopcommon.smbus_device import SMBusDevice
from pitopcommon.logger import PTLogger
from pitopcommon.singleton import Singleton
from .common.plate_registers import PlateRegisters


class PlateInterface(metaclass=Singleton):

    def __init__(self):

        self.__device_mcu = None
        self.__mcu_connected = False
        self.__mcu_thread_lock = Lock()
        self.__heartbeat_thread = None

    def __del__(self):
        self.__disconnect_mcu()

    def get_device_mcu(self):

        self.__connect_mcu()

        # Return the SMBusDevice instance
        return self.__device_mcu

    def __connect_mcu(self):
        if self.__mcu_connected:
            PTLogger.debug("Already connected to MCU")
            return

        PTLogger.debug("Connecting to Plate MCU...")
        try:
            self.__device_mcu = SMBusDevice(1, PlateRegisters.I2C_ADDRESS_PLATE_MCU)
            self.__device_mcu.connect()
            self.__mcu_connected = True
            self.__send_heartbeat()
        except Exception:
            self.__disconnect_mcu()
            raise

        self.__heartbeat_thread = Thread(target=self.__heartbeat_thread_loop, daemon=True)
        self.__heartbeat_thread.start()

    def __disconnect_mcu(self):
        if self.__mcu_connected is False:
            return

        PTLogger.debug("Disconnecting from MCU...")

        self.__mcu_connected = False

        if self.__heartbeat_thread is not None:
            self.__heartbeat_thread.join()
            self.__heartbeat_thread = None

        if self.__device_mcu is not None:
            self.__device_mcu.disconnect()

    def __send_heartbeat(self):
        PTLogger.debug("Sending heartbeat")
        try:
            self.__device_mcu.write_byte(PlateRegisters.REGISTER_HEARTBEAT,
                                         PlateRegisters.HEARTBEAT_SECONDS_BEFORE_SHUTDOWN)
        except OSError:
            self.__mcu_connected = False
            raise IOError("Error communicating with Foundation/Expansion plate. Make sure it's connected to your pi-top.") from None

    def __heartbeat_thread_loop(self):
        while self.__mcu_connected:

            with self.__mcu_thread_lock:
                self.__send_heartbeat()

            for _ in range(10):
                sleep(PlateRegisters.HEARTBEAT_SEND_INTERVAL_SECONDS / 10)
                if self.__mcu_connected is False:
                    break

        PTLogger.debug("Exiting heartbeat loop")
