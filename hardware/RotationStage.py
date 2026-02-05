import CONFIG

import clr
import time

import System
from System import Decimal, Enum
from importlib import import_module


class UnsupportedControllerModelError(Exception):
    pass

class RotationStage:
    def __init__(self, controller_model, serial_number):
        self.controller_model = controller_model
        self.serial_number = str(serial_number)

        self.__load_kinesis_api()

        try:
            self.__initialize_controller()
        except UnsupportedControllerModelError:
            self.__controller = False
            print('ERROR: controller model {} not supported.'.format(self.controller_model))
        except self.__DeviceNotReadyException:
            self.__controller = False
            print('ERROR: controller {} (serial number {}) could not be connected. Check that the controller is turned ON, verify its serial number, and try again.'.format(self.controller_model, self.serial_number))
        except AssertionError:
            print('ERROR: controller {} (serial number {}), settings could not be initialized.'.format(self.controller_model, self.serial_number))

        if self.controller_model.lower() == 'kbd101' and self.__controller != False:
            self.__configure_for_analysis()

    def __load_kinesis_api(self):
        try:
            clr.AddReference(CONFIG.DeviceManagerCLI_fullpath)
            clr.AddReference(CONFIG.GenericMotorCLI_fullpath)
            clr.AddReference(CONFIG.BrushlessMotorCLI_fullpath)
            clr.AddReference(CONFIG.DCServoCLI_fullpath)
        except System.IO.FileNotFoundException:
            print('ERROR: unable to load Thorlabs Kinesis libraries. Check the paths to the libraries in the configuration file.')

        self.__DeviceManagerCLI = getattr(import_module(CONFIG.DeviceManagerCLI), 'DeviceManagerCLI')
        self.__DeviceConfiguration = getattr(import_module(CONFIG.DeviceManagerCLI), 'DeviceConfiguration')
        self.__DeviceNotReadyException = getattr(import_module(CONFIG.DeviceManagerCLI), 'DeviceNotReadyException')
        self.__KCubeDCServo = getattr(import_module(CONFIG.DCServoCLI), 'KCubeDCServo')
        self.__KCubeBrushlessMotor = getattr(import_module(CONFIG.BrushlessMotorCLI), 'KCubeBrushlessMotor')
        self.__KCubeTriggerConfigSettings = getattr(import_module(CONFIG.GenericMotorCLI+'.Settings'), 'KCubeTriggerConfigSettings')
        self.__MotorDirection = getattr(import_module(CONFIG.GenericMotorCLI), 'MotorDirection')

    def __initialize_controller(self):
        self.__DeviceManagerCLI.BuildDeviceList()

        match self.controller_model.lower():
            case 'kbd101':
                self.__controller = self.__KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.serial_number)
            case 'kdc101':
                self.__controller = self.__KCubeDCServo.CreateKCubeDCServo(self.serial_number)
            case _:
                self.__controller = False
                raise UnsupportedControllerModelError

        self.__controller.Connect(self.serial_number)
        time.sleep(CONFIG.kcube_initialization_sleep_in_s)
        self.__controller.StartPolling(CONFIG.kcube_polling_interval_in_ms)
        time.sleep(CONFIG.kcube_initialization_sleep_in_s)
        self.__controller.EnableDevice()
        time.sleep(CONFIG.kcube_initialization_sleep_in_s)
        
        if self.__controller.IsSettingsInitialized() is False:
            self.__controller.WaitForSettingsInitialized(CONFIG.kcube_settings_timeout_in_ms)
            assert self.__controller.IsSettingsInitialized() is True

        self.__controller.LoadMotorConfiguration(self.serial_number, self.__DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)

        self.__controller.SetRotationModes(
            Enum.Parse(self.__controller.MotorDeviceSettings.Rotation.RotationModes, "RotationalUnlimited"),
            Enum.Parse(self.__controller.MotorDeviceSettings.Rotation.RotationDirections, "Forwards")
        )

        self.__controller.Home(CONFIG.home_timeout_in_ms)

    def __configure_for_analysis(self):
        self.set_position(CONFIG.analyzer_start_position, absolute=True)

        self.__set_triggers_for_analysis()

    def __set_triggers_for_analysis(self):
        self.__trigger_config_params = self.__controller.GetTriggerConfigParams()
        self.__trigger_params_params = self.__controller.GetTriggerParamsParams()
        
        self.__trigger_config_params.Trigger1Mode = self.__KCubeTriggerConfigSettings.TriggerPortMode.TrigOUT_AtPositionFwd
        self.__trigger_config_params.Trigger1Polarity = self.__KCubeTriggerConfigSettings.TriggerPolarity.TriggerHigh

        self.__trigger_params_params.CycleCount = CONFIG.trigger_out_cycle_count
        self.__trigger_params_params.TriggerCountFwd = CONFIG.trigger_out_trigger_count
        self.__trigger_params_params.TriggerIntervalFwd = Decimal(CONFIG.trigger_out_interval_in_deg)
        self.__trigger_params_params.TriggerPulseWidth = CONFIG.trigger_out_pulse_width_in_us
        self.__trigger_params_params.TriggerStartPositionFwd = Decimal(CONFIG.trigger_out_start_position)

        self.__controller.SetTriggerParamsParams(self.__trigger_params_params)
        self.__controller.SetTriggerConfigParams(self.__trigger_config_params)   

    def set_position(self, position, absolute=False):
        if absolute:
            self.__controller.MoveTo(Decimal(position), CONFIG.move_timeout_in_ms)
        else:
            self.__controller.MoveRelative(self.__MotorDirection.Forward, Decimal(position), CONFIG.move_timeout_in_ms)

        while self.__controller.IsDeviceBusy:
            time.sleep(CONFIG.kcube_polling_interval_in_ms/1000)

    def get_position(self):
        return float(str(self.__controller.DevicePosition))

    def close(self):
        if self.__controller:
            self.__controller.DisableDevice()
            time.sleep(CONFIG.kcube_initialization_sleep_in_s)
            self.__controller.StopPolling()
            time.sleep(CONFIG.kcube_initialization_sleep_in_s)
            self.__controller.Disconnect()
            time.sleep(CONFIG.kcube_initialization_sleep_in_s)