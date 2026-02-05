import CONFIG

import time
import numpy as np

from hardware.RotationStage import RotationStage
from hardware.Photodiode import Photodiode
from hardware.Powermeter import Powermeter


class UnsupportedDetectorError(Exception):
    pass

class PowermeterNotFoundError(Exception):
    pass

class Analyzer:
    def __init__(self, detector):
        self.rotation_stage = RotationStage('KBD101', CONFIG.polarimeter_kcube)
        self.detector = detector.lower()
        self.measurement_data = None

        match self.detector:
            case 'photodiode':
                self.photodiode = Photodiode()
            case 'powermeter':
                try:
                    self.powermeter = Powermeter()
                except:
                    raise PowermeterNotFoundError
            case _:
                raise UnsupportedDetectorError
    def snap(self):
        current_rotation_stage_position = self.rotation_stage.get_position()
        if current_rotation_stage_position < 0:
            next_motor_position = 0
        else:
            next_motor_position = (current_rotation_stage_position // 360 + 1) * 360

        match self.detector:
            case 'photodiode':
                self.photodiode.arm_daq()
                time.sleep(CONFIG.nidaqmx_arm_sleep_in_seconds)
                next_motor_position += 360 + CONFIG.analyzer_start_position
                self.rotation_stage.set_position(next_motor_position, absolute=True)
                self.photodiode.disarm_daq()
                if self.photodiode.analog_data is not None:
                    self.measurement_data = self.photodiode.get_signal_at_triggers()

                self.analog_data = self.photodiode.analog_data
                self.analog_data_valid = self.photodiode.analog_data_valid
                self.missed_triggers = int(360/CONFIG.trigger_out_interval_in_deg) - self.measurement_data.shape[1]
            case 'powermeter':
                motor_step = int(360/CONFIG.powermeter_number_of_measurements)

                self.measurement_data = np.zeros((2, CONFIG.powermeter_number_of_measurements))
                self.measurement_data[0] = np.linspace(0, 360, num=self.measurement_data.shape[1], endpoint=False)

                for ii in range(CONFIG.powermeter_number_of_measurements):
                    self.rotation_stage.set_position(next_motor_position+ii*motor_step, absolute=True)
                    time.sleep(CONFIG.powermeter_stabilization_in_seconds)
                    self.measurement_data[1, ii] = self.powermeter.measure_once()

                self.analog_data = None
                self.analog_data_valid = False

    def save(self, path):
        match self.detector:
            case 'photodiode':
                np.savez(
                    path, 
                    analog_data=self.analog_data,
                    measurement_data=self.measurement_data,
                    calibration_mean=self.photodiode.calibration_mean,
                    calibration_std=self.photodiode.calibration_std
                    )
            case 'powermeter':
                np.savez(
                    path, 
                    measurement_data=self.measurement_data
                    )

    def close(self):
        self.rotation_stage.close()

        try:
            self.photodiode.disarm_daq()
            self.photodiode.set_bias_voltage(0)
        except:
            pass