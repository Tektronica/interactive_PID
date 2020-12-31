def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class PID:
    def __init__(self):
        self.derror = [0, 0, 0]
        self.perror = [0, 0]
        self.ierror = 0

        self.min = -500000
        self.max = 500000
        self.beta = 0
        self.gamma = 0

    def proportional(self, SP, PV, Kp):
        self.perror[0] = self.beta * SP - PV
        eP = self.perror[0] - self.perror[1]
        self.perror[1] = self.perror[0]
        return eP * Kp

    def integral(self, SP, PV, Ki, min_lim, max_lim, dt):
        self.ierror = Ki * (SP - PV) * dt
        # print(f'SP: {SP}, PV: {PV}')
        # self.ierror = clamp(self.ierror, min_lim, max_lim)  # limit state to a range
        return self.ierror

    def derivative(self, SP, PV, Kd, dt):
        self.derror[0] = self.gamma * SP - PV
        # Employing first order finite central difference
        deD = (self.derror[0] - 2 * self.derror[1] + self.derror[2]) / (dt)

        # memory
        self.derror[2] = self.derror[1]
        self.derror[1] = self.derror[0]

        return deD * Kd

    def pid(self, SP, PV, Kp, Ki, Kd, dt):
        p = self.proportional(SP, PV, Kp)
        i = self.integral(SP, PV, Ki, self.min, self.max, dt)
        d = self.derivative(SP, PV, Kd, dt)
        # print(f'p: {p}, i: {i}, d: {d}')
        return p + i + d

    def set_limits(self, out_min, out_max):
        self.min = out_min
        self.max = out_max

    def reset(self):
        self.derror = [0, 0, 0]
        self.perror = [0, 0]
        self.ierror = 0
