from PID import PID
import numpy as np
import matplotlib.pyplot as plt
from plant_Reactor import Plant as Reactor
from plant_DCMotor import Plant as DCMotor
from plant_2ndOrder import Plant as SecOrder


class System:
    def __init__(self, plant_name):
        self.plant = get_plant(plant_name)
        self.pid_controller = PID()

    def run(self, params):
        self.reset()
        setpoint, runtime, dt, Kp, Ki, Kd = params
        output = []
        fdbk = 0
        x = np.arange(0, runtime + dt, dt)

        for t in x:
            pid_val = self.pid_controller.pid(setpoint, fdbk, Kp, Ki, Kd, dt)
            fdbk = self.plant.update(pid_val, t, dt)
            output += [fdbk]
        # plant.plot()
        return x, output

    def reset(self):
        self.pid_controller.reset()
        self.plant.reset()


def get_plant(name):
    if name == 'Reactor':
        plant = Reactor()
    elif name == 'DC Motor':
        plant = DCMotor()
    elif name == '2nd Order ODE':
        plant = SecOrder()
    else:
        plant = Reactor()
    return plant


def plot_temporal(x, y, title=''):
    fig, ax = plt.subplots(1, 1, constrained_layout=True)
    ax.plot(x, y, '-b')  # scaling is applied.

    # ax.legend(['data'])
    ax.set_title(title)
    ax.set_xlabel('time (s)')
    ax.set_ylabel('Amplitude')
    ax.grid()
    plt.show()


def main():
    Kp = 500
    Ki = 500
    Kd = 0.01
    plant = 'DC Motor'
    params = (10, 100, 0.05, Kp, Ki, Kd)
    system = System(plant)
    x, y = system.run(params)
    plot_temporal(x, y, title="Step Response")


if __name__ == "__main__":
    main()
