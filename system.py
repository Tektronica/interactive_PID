from PID import PID
import numpy as np
import matplotlib.pyplot as plt
import Models
from plant_Reactor import Plant as Reactor
from plant_DCMotor import Plant as DCMotor

def system(params):
    plant_name, setpoint, runtime, dt, Kp, Ki, Kd = params
    pid_controller = PID()
    output = []
    plant = get_plant(plant_name)
    fdbk = 0
    x = np.arange(0, runtime+dt, dt)

    for t in x:
        pid_val = pid_controller.pid(setpoint, fdbk, Kp, Ki, Kd, dt)
        fdbk = plant.update(pid_val, t, dt)
        output += [fdbk]
    # plant.plot()
    return x, output


def get_plant(name):
    if name == 'Reactor':
        plant = Reactor()
    elif name == 'Water Boiler':
        plant = DCMotor()
    else:
        plant = DCMotor()
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
    Kp = 40
    Ki = 80
    Kd = 0
    params = ("Reactor", 390, 8, 0.05, Kp, Ki, Kd)
    x, y = system(params)
    plot_temporal(x, y, title="Step Response")


if __name__ == "__main__":
    main()
