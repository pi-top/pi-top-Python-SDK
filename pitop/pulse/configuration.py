from math import pow
from smbus import SMBus
from pitopcommon.logger import PTLogger

_bus_id = 1
_device_addr = 0x24

_speaker_bit = 0
_mcu_bit = 1
_eeprom_bit = 2
_16khz_bit = 3

#######################
# INTERNAL OPERATIONS #
#######################


def __get_addr_for_bit(bit):
    if bit in [0, 1, 2, 3]:
        PTLogger.debug("bit:  " + str(bit))
        addr = int(pow(2, bit))
        PTLogger.debug("addr: " + str(addr))
        return addr
    else:
        PTLogger.warning("Internal ERROR: invalid bit; cannot get address")
        return -1


def __get_bit_string(value):
    """INTERNAL. Get string representation of an int in binary"""

    return "{0:b}".format(value).zfill(8)


def __update_device_state_bit(bit, value):
    """INTERNAL. Set a particular device state bit to enable or disable a particular function"""

    # Bits:  0x0000
    # Index:   3210

    if bit not in [0, 1, 2, 3]:
        PTLogger.warning("Error: Not a valid state bit")
        return False

    try:
        current_state = __read_device_state()
        PTLogger.debug("Current device state: " +
                       __get_bit_string(current_state))

    except Exception:
        PTLogger.warning(
            "Error: There was a problem getting the current device state")
        return False

    # Get the bit mask for the new state
    new_state = __get_addr_for_bit(bit)

    if value == 0:
        new_state = ~new_state

    # Check if there is anything to do
    if (value == 1 and (new_state & current_state) != 0) or (value == 0 and (~new_state & ~current_state) != 0):
        PTLogger.debug("Warning: Mode already set, nothing to send")
        return True

    if value == 0:
        new_state = new_state & current_state
    else:
        new_state = new_state | current_state

    # Combine the old with the new and send
    return __write_device_state(new_state)


def __verify_device_state(expected_state):
    """INTERNAL. Verify that that current device state matches that expected"""

    current_state = __read_device_state()

    if expected_state == current_state:
        return True

    else:
        PTLogger.warning("Error: Device write verification failed. Expected: " +
                         __get_bit_string(expected_state) + " Received: " + __get_bit_string(current_state))
        return False


def __write_device_state(state):
    """INTERNAL. Send the state bits across the I2C bus"""

    try:
        PTLogger.debug("Connecting to bus...")
        i2c_bus = SMBus(_bus_id)

        state_to_send = 0x0F & state

        PTLogger.debug("Writing new state:    " +
                       __get_bit_string(state_to_send))
        i2c_bus.write_byte_data(_device_addr, 0, state_to_send)

        result = __verify_device_state(state_to_send)

        if result is True:
            PTLogger.debug("OK")
        else:
            PTLogger.warning("Error: New state could not be verified")

        return result

    except Exception:
        PTLogger.warning("Error: There was a problem writing to the device")
        return False


def __read_device_state():
    """INTERNAL. Read from the I2C bus to get the current state of the pulse. Caller should handle exceptions"""

    try:
        PTLogger.debug("Connecting to bus...")
        i2c_bus = SMBus(_bus_id)

        current_state = i2c_bus.read_byte(_device_addr) & 0x0F

        return int(current_state)

    except Exception:
        PTLogger.warning("Error: There was a problem reading from the device")
        # Best to re-raise as we can't recover from this
        raise


def __reset_device_state(enable):
    """Reset the device state bits to the default enabled or disabled state"""

    clean_enable_state = __get_addr_for_bit(_eeprom_bit)
    clean_disable_state = __get_addr_for_bit(
        _speaker_bit) | __get_addr_for_bit(_mcu_bit)

    state_to_send = clean_enable_state if enable else clean_disable_state
    return __write_device_state(state_to_send)


#######################
# EXTERNAL OPERATIONS #
#######################

def reset_device_state(enable):
    """reset_device_state: Deprecated"""
    PTLogger.info(
        "'reset_device_state' function has been deprecated, and can likely be removed. "
        "If you experience problems, please see documentation for instructions."
    )
    return False


def enable_device():
    PTLogger.info(
        "'enable_device' function has been moved to pt-device-manager, and is handled automatically."
    )
    return False


def disable_device():
    PTLogger.info(
        "'disable_device' function has been moved to pt-device-manager, and is handled automatically."
    )
    return False


def set_microphone_sample_rate_to_16khz():
    """Set the appropriate I2C bits to enable 16,000Hz recording on the microphone"""

    return __update_device_state_bit(_16khz_bit, 1)


def set_microphone_sample_rate_to_22khz():
    """Set the appropriate I2C bits to enable 22,050Hz recording on the microphone"""

    return __update_device_state_bit(_16khz_bit, 0)


# GET STATE

def speaker_enabled():
    """Get whether the speaker is enabled"""

    return (__read_device_state() & __get_addr_for_bit(_speaker_bit)) == 0


def mcu_enabled():
    """Get whether the onboard MCU is enabled"""

    return (__read_device_state() & __get_addr_for_bit(_mcu_bit)) == 0


def eeprom_enabled():
    """Get whether the eeprom is enabled"""

    return (__read_device_state() & __get_addr_for_bit(_eeprom_bit)) != 0


def microphone_sample_rate_is_16khz():
    """Get whether the microphone is set to record at a sample rate of 16,000Hz"""

    return (__read_device_state() & __get_addr_for_bit(_16khz_bit)) != 0


def microphone_sample_rate_is_22khz():
    """Get whether the microphone is set to record at a sample rate of 22,050Hz"""

    return (__read_device_state() & __get_addr_for_bit(_16khz_bit)) == 0
