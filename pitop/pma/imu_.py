#!/usr/bin/env python3

from .imu_controller import ImuController

class Imu:
    def __init__(self):
        self._imu_controller = ImuController()