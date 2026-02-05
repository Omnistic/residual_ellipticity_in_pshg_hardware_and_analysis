import os
import configparser

def load_config():
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read('config.ini')

    for (dll_name, dll_filename) in config.items('kinesis.dlls'):
        globals()[dll_name+'_fullpath'] = os.path.join(config['kinesis.folder']['root'], dll_filename)
        globals()[dll_name] = dll_filename[:-4]

    globals()['polarimeter_kcube'] = config['kinesis.serial_numbers']['polarimeter_kcube']
    globals()['hwp_kcube'] = config['kinesis.serial_numbers']['hwp_kcube']
    globals()['qwp_kcube'] = config['kinesis.serial_numbers']['qwp_kcube']

    globals()['kcube_polling_interval_in_ms'] = int(config['kinesis.timmings']['kcube_polling_interval_in_ms'])
    globals()['kcube_initialization_sleep_in_s'] = float(config['kinesis.timmings']['kcube_initialization_sleep_in_s'])
    globals()['home_timeout_in_ms'] = int(config['kinesis.timmings']['home_timeout_in_ms'])
    globals()['move_timeout_in_ms'] = int(config['kinesis.timmings']['move_timeout_in_ms'])

    globals()['analyzer_start_position'] = float(config['kinesis.analyzer_initialization']['analyzer_start_position'])

    globals()['trigger_out_cycle_count'] = int(config['kinesis.trigger_out_settings']['trigger_out_cycle_count'])
    globals()['trigger_out_trigger_count'] = int(config['kinesis.trigger_out_settings']['trigger_out_trigger_count'])
    globals()['trigger_out_interval_in_deg'] = float(config['kinesis.trigger_out_settings']['trigger_out_interval_in_deg'])
    globals()['trigger_out_pulse_width_in_us'] = int(config['kinesis.trigger_out_settings']['trigger_out_pulse_width_in_us'])
    globals()['trigger_out_start_position'] = float(config['kinesis.trigger_out_settings']['trigger_out_start_position'])

    globals()['nidaqmx_ai_rotation_stage_trigger'] = config['nidaqmx.channels']['ai_rotation_stage_trigger']
    globals()['nidaqmx_ai_photodiode_signal'] = config['nidaqmx.channels']['ai_photodiode_signal']
    globals()['nidaqmx_ao_photodiode_bias'] = config['nidaqmx.channels']['ao_photodiode_bias']
    globals()['nidaqmx_trigger_source'] = config['nidaqmx.channels']['trigger_source']

    globals()['nidaqmx_samples_per_channel'] = int(config['nidaqmx.timmings']['samples_per_channel'])
    globals()['nidaqmx_clock_rate'] = float(config['nidaqmx.timmings']['clock_rate'])
    globals()['nidaqmx_arm_sleep_in_seconds'] = float(config['nidaqmx.timmings']['arm_sleep_in_seconds'])
    globals()['ai_timeout_in_seconds'] = float(config['nidaqmx.timmings']['ai_timeout_in_seconds'])
    globals()['nidaqmx_calibration_duration_in_seconds'] = float(config['nidaqmx.timmings']['calibration_duration_in_seconds'])

    globals()['nidaqmx_number_of_samples_averaged_per_trigger'] = int(config['nidaqmx.acquisition_settings']['number_of_samples_averaged_per_trigger'])

    globals()['detector_max_intensity'] = float(config['detector']['max_intensity'])

    globals()['powermeter_resource'] = config['powermeter']['resource']
    globals()['powermeter_wavelength_in_nm'] = int(config['powermeter']['wavelength_in_nm'])
    globals()['powermeter_number_of_measurements'] = int(config['powermeter']['number_of_measurements'])
    globals()['powermeter_number_of_samples_averaged_per_measurement'] = int(config['powermeter']['number_of_samples_averaged_per_measurement'])
    globals()['powermeter_stabilization_in_seconds'] = float(config['powermeter']['stabilization_in_seconds'])

    globals()['c0'] = config['plotly.colors']['c0']
    globals()['c1'] = config['plotly.colors']['c1']
    globals()['c2'] = config['plotly.colors']['c2']
    globals()['c3'] = config['plotly.colors']['c3']
    globals()['c4'] = config['plotly.colors']['c4']
    globals()['c5'] = config['plotly.colors']['c5']
    globals()['c6'] = config['plotly.colors']['c6']

    globals()['hwp_mapping_steps'] = int(config['mapping.settings']['hwp_mapping_steps'])
    globals()['qwp_mapping_steps'] = int(config['mapping.settings']['qwp_mapping_steps'])

    globals()['experiment_folder'] = config['app.folders']['experiment_folder']

if __name__ == '__main__':
    load_config()