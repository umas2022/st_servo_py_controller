

import time
from ArmController.ArmController import ArmController

arm_slave = ArmController(serial_port='COM12')
arm_slave.hardware_init()  # Initialize the hardware

while True:
    if arm_slave.online_check():  # Check if the motor is connected
        break

while True:
    arm_slave.move_all_zero()  # Move all motors to the zero position
    print("All motors are at zero position.")
    time.sleep(3)  # Wait for 1 second before checking again

    arm_slave.move_test()  # Move the motor to the test position
    print("All motors are at test position.")
    time.sleep(3)  # Wait for 1 second before checking again
        


