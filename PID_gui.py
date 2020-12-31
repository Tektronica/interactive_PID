import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import threading
import numpy as np
import time
import system
from FloatSlider import FloatSlider


def toFloat(s):
    try:
        return float(s)
    except ValueError:
        print(f"Could not convert [{s}] to decimal")
        return 0.0


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1100, 605))
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)

        # (LEFT) Settings Panel ----------------------------------------------------------------------------------------
        self.left_panel = wx.Panel(self.panel_2, wx.ID_ANY)
        self.plant_combo_box = wx.ComboBox(self.left_panel, wx.ID_ANY,
                                           choices=['Reactor', 'DC Motor', 'Water Boiler', '2nd Order ODE'],
                                           style=wx.CB_DROPDOWN)
        self.setpoint_text_ctrl = wx.TextCtrl(self.left_panel, wx.ID_ANY, "390")
        self.runtime_text_ctrl = wx.TextCtrl(self.left_panel, wx.ID_ANY, "8")
        self.stepsize_text_ctrl = wx.TextCtrl(self.left_panel, wx.ID_ANY, "0.05")
        self.pCheck = wx.CheckBox(self.left_panel, wx.ID_ANY, "")
        # self.slider_1 = wx.Slider(self.left_panel, wx.ID_ANY, value=5, minValue=0, maxValue=10,
        #                           style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS)
        self.slider_1 = FloatSlider(self.left_panel, value=0.5, minVal=0, maxVal=1, label='Kp')
        self.iCheck = wx.CheckBox(self.left_panel, wx.ID_ANY, "")
        # self.slider_2 = wx.Slider(self.left_panel, wx.ID_ANY, value=5, minValue=0, maxValue=10,
        #                           style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS)
        self.slider_2 = FloatSlider(self.left_panel, value=0.5, minVal=0, maxVal=1, label='Ki')
        self.dCheck = wx.CheckBox(self.left_panel, wx.ID_ANY, "")
        # self.slider_3 = wx.Slider(self.left_panel, wx.ID_ANY, value=5, minValue=0, maxValue=10,
        #                           style=wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS)
        self.slider_3 = FloatSlider(self.left_panel, value=0.5, minVal=0, maxVal=1, label='Kd')

        # (RIGHT) PLOT Panel -------------------------------------------------------------------------------------------
        self.right_panel = wx.Panel(self.panel_2, wx.ID_ANY, style=wx.SIMPLE_BORDER)

        self.figure = plt.figure(figsize=(1, 1))  # look into Figure((5, 4), 75)
        self.canvas = FigureCanvas(self.right_panel, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()

        self.ax1 = self.figure.add_subplot(111)
        # self.ax1 = self.figure.add_subplot(211)
        # self.ax2 = self.figure.add_subplot(212)
        self.step, = self.ax1.plot([], [], linestyle='-')
        # self.temporal, = self.ax1.plot([], [], linestyle='-')
        # self.spectral, = self.ax2.plot([], [], color='red')

        self.plot_title = 'Step Plot'
        self.yaxis_label = 'Amplitude'
        self.system = None

        # EVENT HANDLES ------------------------------------------------------------------------------------------------
        self.Bind(wx.EVT_COMBOBOX, lambda event: self.report_combo(event, "plant"), self.plant_combo_box)
        self.Bind(wx.EVT_TEXT, lambda event: self.report_text(event, "setpoint"), self.setpoint_text_ctrl)
        self.Bind(wx.EVT_TEXT, lambda event: self.report_text(event, "runtime"), self.runtime_text_ctrl)
        self.Bind(wx.EVT_TEXT, lambda event: self.report_text(event, "step size"), self.stepsize_text_ctrl)

        self.Bind(wx.EVT_CHECKBOX, lambda event: self.report_checkbox(event, self.slider_1, 'Kp'), self.pCheck)
        self.Bind(wx.EVT_CHECKBOX, lambda event: self.report_checkbox(event, self.slider_2, 'Ki'), self.iCheck)
        self.Bind(wx.EVT_CHECKBOX, lambda event: self.report_checkbox(event, self.slider_3, 'Kd'), self.dCheck)

        # self.Bind(wx.EVT_SLIDER, lambda event: self.report_slider(event, "Kp"), self.slider_1)
        # self.Bind(wx.EVT_SLIDER, lambda event: self.report_slider(event, "Ki"), self.slider_2)
        # self.Bind(wx.EVT_SLIDER, lambda event: self.report_slider(event, "Kd"), self.slider_3)

        self.Bind(wx.EVT_SLIDER, lambda event: self.report_slider(event, "Kp"))

        self.Freeze()
        self.__set_properties()
        self.__do_layout()
        self.__do_plot_layout()
        self.setup()
        self.update()
        self.Thaw()

    def __set_properties(self):
        self.SetTitle("PID Controller")
        self.plant_combo_box.SetMinSize((200, 23))
        self.plant_combo_box.SetSelection(0)
        self.pCheck.SetValue(1)
        self.iCheck.SetValue(1)
        self.dCheck.SetValue(1)
        self.left_panel.SetMinSize((310, 502))
        self.right_panel.SetMinSize((700, 502))
        self.canvas.SetMinSize((700, 490))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.GridBagSizer(0, 0)
        grid_sizer_2 = wx.GridBagSizer(0, 0)
        grid_sizer_3 = wx.GridBagSizer(0, 0)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        # RIGHT PANEL --------------------------------------------------------------------------------------------------
        grid_sizer_2.Add(self.canvas, (0, 0), (1, 1), wx.ALL | wx.EXPAND)
        grid_sizer_2.Add(self.toolbar, (1, 0), (1, 1), wx.ALL | wx.EXPAND)
        self.right_panel.SetSizer(grid_sizer_2)

        # LEFT PANEL --------------------------------------------------------------------------------------------------
        label_1 = wx.StaticText(self.left_panel, wx.ID_ANY, "Plant Settings")
        label_1.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_1, (0, 0), (1, 2), 0, 0)
        static_line_6 = wx.StaticLine(self.left_panel, wx.ID_ANY)
        static_line_6.SetMinSize((300, 2))
        grid_sizer_3.Add(static_line_6, (1, 0), (1, 2), wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 5)
        label_3 = wx.StaticText(self.left_panel, wx.ID_ANY, "Plant")
        label_3.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_3, (2, 0), (1, 1), 0, 0)
        grid_sizer_3.Add(self.plant_combo_box, (2, 1), (1, 1), wx.BOTTOM | wx.LEFT, 5)
        label_4 = wx.StaticText(self.left_panel, wx.ID_ANY, "Setpoint")
        label_4.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_4, (3, 0), (1, 1), 0, 0)
        grid_sizer_3.Add(self.setpoint_text_ctrl, (3, 1), (1, 1), wx.BOTTOM | wx.LEFT, 5)
        label_11 = wx.StaticText(self.left_panel, wx.ID_ANY, "Runtime (s)")
        label_11.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_11, (4, 0), (1, 1), 0, 0)
        grid_sizer_3.Add(self.runtime_text_ctrl, (4, 1), (1, 1), wx.BOTTOM | wx.LEFT, 5)
        label_2 = wx.StaticText(self.left_panel, wx.ID_ANY, "Stepsize (s)")
        label_2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_2, (5, 0), (1, 1), 0, 0)
        grid_sizer_3.Add(self.stepsize_text_ctrl, (5, 1), (1, 1), wx.BOTTOM | wx.LEFT, 5)
        label_5 = wx.StaticText(self.left_panel, wx.ID_ANY, "PID Settings")
        label_5.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_5, (6, 0), (1, 2), wx.TOP, 10)
        static_line_7 = wx.StaticLine(self.left_panel, wx.ID_ANY)
        static_line_7.SetMinSize((300, 2))
        grid_sizer_3.Add(static_line_7, (7, 0), (1, 2), wx.ALIGN_CENTER, 0)
        label_6 = wx.StaticText(self.left_panel, wx.ID_ANY, "Proportional")
        label_6.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_6, (8, 0), (1, 2), wx.TOP, 5)
        grid_sizer_3.Add(self.pCheck, (9, 0), (1, 1), wx.ALIGN_CENTER, 0)
        label_7 = wx.StaticText(self.left_panel, wx.ID_ANY, "Gain (Kp)")
        label_7.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_3.Add(label_7, 0, 0, 0)
        sizer_3.Add(self.slider_1, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(sizer_3, (9, 1), (1, 1), wx.EXPAND, 0)
        label_8 = wx.StaticText(self.left_panel, wx.ID_ANY, "Integral")
        label_8.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_8, (10, 0), (1, 2), wx.TOP, 5)
        grid_sizer_3.Add(self.iCheck, (11, 0), (1, 1), wx.ALIGN_CENTER, 0)
        label_9 = wx.StaticText(self.left_panel, wx.ID_ANY, "Gain (Ki)")
        label_9.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_4.Add(label_9, 0, 0, 0)
        sizer_4.Add(self.slider_2, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(sizer_4, (11, 1), (1, 1), wx.EXPAND, 0)
        label_12 = wx.StaticText(self.left_panel, wx.ID_ANY, "Derivative")
        label_12.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_3.Add(label_12, (12, 0), (1, 2), wx.TOP, 5)
        grid_sizer_3.Add(self.dCheck, (13, 0), (1, 1), wx.ALIGN_CENTER, 0)
        label_10 = wx.StaticText(self.left_panel, wx.ID_ANY, "Gain (Kd)")
        label_10.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_5.Add(label_10, 0, 0, 0)
        sizer_5.Add(self.slider_3, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(sizer_5, (13, 1), (1, 1), wx.EXPAND, 0)
        self.left_panel.SetSizer(grid_sizer_3)
        grid_sizer_1.Add(self.left_panel, (0, 0), (1, 1), wx.EXPAND, 0)
        self.right_panel.SetSizer(grid_sizer_2)
        grid_sizer_1.Add(self.right_panel, (0, 1), (1, 1), wx.EXPAND | wx.LEFT, 10)
        self.panel_2.SetSizer(grid_sizer_1)
        sizer_2.Add(self.panel_2, 1, wx.ALL | wx.EXPAND, 10)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)

        # Growable objects within frame  -------------------------------------------------------------------------------
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(1)
        grid_sizer_2.AddGrowableRow(0)
        grid_sizer_2.AddGrowableCol(0)

        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()

    def get_plant(self):
        return self.plant_combo_box.GetStringSelection()

    def get_values(self):
        setpoint = toFloat(self.setpoint_text_ctrl.GetValue())
        runtime = toFloat(self.runtime_text_ctrl.GetValue())
        stepsize = toFloat(self.stepsize_text_ctrl.GetValue())
        Kp = self.get_slider(self.slider_1)
        Ki = self.get_slider(self.slider_2)
        Kd = self.get_slider(self.slider_3)
        return setpoint, runtime, stepsize, Kp, Ki, Kd

    def set_slider(self, params):
        self.slider_1.SetRange(params['kpmin'], params['kpmax'])
        self.slider_1.SetValue(params['kpset'])
        self.slider_2.SetRange(params['kimin'], params['kimax'])
        self.slider_2.SetValue(params['kiset'])
        self.slider_3.SetRange(params['kdmin'], params['kdmax'])
        self.slider_3.SetValue(params['kdset'])

    def get_slider(self, slider):
        if slider.IsEnabled():
            K = slider.GetValue()
        else:
            K = 0.0
        return K

    # ------------------------------------------------------------------------------------------------------------------
    def setup(self):
        self.system = system.System(self.get_plant())
        self.update_plot_labels(self.system.plant.plot_settings)

    def update(self):
        x, y = self.system.run(self.get_values())

        self.plot({'x': x, 'y': y})
        time.sleep(0.01)

    # ------------------------------------------------------------------------------------------------------------------
    def report_combo(self, evt, text_name):
        print(f'The {text_name} has changed to {evt.GetEventObject().GetValue()}')
        self.setup()
        self.update()

    def report_text(self, evt, text_name):
        print(f'The {text_name} has changed to {evt.GetEventObject().GetValue()}')
        self.update()

    def report_checkbox(self, evt, slider, slider_name):
        state = evt.GetEventObject().GetValue()
        print(f'The check box for {slider_name} has changed to {state}')
        if not state:
            slider.Disable()
        else:
            slider.Enable()
        self.update()

    def report_slider(self, evt, slider_name):
        print(f'The gain, {slider_name}, has changed to {evt.GetEventObject().GetValue()}')
        self.update()

    # ------------------------------------------------------------------------------------------------------------------
    def __do_plot_layout(self):
        self.ax1.set_title(self.plot_title)
        self.ax1.set_xlabel('TIME (s)')
        self.ax1.set_ylabel(self.yaxis_label)
        self.ax1.grid()
        # self.ax2.set_title('DIGITIZED WAVEFORM SPECTRAL RESPONSE')
        # self.ax2.set_xlabel('FREQUENCY (kHz)')
        # self.ax2.set_ylabel('MAGNITUDE (dB)')
        # self.ax2.grid()
        # self.figure.align_ylabels([self.ax1, self.ax2])
        self.figure.align_ylabels([self.ax1])
        self.figure.tight_layout()

    def update_plot_labels(self, params):
        self.ax1.set_xlabel(params['xlabel'])
        self.ax1.set_ylabel(params['ylabel'])
        self.ax1.set_title(params['title'])

    def plot(self, data):
        # TEMPORAL -----------------------------------------------------------------------------------------------------
        x = data['x']
        y = data['y']

        self.step.set_data(x, y)
        # ylimit = np.max(np.abs(y)) * 1.25
        # increment = ylimit / 4
        # self.ax1.set_yticks(np.arange(-ylimit, ylimit + increment, increment))
        self.ax1.relim()  # recompute the ax.dataLim
        self.ax1.autoscale()

        # SPECTRAL -----------------------------------------------------------------------------------------------------
        # xf = data['xf']
        # ywf = data['ywf']
        # Fs = data['Fs']
        # N = data['N']
        # yrms = data['yrms']
        #
        # # divide by number of samples to keep the scaling.
        # self.spectral.set_data(xf[0:N] / 1000, 20 * np.log10(2 * np.abs(ywf[0:N] / (yrms * N))))
        #
        # xf_max = min(10 ** (np.ceil(np.log10(F0)) + 1), Fs / 2 - Fs / N)  # Does not exceed max bin
        # self.ax2.set_xlim(np.min(xf) / 1000, xf_max / 1000)
        # self.ax2.set_ylim(-150, 0)

        # UPDATE PLOT FEATURES -----------------------------------------------------------------------------------------
        self.figure.tight_layout()

        self.toolbar.update()  # Not sure why this is needed - ADS
        self.canvas.draw()
        self.canvas.flush_events()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
