from scipy.integrate import odeint

# https://www.apmonitor.com/pdc/index.php/Main/ModelSimulation
# tau * dy2/dt2 + 2*zeta*tau*dy/dt + y = Kp*u

Kp = 2.0  # gain
tau = 1.0  # time constant
zeta = 0.25  # damping factor
theta = 0.0  # no time delay
du = 1  # change in u


class Plant:
    def __init__(self):
        self.X1, self.X2 = [0, 0]  # initial condition
        self.log = []
        self.pid = 0

        self.plot_settings = {'title': 'Second Order ODE',
                              'xlabel': 'time (s)', 'ylabel': 'Ampltiude'}
        self.controls = {'setpoint': 10, 'runtime': 30, 'stepsize': 0.05,
                         'kpmin': 0, 'kpmax': 100, 'kpstep': 10, 'kpset': 5,
                         'kimin': 0, 'kimax': 100, 'kistep': 10, 'kiset': 5,
                         'kdmin': 0, 'kdmax': 100, 'kdstep': 10, 'kdset': 5}

    def deriv(self, x, t):
        y = x[0]
        dydt = x[1]
        dy2dt2 = (-2.0 * zeta * tau * dydt - y + self.pid*du) / tau ** 2
        return [dydt, dy2dt2]

    def update(self, pid, t, dt):
        self.pid += pid
        X1, X2 = self.X1, self.X2
        self.log.append([t, X1, X2])
        X1, X2 = odeint(self.deriv, [X1, X2], [t, t + dt])[-1]  # start at t, find state at t + dt
        self.X1, self.X2 = X1, X2

        return self.X1

    def reset(self):
        self.X1, self.X2 = [0, 0]  # initial condition
        self.pid = 0
        self.log = []

    def logger(self):
        return self.log
