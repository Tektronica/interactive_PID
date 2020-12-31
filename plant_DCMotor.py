import numpy as np
from scipy.integrate import odeint

# https://towardsdatascience.com/on-simulating-non-linear-dynamic-systems-with-python-or-how-to-gain-insights-without-using-ml-353eebf8dcc3
# tau * dy2/dt2 + 2*zeta*tau*dy/dt + y = Kp*u

# initialize system's parameters
R = 2  # Ohm
T_r = 3
L = 400 * 10e-3  # Henri
k = 100  # Nm/A
r = 0.5  # m
m = 500  # kg
g = 9.81  # m/s^2


# The resistor R will increase its temperature with runtime t
def R_nonlinear(t):
    return R + 8 * (1 - np.exp(-t / T_r))


# this one could be any other function of time
def u_t(t):
    return 0


class Plant:
    def __init__(self):
        self.x, self.v, self.i = [0, 0, 0]  # initial condition
        self.log = []
        self.pid = 0
        self.plot_settings = {'title': 'Elevator position off of ground',
                              'xlabel': 'time (s)', 'ylabel': 'x position away from ground (in)'}
        self.controls = {'setpoint': 10, 'runtime': 100, 'stepsize': 0.05,
                         'kpmin': 0, 'kpmax': 1000, 'kpstep': 100, 'kpset': 500,
                         'kimin': 0, 'kimax': 1000, 'kistep': 100, 'kiset': 500,
                         'kdmin': 0, 'kdmax': 1000, 'kdstep': 100, 'kdset': 500}

    def deriv(self, X, t):
        x, v, i = X
        dxdt = v
        dvdt = k / (r * m) * i - g
        didt = (-R_nonlinear(t) / L) * i - (k / r) * v + (1 / L) * self.pid
        return [dxdt, dvdt, didt]

    def update(self, pid, t, dt):
        self.pid += pid
        x, v, i = self.x, self.v, self.i
        self.log.append([t, x, v, i])
        x, v, i = odeint(self.deriv, [x, v, i], [t, t + dt])[-1]  # start at t, find state at t + dt
        self.x, self.v, self.i = x, v, i

        return self.x

    def reset(self):
        self.x, self.v, self.i = [0, 0, 0]  # initial condition
        self.log = []
        self.pid = 0

    def logger(self):
        return self.log
