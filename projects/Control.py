import math
import time

import matplotlib.pyplot as plt
import rtde_control
import rtde_io
import rtde_receive

Global_number = [0, 0, 0]


def calculate(radius, n, x0, y0):
    x = []
    y = []
    n_count = n
    i = 0
    while n_count > -1:
        x.append(x0 + radius * math.cos(i * 2 * math.pi / n))
        y.append(y0 + radius * math.sin(i * 2 * math.pi / n))
        n_count = n_count - 1
        i = i + 1
    return x, y


def calculate_e(n, x0, y0, a, b):
    x = []
    y = []
    n_count = n
    i = 0
    while n_count > -1:
        x.append(x0 + a * math.cos(i * 2 * math.pi / n))
        y.append(y0 + b * math.sin(i * 2 * math.pi / n))
        n_count = n_count - 1
        i = i + 1
    return x, y


def calculate_h(X, Y, n, x0, y0, T):  # t:2*pi*n
    a = X / T * math.cos(T)
    b = a * Y / X
    x = []
    y = []
    n_count = n
    i = 0
    t = 0
    T_deliver = T / n
    while n_count > -1:
        t = t + T_deliver
        x.append(x0 + a * t * math.cos(t))
        y.append(y0 + b * t * math.sin(t))
        n_count = n_count - 1
        i = i + 1
    return x, y


class URControl:
    def __init__(self):
        self.control_c = rtde_control.RTDEControlInterface("192.168.1.10")
        self.receive_r = rtde_receive.RTDEReceiveInterface("192.168.1.10")
        self.rtde_i = rtde_io.RTDEIOInterface("192.168.1.10")
        return

    def get_self(self):
        return self

    def move_l(self, x, y, z, r, s, t):
        self.control_c.moveL(x, y, z, r, s, t, 0.5, 0.5, 0)
        return

    def get_TCPPose(self):
        return self.receive_r.getActualTCPPose()

    def get_ft_chart(self):
        FM_num = 3
        t_array = [[0], [0], [0], [0], [0], [0]]
        t = [0, 0]
        t_append = 0
        color = ['b', 'g', 'r', 'c', 'm', 'y']
        text = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
        self.control_c.zeroFtSensor()
        for i in range(FM_num):
            plt.plot(0, t_array[i], color[i], linewidth=5, linestyle="-", label=text[i])
            plt.legend(loc='upper right', frameon=False, labelspacing=0.5)

        while True:
            # plt.clf()
            tcp_force = self.receive_r.getActualTCPForce()
            Global_number[0:2] = tcp_force[0:2]
            for i in range(FM_num):
                t_array[i].append(tcp_force[i])
                plt.plot(t, t_array[i], color[i], linewidth=0.2)
            t_append += 1
            t.append(t_append)
            plt.pause(0.01)
        return

    def get_ft_date(self):

        tcp_force = self.receive_r.getActualTCPForce()
        return

    def circle_move(self, radius, n, x0, y0):
        velocity = 0.05
        acceleration = 0.5
        [x, y] = calculate(radius, n, x0, y0)
        path = []
        for i in range(len(x)):
            if i == n or i == 0:
                blend = 0.0
            else:
                blend = radius / 10
            path.append([x[i], y[i], 0.5, 3.14, 0, 0, velocity, acceleration, blend])
        self.control_c.moveL(path, 1)  # 0:default:wait it completed 1:continue next stop directly
        return

    def ellipse_move(self, a, b, n, x0, y0):  # a: long side
        velocity = 0.1
        acceleration = 0.5
        [x, y] = calculate_e(n, x0, y0, a, b)
        path = []
        for i in range(len(x)):
            # path.append([x[i], y[i], 0.5, 3.14, 0, 0])
            path.append([x[i], y[i], 0.5])
        blend = 0.01
        self.control_c.moveC(path[1], path[0], velocity, acceleration, blend, 1)
        return

    def helical_line_move(self, radiusX, radiusY, n, x0, y0, t):
        velocity = 0.01
        acceleration = 0.5
        [x, y] = calculate_h(radiusX, radiusY, n, x0, y0, t)
        path = []
        for i in range(len(x)):
            if i == n or i == 0:
                blend = 0.0
            else:
                blend = radiusY / 10
            path.append([x[i], y[i], self.receive_r.getActualTCPPose()[2], 3.14, 0, 0, velocity, acceleration, blend])
        self.control_c.moveL(path, 1)  # 0:default:wait it completed 1:continue next stop directly
        return

    def control_force_mode(self, z_force):
        task_frame = [0, 0, 0, 0, 0, 0]
        selection_vector = [0, 0, 1, 0, 0, 0]
        wrench_up = [0, 0, z_force, 0, 0, 0]
        force_type = 1
        limits = [2, 2, 1.5, 1, 1, 1]
        # self.control_c.forceModeSetDamping(1)
        # self.control_c.forceModeSetGainScaling(0.5)
        self.control_c.forceMode(task_frame, selection_vector, wrench_up, force_type, limits)
        return

    def control_force_mode_stop(self):
        self.control_c.forceModeStop()
        return

    def isSteady(self):
        return self.control_c.isSteady()

    def moveC(self):
        self.control_c.moveC()

    def logic(self):
        self.control_c.moveL([-0.6, -0.06, -0.01, 3.14, 0, 0], 0.1, 0.5, 0)
        self.control_force_mode(5)
        get_z_force = 0.0
        while get_z_force < 5:
            get_z_force = self.receive_r.getActualTCPForce()[2]
            time.sleep(0.1)
            continue
        self.control_force_mode_stop()
        self.control_c.stopL(0.5)
        self.helical_line_move(0.01, 0.015, 200, -0.6, -0.065, 24 * math.pi)
        self.control_force_mode(5)
        time.sleep(0.1)
        Force = self.receive_r.getActualTCPForce()
        Force_x_y = 0
        while Force_x_y < 10 and (not self.isSteady()) and Force[2] < 100:
            Force = self.receive_r.getActualTCPForce()
            Force_x_y = math.sqrt(Force[0] * Force[0] + Force[1] * Force[1])
            continue
        self.control_c.stopL(10)
        self.control_force_mode_stop()
        time.sleep(0.1)
        R = self.receive_r.getActualTCPPose()
        self.control_c.moveL([R[0], R[1], -0.02, 3.14, 0, 0], 0.1, 0.5, 1)
        while not self.isSteady():
            continue

    def move_test(self):
        self.control_c.moveL([-0.6, 0, 0.5, 3.14, 0, 0], 0.1, 0.5, 0)
        time.sleep(2)
        self.control_c.moveL([-0.6, 0, 0.5, 4, 0, 0], 0.1, 0.5, 0)
        time.sleep(5)

    def move_test2(self):
        self.control_c.moveL([-0.6, 0, 0.5, 3.14, 0, 0], 0.1, 0.5, 0)
        time.sleep(2)
        self.control_c.moveL([-0.6, 0, 0.5, 4, 0, 0], 0.1, 0.5, 0)
        time.sleep(5)


if __name__ == '__main__':
    A = URControl()
    R = A.receive_r.getActualTCPPose()
    print(R)
    # A.control_c.
    A.control_c.moveL([R[0], R[1], 0, 3.14, 0, 0], 0.1, 0.5, 0)
    # # A.helical_line_move(0.05, 0.03, 500, -0.6247583794035511, -0.07278212409697761, 6 * math.pi)
    # A.control_force_mode()
    # # A.get_ft_chart()
    # get_Z_Force = 0.0
    # while get_Z_Force < 5:
    #     get_Z_Force = A.receive_r.getActualTCPForce()[2]
    #     time.sleep(0.01)
    #     continue
    # A.control_force_mode_stop()
    #
    # # while A.isSteady() == 0:
    # #     continue
    # A.control_c.moveL([-0.6247583794035511, -0.0727821, 0.2, 3.14, 0, 0], 0.1, 0.5, 0)
