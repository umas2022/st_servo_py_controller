import sys
import time
import numpy as np

sys.path.append("..")
from STservo_sdk import *


from dataclasses import dataclass


@dataclass
class Motor:
    id: int
    min: int
    max: int
    init: int
    reverse: bool


class ArmController:
    def __init__(self, serial_port="COM4", baudrate=1000000):
        self.serial_port = serial_port
        self.baudrate = baudrate

        self.motor_1 = Motor(id=1, min=1024, max=3072, init=2048, reverse=False)
        self.motor_2 = Motor(id=2, min=0, max=2048, init=2048, reverse=True)
        self.motor_3 = Motor(id=3, min=0, max=2048, init=2048, reverse=True)
        self.motor_4 = Motor(id=4, min=1024, max=3072, init=2048, reverse=True)
        self.motor_5 = Motor(id=5, min=1024, max=3072, init=2048, reverse=False)
        self.motor_6 = Motor(id=6, min=1024, max=3072, init=2048, reverse=False)
        self.motors_list = [
            self.motor_1,
            self.motor_2,
            self.motor_3,
            self.motor_4,
            self.motor_5,
            self.motor_6,
        ]

        self.port_handler = PortHandler(self.serial_port)
        self.packet_handler = sts(self.port_handler)

    def hardware_init(self) -> None:
        """
        Initialize the hardware by opening the port and setting the baudrate.
        """
        # Open port
        if self.port_handler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            return False
        # Set port baudrate
        if self.port_handler.setBaudRate(self.baudrate):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            return False
        return True

    def online_check(self) -> bool:
        """
        check if the motors are online by pinging each motor.
        """
        offline_list = []
        for each_motor in self.motors_list:
            sts_model_number, sts_comm_result, sts_error = self.packet_handler.ping(each_motor.id)
            if sts_comm_result != COMM_SUCCESS:
                print(f"Motor {each_motor.id} is offline")
                offline_list.append(each_motor.id)
            if sts_error != 0:
                print("%s" % self.packet_handler.getRxPacketError(sts_error))
        if len(offline_list) == 0:
            print("All motors are online")
            return True
        else:
            print(f"Offline motors: {offline_list}")
            return False

    def _get_raw_position(self, norm_pos: int, motor: Motor) -> int:
        """
        position convert: normalized position to raw position
        """
        if motor.reverse:
            return motor.max - norm_pos
        else:
            return motor.min + norm_pos

    def _get_norm_position(self, raw_pos: int, motor: Motor) -> int:
        """
        position convert: raw position to normalized position
        """
        if motor.reverse:
            return motor.max - raw_pos
        else:
            return raw_pos - motor.min

    def _move_to_absolute(self, motor: Motor, position: int, speed: int, acc: int) -> bool:
        range_check = True
        target_pos = np.clip(position, motor.min, motor.max)
        if target_pos != position:
            print(f"Target position {position} is out of range for motor {motor.id}.")
            range_check = False
        sts_comm_result, sts_error = self.packet_handler.RegWritePosEx(motor.id, target_pos, speed, acc)
        return range_check

    def _move_to_offset(self, motor: Motor, offset: int, speed: int, acc: int) -> bool:
        if motor.reverse:
            offset = -offset
        return self._move_to_absolute(motor, motor.init + offset, speed, acc)

    def _move_excute(self) -> None:
        self.packet_handler.RegAction()

    def move_all_zero(self) -> None:
        self._move_to_offset(self.motor_1, 0, 1000, 50)
        self._move_to_offset(self.motor_2, 0, 1000, 50)
        self._move_to_offset(self.motor_3, 0, 1000, 50)
        self._move_to_offset(self.motor_4, 0, 1000, 50)
        self._move_to_offset(self.motor_5, 0, 1000, 50)
        self._move_to_offset(self.motor_6, 0, 1000, 50)
        self._move_excute()

    def move_test(self) -> None:
        """
        Test the motors by moving them to their middle position.
        """
        self._move_to_offset(self.motor_1, 1024, 1000, 50)
        self._move_to_offset(self.motor_2, 1024, 1000, 50)
        self._move_to_offset(self.motor_3, 1024, 1000, 50)
        self._move_to_offset(self.motor_4, 1024, 1000, 50)
        self._move_to_offset(self.motor_5, 1024, 1000, 50)
        self._move_to_offset(self.motor_6, 1024, 1000, 50)
        self._move_excute()
