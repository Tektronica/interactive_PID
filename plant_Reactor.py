import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# REACTOR PLANT --------------------------------------------------------------------------------------------------------
# https://jckantor.github.io/CBE30338/04.11-Implementing-PID-Control-in-Nonlinear-Simulations.html

Ea = 72750  # activation energy J/gmol
R = 8.314  # gas constant J/gmol/K
k0 = 7.2e10  # Arrhenius rate constant 1/min
V = 100.0  # Volume [L]
rho = 1000.0  # Density [g/L]
Cp = 0.239  # Heat capacity [J/g/K]
dHr = -5.0e4  # Enthalpy of reaction [J/mol]
UA = 5.0e4  # Heat transfer [J/min/K]
q = 100.0  # Flowrate [L/min]
Cf = 1.0  # Inlet feed concentration [mol/L]
Tf = 300.0  # Inlet feed temperature [K]

C0 = 0.5  # Initial concentration [mol/L]
T0 = 350.0  # Initial temperature [K]
Tcf = 300.0  # Coolant feed temperature [K]

qc = 150.0  # Nominal coolant flowrate [L/min]
Vc = 20.0  # Cooling jacket volume

# control saturation
qc_min = 0  # minimum possible coolant flowrate
qc_max = 300  # maximum possible coolant flowrate


# Arrhenius rate expression
def k(T):
    return k0 * np.exp(-Ea / R / T)


def sat(qc):  # function to return feasible value of qc
    return max(qc_min, min(qc_max, qc))


def plotReactor(X):
    log = np.asarray(X).T
    plt.figure(figsize=(16, 4))
    plt.subplot(1, 3, 1)
    plt.plot(log[0], log[1])
    plt.title('Concentration')
    plt.ylabel('moles/liter')
    plt.xlabel('Time [min]')

    plt.subplot(1, 3, 2)
    plt.plot(log[0], log[2], log[0], log[3])
    # if 'Tsp' in globals():
    #     plt.plot(plt.xlim(), [Tsp, Tsp], 'r:')
    plt.title('Temperature')
    plt.ylabel('Kelvin')
    plt.xlabel('Time [min]')
    plt.legend(['Reactor', 'Cooling Jacket'])

    plt.subplot(1, 3, 3)
    plt.plot(log[0], log[4])
    plt.title('Cooling Water Flowrate')
    plt.ylabel('liters/min')
    plt.xlabel('Time [min]')
    plt.tight_layout()
    plt.show()


"""
output = _odepack.odeint(func, y0, t, args, Dfun, col_deriv, ml, mu,
RuntimeError: The size of the array returned by func (3) does not match the size of y0 (1).
OnInit returned false, exiting...
"""


class Plant:
    def __init__(self):
        self.C, self.T, self.Tc = [C0, T0, Tcf]  # initial condition
        self.qc = qc
        self.log = []

        self.plot_settings = {'title': 'Reactor',
                              'xlabel': 'time (s)', 'ylabel': 'Temperature (K)'}
        self.controls = {'setpoint': 10, 'runtime': 30, 'stepsize': 0.05,
                         'kpmin': 0, 'kpmax': 100, 'kpstep': 10, 'kpset': 5,
                         'kimin': 0, 'kimax': 100, 'kistep': 10, 'kiset': 5,
                         'kdmin': 0, 'kdmax': 100, 'kdstep': 10, 'kdset': 5}

    def deriv(self, params, t):
        C, T, Tc = params
        dC = (q / V) * (Cf - C) - k(T) * C
        dT = (q / V) * (Tf - T) + (-dHr / rho / Cp) * k(T) * C + (UA / V / rho / Cp) * (Tc - T)
        dTc = (self.qc / Vc) * (Tcf - Tc) + (UA / Vc / rho / Cp) * (T - Tc)
        return [dC, dT, dTc]

    def update(self, pid, t, dt):
        self.qc -= pid
        self.qc = sat(self.qc)

        C, T, Tc = self.C, self.T, self.Tc
        self.log.append([t, C, T, Tc, self.qc])
        C, T, Tc = odeint(self.deriv, [C, T, Tc], [t, t + dt])[-1]  # start at t, find state at t + dt
        self.C, self.T, self.Tc = C, T, Tc

        return self.T

    def reset(self):
        self.C, self.T, self.Tc = [C0, T0, Tcf]  # initial condition
        self.qc = qc
        self.log = []

    def logger(self):
        return self.log

    def plot(self):
        plotReactor(self.logger())
