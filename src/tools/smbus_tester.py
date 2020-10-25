from smbus2 import SMBus
bus = SMBus(1)
while True:
    data = bus.read_i2c_block_data(0x04, 0x75, 4)
    # data = bus.read_i2c_block_data(0x04, 0x7A, 4)
    # data = bus.read_i2c_block_data(0x04, 0x7A, 4)
    print(data)
