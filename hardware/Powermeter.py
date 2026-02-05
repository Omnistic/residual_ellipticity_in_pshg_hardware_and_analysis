import CONFIG

import time

import pyvisa


class Powermeter():
    def __init__(self):
        self._rm = pyvisa.ResourceManager()
        self._resource = CONFIG.powermeter_resource
        self._wavelength = CONFIG.powermeter_wavelength_in_nm
        self._samples_per_measurement = CONFIG.powermeter_number_of_samples_averaged_per_measurement

        try:
            self._inst = self._rm.open_resource(self._resource)
        except:
            print("ERROR: Powermeter not found. List of resources: " + ', '.join(self._rm.list_resources()))
            raise TimeoutError

        self._inst.write("AVER {}".format(self._samples_per_measurement))
        self.set_wavelength(self._wavelength)
        self._inst.write("POW:RANG:AUTO ON")
        self.zero()

    def beep(self):
        self._inst.write("SYST:BEEP")

    def zero(self):
        self._inst.write("CORR:COLL:ZERO")
        time.sleep(2)

    def measure_once(self):
        power = self._inst.query("READ?")
        return power

    def set_wavelength(self, wavelength):
        self._inst.write("CORR:WAV {}".format(wavelength))