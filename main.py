import CONFIG
CONFIG.load_config()

from datetime import datetime
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from contextlib import contextmanager
from nicegui import run, ui
from plotly.subplots import make_subplots

from hardware.Analyzer import Analyzer, UnsupportedDetectorError, PowermeterNotFoundError
from hardware.Compensator import Compensator
from processing.processing import compute_polarization_parameters

def set_all_elements_enable_state(elements_list, enable, ignore_first=False):
    if ignore_first:
        actual_list = elements_list[1:]
    else:
        actual_list = elements_list

    for element in actual_list:
        if enable:
            element.enable()
        else:
            element.disable()

@contextmanager
def disable_all_while_busy(elements_list):
    set_all_elements_enable_state(elements_list, enable=False)
    try:
        yield
    finally:
        set_all_elements_enable_state(elements_list, enable=True)

def hardware_initialization():
    CONFIG.load_config()

    detector = measurement_method_toggle.value

    analyzer = None
    compensator = None
    error = None

    try:
        analyzer = Analyzer(detector)
    except PowermeterNotFoundError:
        error = 'Powermeter not found.'
    except UnsupportedDetectorError:
        error = f'Detector {detector} is not supported.'

    if polarimeter_checkbox.value == False:
        compensator = Compensator()

    return analyzer, compensator, error

def hardware_deinitialization():
    if measurement_method_toggle.value == 'Photodiode':
        bias_slide.value = 0
        clear_calibration()
    if compensator is not None:
        compensator.close()
    analyzer.close()

async def connect_hardware():
    global analyzer
    global compensator

    set_all_elements_enable_state(elements_list, enable=False)
    loading_spinner.visible = True

    if connect_switch.value:
        analyzer, compensator, error = await run.io_bound(hardware_initialization)

        if error is None:
            connect_switch.text = 'Disconnect hardware'
        else:
            ui.notify(error, type='negative')
            connect_switch.value = False

        set_all_elements_enable_state(elements_list, enable=True)
    else:
        set_all_elements_enable_state(elements_list, enable=False, ignore_first=True)

        await run.io_bound(hardware_deinitialization)

        connect_switch.text = 'Connect hardware'

    loading_spinner.visible = False
    connect_switch.enable()

def set_bias_voltage():
    analyzer.photodiode.set_bias_voltage(bias_slide.value)

def perform_single_measurement(path=None):
    global analyzer

    analyzer.snap()

    if analyzer.analog_data_valid or measurement_method_toggle.value == 'Powermeter':
        degree_of_polarization, _, degree_of_polarization_fit, _ = compute_polarization_parameters(
            np.deg2rad(analyzer.measurement_data[0]),
            analyzer.measurement_data[1],
            max_intensity=CONFIG.detector_max_intensity
            )
    else:
        degree_of_polarization = -1
        degree_of_polarization_fit = None
        return False

    if analyzer.analog_data_valid and measurement_method_toggle.value == 'Photodiode':
        analog_signal_figure.data = []
        analog_signal_figure.add_trace(go.Scatter(
            x=np.arange(analyzer.analog_data.shape[1]),
            y=analyzer.analog_data[0],
            name='Detected {} triggers'.format(analyzer.measurement_data.shape[1]),
            line={'color': CONFIG.c1 + '1.0)'}
            ), row=1, col=1)
        analog_signal_figure.add_trace(go.Scatter(
            x=np.arange(analyzer.analog_data.shape[1]),
            y=analyzer.analog_data[1],
            line={'color': CONFIG.c0 + '1.0)'},
            showlegend=False
            ), row=2, col=1)
        analog_signal_plot.update()

    processed_signal_figure.data = []
    processed_signal_figure.add_trace(go.Scatter(
        x=analyzer.measurement_data[0],
        y=analyzer.measurement_data[1],
        name='Degree of polarization = {:.6f}'.format(degree_of_polarization),
        mode='lines+markers',
        marker={
            'size': 3,
            'color': CONFIG.c0 + '1.0)'
            },
        line={'color': CONFIG.c0 + '0.3)'}
        ), row=1, col=1)
    processed_signal_figure.add_trace(go.Scatterpolar(
        r=analyzer.measurement_data[1],
        theta=analyzer.measurement_data[0],
        name='Photodiode signal',
        mode='lines+markers',
        marker={
            'size': 3,
            'color': CONFIG.c0 + '1.0)'
            },
        line={'color': CONFIG.c0 + '0.3)'},
        showlegend=False
        ), row=1, col=2)
    if degree_of_polarization_fit is not None:
        processed_signal_figure.add_trace(go.Scatter(
            x=analyzer.measurement_data[0],
            y=degree_of_polarization_fit,
            name='Fitted curve',
            line={'color': CONFIG.c2 + '1.0)'}
            ), row=1, col=1)
        processed_signal_figure.add_trace(go.Scatterpolar(
            r=degree_of_polarization_fit,
            theta=analyzer.measurement_data[0],
            line={'color': CONFIG.c2 + '1.0)'},
            showlegend=False
            ), row=1, col=2)
        
        fit_success = True
    else:
        fit_success = False
    
    processed_signal_plot.update()

    if path is not None:
        analyzer.save(path)

    return True, analyzer.missed_triggers, fit_success

def perform_hwp_mapping(folder):
    global compensator

    compensator.hwp_rotation_stage.set_position(0, absolute=True)
    hwp_mapping_step_size = int(90/(CONFIG.hwp_mapping_steps-1))
    for ii in range(CONFIG.hwp_mapping_steps):
        print(ii*hwp_mapping_step_size)
        compensator.hwp_rotation_stage.set_position(ii*hwp_mapping_step_size, absolute=True)

        path = f"{folder}/{ii:03d}"

        perform_single_measurement(path)

        experiment_progress.value = (ii+1)/CONFIG.hwp_mapping_steps

def perform_hqwp_mapping(folder):
    global compensator

    compensator.hwp_rotation_stage.set_position(0, absolute=True)
    hwp_mapping_step_size = int(90/(CONFIG.hwp_mapping_steps-1))
    qwp_mapping_step_size = int(180/(CONFIG.qwp_mapping_steps-1))
    for ii in range(CONFIG.hwp_mapping_steps):
        print(ii*hwp_mapping_step_size)
        compensator.hwp_rotation_stage.set_position(ii*hwp_mapping_step_size, absolute=True)

        for jj in range(CONFIG.qwp_mapping_steps):
            compensator.qwp_rotation_stage.set_position(jj*qwp_mapping_step_size, absolute=True)

            path = f"{folder}/HWP-{ii:03d}_QWP-{jj:03d}"

            perform_single_measurement(path)

        experiment_progress.value = (ii+1)/CONFIG.hwp_mapping_steps    

def perform_compensation_test(folder):
    # Very ugly, TODO: clean this up!
    global compensator

    import pickle
    filepath = r'...\\calib.pkl'
    file = open(filepath, 'rb')
    motor_angles = pickle.load(file)
    file.close()

    HWP_angles = motor_angles[0,:]
    QWP_angles = motor_angles[1,:]

    for ii in range(len(HWP_angles)):
        compensator.hwp_rotation_stage.set_position(HWP_angles[ii], absolute=True)
        compensator.qwp_rotation_stage.set_position(QWP_angles[ii], absolute=True)
        path = f"{folder}/HWP-{ii:03d}"
        perform_single_measurement(path)
        experiment_progress.value = (ii+1)/len(HWP_angles)  

async def single_measurement():
    with disable_all_while_busy(elements_list):
        loading_spinner.visible = True

        path = None

        if save_measurement_checkbox.value:
            folder = folder_path_input.value
            experiment_name = experiment_name_input.value

            Path(folder).mkdir(parents=True, exist_ok=True)

            current_datetime = datetime.now().strftime("%Y%m%dT%H%M%SZ")
            
            if experiment_name != "":
                experiment_name = f"_{experiment_name}"

            path = f"{folder}/{current_datetime}{experiment_name}"


        single_measurement_success, missing_analog_triggers, fit_success = await run.io_bound(perform_single_measurement, path)

        if not single_measurement_success:
            ui.notify('Unable to acquire data, check DAQ timeout if using Photodiode.', type='warning')

        if missing_analog_triggers > 0:
            ui.notify(f'Missing {missing_analog_triggers} analog triggers.', type='warning')

        if not fit_success:
            ui.notify('Unable to fit intensity data.', type='warning')

        loading_spinner.visible = False
        loading_spinner.value = 0

async def hwp_mapping():
    with disable_all_while_busy(elements_list):
        experiment_progress.visible = True

        folder = f"{folder_path_input.value}/{datetime.now().strftime('%Y%m%dT%H%M%SZ')}_HWP_mapping"
        Path(folder).mkdir(parents=True, exist_ok=True)

        await run.io_bound(perform_hwp_mapping, folder)

        experiment_progress.visible = False

async def hqwp_mapping():
    with disable_all_while_busy(elements_list):
        experiment_progress.visible = True

        folder = f"{folder_path_input.value}/{datetime.now().strftime('%Y%m%dT%H%M%SZ')}_HQWP_mapping"
        Path(folder).mkdir(parents=True, exist_ok=True)

        await run.io_bound(perform_hqwp_mapping, folder)

        experiment_progress.visible = False

async def test_compensation():
    with disable_all_while_busy(elements_list):
        experiment_progress.visible = True

        folder = f"{folder_path_input.value}/{datetime.now().strftime('%Y%m%dT%H%M%SZ')}_compensation_test"
        Path(folder).mkdir(parents=True, exist_ok=True)

        await run.io_bound(perform_compensation_test, folder)

        experiment_progress.visible = False

async def calibration_measurement():
    with disable_all_while_busy(elements_list):
        calibration_progress.visible = True
        calibration_timer.activate()
        await run.io_bound(analyzer.photodiode.calibrate)
        calibration_label.text = f'Calibration offset: {1000 * analyzer.photodiode.calibration_mean:.3f}±{1000 * analyzer.photodiode.calibration_std:.3f}mV'
        calibration_timer.deactivate()
        calibration_progress.visible = False
        calibration_progress.value = 0

def clear_calibration():
    analyzer.photodiode.calibration_mean = 0
    analyzer.photodiode.calibration_std = 0
    calibration_label.text = 'No calibration offset'

def create_analog_signal_figure():
    analog_signal_figure = make_subplots(rows=2, shared_xaxes=True, x_title='Samples @ 25kS/s', vertical_spacing=0.1)
    analog_signal_figure.update_layout(
        margin=dict(l=50, r=50, t=10, b=50),
        showlegend=True,
        xaxis_range=[0, 9000],
        template='plotly_dark'
    )
    analog_signal_figure['layout']['yaxis']['title']='Dev1/ai0:stage trigger (V)'
    analog_signal_figure['layout']['yaxis2']['title']='Dev1/ai1:photodiode signal (V)'

    analog_signal_figure.add_trace(go.Scatter(x=np.arange(9000), y=np.arange(5), visible=False), row=1, col=1)
    analog_signal_figure.add_trace(go.Scatter(x=np.arange(9000), y=np.arange(5), visible=False), row=2, col=1)

    return analog_signal_figure

def create_processed_signal_figure():
    processed_signal_figure = make_subplots(cols=2, specs=[[{'type': 'xy'}, {'type': 'polar'}]])
    processed_signal_figure.update_layout(
        xaxis=dict(range=[0, 360], tickmode='linear', dtick='30', minor=dict(dtick='10', showgrid=True)),
        margin=dict(l=50, r=50, t=10, b=50),
        showlegend=True,
        template='plotly_dark'
    )
    processed_signal_figure['layout']['xaxis']['title']='Analyzer motor angle (deg)'
    processed_signal_figure['layout']['yaxis']['title']='Photodiode signal (V)'

    processed_signal_figure.add_trace(go.Scatter(x=np.arange(360), y=np.sin(np.deg2rad(np.arange(360)))**2, visible=False), row=1, col=1)
    processed_signal_figure.add_trace(go.Scatterpolar(r=np.sin(np.deg2rad(np.arange(360)))**2, theta=np.arange(360), visible=False), row=1, col=2)

    return processed_signal_figure

def analog_visibility():
    if measurement_method_toggle.value == 'Photodiode':
        analog_signal_plot.set_visibility(True)
        calibration_measurement_button.set_visibility(True)
        calibration_clear_button.set_visibility(True)
        calibration_label.set_visibility(True)
        bias_card.set_visibility(True)
    else:
        analog_signal_plot.set_visibility(False)
        calibration_measurement_button.set_visibility(False)
        calibration_clear_button.set_visibility(False)
        calibration_label.set_visibility(False)
        bias_card.set_visibility(False)

with ui.row():
    connect_switch = ui.switch('Connect hardware', on_change=connect_hardware).style('font-size: 1.5em;')
    polarimeter_checkbox = ui.checkbox('Polarimeter only').style('font-size: 1.5em;').bind_enabled_from(connect_switch, 'value', backward=lambda v: not v)

measurement_method_toggle = ui.toggle(['Photodiode', 'Powermeter'], value='Photodiode', on_change=analog_visibility).bind_enabled_from(connect_switch, 'value', backward=lambda v: not v)

processed_signal_figure = create_processed_signal_figure()
processed_signal_plot = ui.plotly(processed_signal_figure).classes('w-full').style('height: 600px;')

with ui.row():
    save_measurement_checkbox = ui.checkbox('Save measurements', value=False).style('font-size: 170%; font-weight: 300')
    save_measurement_checkbox.disable()

with ui.row():
    folder_path_input = ui.input(label='Destination folder', value=CONFIG.experiment_folder).classes('w-96')
    experiment_name_input = ui.input(label='Experiment name', placeholder='polarization').classes('w-96')
    folder_path_input.bind_visibility_from(save_measurement_checkbox, 'value')
    experiment_name_input.bind_visibility_from(save_measurement_checkbox, 'value')

with ui.card() as bias_card:
    bias_slide = ui.slider(min=0, max=10, value=0, step=0.1).classes('w-96').on_value_change(set_bias_voltage)
    ui.label().bind_text_from(bias_slide, 'value', backward=lambda bias: f'Bias voltage: {bias}V').style('font-size: 170%; font-weight: 300')
    bias_slide.disable()

with ui.row():
    calibration_measurement_button = ui.button('Calibrate', on_click=calibration_measurement)
    calibration_measurement_button.disable()
    calibration_clear_button = ui.button('Clear calibration', on_click=clear_calibration)
    calibration_clear_button.disable()
    calibration_label = ui.label('No calibration offset').style('font-size: 170%; font-weight: 300')

with ui.row():
    single_measurement_button = ui.button('Acquire single measurement', on_click=single_measurement)
    hwp_mapping_button = ui.button('Polarization mapping with HWP', on_click=hwp_mapping)
    hqwp_mapping_button = ui.button('Polarization mapping with HWP and QWP', on_click=hqwp_mapping)
    test_compensation_button = ui.button('Test compensation', on_click=test_compensation)
    single_measurement_button.disable()
    hwp_mapping_button.disable()
    hqwp_mapping_button.disable()
    test_compensation_button.disable()

calibration_progress = ui.circular_progress(show_value=False, size='100px').props('instant-feedback').classes('absolute-center')
calibration_timer = ui.timer(0.1, lambda: calibration_progress.set_value(calibration_progress.value + 0.1 / CONFIG.nidaqmx_calibration_duration_in_seconds), active=False)
calibration_progress.visible = False

experiment_progress = ui.circular_progress(show_value=False, size='100px').props('instant-feedback').classes('absolute-center')
experiment_progress.visible = False

loading_spinner = ui.spinner(size=200).classes('absolute-center')
loading_spinner.visible = False

analog_signal_figure = create_analog_signal_figure()
analog_signal_plot = ui.plotly(analog_signal_figure).classes('w-full').style('height: 500px;')

elements_list = [
    connect_switch,
    save_measurement_checkbox,
    hwp_mapping_button,
    hqwp_mapping_button,
    test_compensation_button,
    single_measurement_button,
    calibration_measurement_button,
    calibration_clear_button,
    bias_slide]

ui.run(
    port=80,
    title='Polarization Control',
    favicon='🔧',
    dark=True
)