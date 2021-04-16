import numpy as np
from projects.Control import URControl as UR


class calibration:
    def __init__(self):
        self.robot = UR()

    def test(self):
        self.robot.move_test()

    def test2(self):
        self.robot.move_test2()

    # def calibration_step_1(self):





if __name__ == '__main__':
    A = calibration()
    A.test()
    A.test2()
