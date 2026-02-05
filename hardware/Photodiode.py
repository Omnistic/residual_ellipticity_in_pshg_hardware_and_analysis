import CONFIG

import numpy as np
from threading import Thread

import nidaqmx


class Photodiode:
    def __init__(self):
        self.analog_data = np.zeros((2, CONFIG.nidaqmx_samples_per_channel))
        self.analog_data_valid = False
        self.data_at_triggers = None
        self.calibration_mean = 0
        self.calibration_std = 0

    def arm_daq(self):
        self.ai_thread = Thread(target=self.__read_ai_channels)
        self.ai_thread.start()

    def disarm_daq(self):
        try:
            self.ai_thread.join()
        except:
            pass

    def calibrate(self):
        calibration_samples = int(CONFIG.nidaqmx_clock_rate*CONFIG.nidaqmx_calibration_duration_in_seconds)

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(CONFIG.nidaqmx_ai_rotation_stage_trigger + ', ' + CONFIG.nidaqmx_ai_photodiode_signal)
            task.timing.cfg_samp_clk_timing(rate=CONFIG.nidaqmx_clock_rate, samps_per_chan=calibration_samples)
            data = np.zeros((2, calibration_samples))
            data[:] = task.read(number_of_samples_per_channel=calibration_samples, timeout=2*CONFIG.nidaqmx_calibration_duration_in_seconds)

        self.calibration_mean = np.mean(data[1, :])
        self.calibration_std = np.std(data[1, :])

    def __read_ai_channels(self):
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(CONFIG.nidaqmx_ai_rotation_stage_trigger + ', ' + CONFIG.nidaqmx_ai_photodiode_signal)
            task.timing.cfg_samp_clk_timing(rate=CONFIG.nidaqmx_clock_rate, samps_per_chan=CONFIG.nidaqmx_samples_per_channel)
            task.triggers.start_trigger.cfg_dig_edge_start_trig(CONFIG.nidaqmx_trigger_source)
            try:
                self.analog_data[:] = task.read(number_of_samples_per_channel=CONFIG.nidaqmx_samples_per_channel, timeout=CONFIG.ai_timeout_in_seconds)
                self.analog_data_valid = True
            except:
                self.analog_data_valid = False

    def set_bias_voltage(self, voltage):
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(CONFIG.nidaqmx_ao_photodiode_bias, min_val=0, max_val=10)
            task.write(voltage, auto_start=True)

    def get_signal_at_triggers(self):
        rotation_stage_trigger_signal = self.analog_data[0]
        trigger_indices = np.flatnonzero( (rotation_stage_trigger_signal[:-1] < 2.5 ) & (rotation_stage_trigger_signal[1:] > 2.5 ) ) + 1
        trigger_indices = np.insert(trigger_indices, 0, 0)
        number_of_triggers = len(trigger_indices)

        data_at_triggers = np.zeros((2, number_of_triggers))
        data_at_triggers[0] = np.linspace(0, 360, num=number_of_triggers, endpoint=False)

        for ii in range(CONFIG.nidaqmx_number_of_samples_averaged_per_trigger):
            data_at_triggers[1,:] += self.analog_data[1, trigger_indices + ii]
        data_at_triggers[1,:] /= CONFIG.nidaqmx_number_of_samples_averaged_per_trigger

        data_at_triggers[1,:] -= self.calibration_mean
        return data_at_triggers