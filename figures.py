import CONFIG
CONFIG.load_config()

from processing.processing import compute_polarization_parameters, compute_system_parameters, phi_motor_for_linear_polarization

import numpy as np
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go

ROOT_FOLDER = r'..\raw_data_root'
HWP_ONLY_SUBFOLDERS = [
    r'hwp_only_before\20251001T100150Z_HWP_mapping',
    r'hwp_only_after\20251001T170811Z_HWP_mapping'
]
HQWP_SUBFOLDERS = [
    r'hwp_qwp_before\20251001T101558Z_HQWP_mapping',
    r'hwp_qwp_after\20251001T135537Z_HQWP_mapping'
]
# === Uncomment to use replicate data (same maps, taken a different day) === #
# HQWP_SUBFOLDERS = [
#     r'hwp_qwp_before_replicate\20250917T101445Z_HQWP_mapping',
#     r'hwp_qwp_after_replicate\20250917T110448Z_HQWP_mapping'
# ]
BEFORE_AFTER_SUBFOLDERS = [
    r'hwp_only_after\20251001T170811Z_HWP_mapping',
    r'comp_after_1\20251001T143516Z_compensation_test',
    r'comp_after_2\20251001T142755Z_compensation_test'
]       

PD_VS_PM_SUBFOLDERS = [
    'beam_only',
    'qwp_only_35_lin',
    'qwp_only_40',
    'qwp_only_45',
    'qwp_only_50',
    'qwp_only_65',
    'qwp_only_80_circ'
]
QWP_STATES = [
    'No QWP',
    'QWP @ 0°',
    'QWP @ 5°',
    'QWP @ 10°',
    'QWP @ 15°',
    'QWP @ 30°',
    'QWP @ 45°'
]
UPPER_HALF_Y_RANGE_FACTOR = 1
LOWER_HALF_Y_RANGE_FACTOR = 5
Y_RANGE_STEP = 0.005

HWP_MEAS_LOC = [
    'Entrance Port',
    'Sample Plane'
]
HWP_MEAS_COL = [
    CONFIG.c5+' 1)',
    CONFIG.c4+' 1)',
    CONFIG.c4+' 1)'
]
HWP_MEAS_COL_OPA = [
    CONFIG.c5+' 0.3)',
    CONFIG.c4+' 0.3)',
    CONFIG.c4+' 0.3)'
]

HQWP_NUM_HWP = 19
HQWP_NUM_QWP = 37
NUM_POL = 360

COMPENSATION_FILENAME = 'hqwp_compensation'

BEFORE_AFTER_LABELS = [
    'HWP',
    'HWP+QWP',
    'HWP+QWP*'
]
BEFORE_AFTER_SYMBOLS = [
    'circle',
    'cross',
    'x'
]
BEFORE_AFTER_COL = [
    CONFIG.c5+' 1)',
    CONFIG.c4+' 0.7)',
    CONFIG.c4+' 0.7)'
]

def pd_vs_pm():
    first_legend=True
    fig = make_subplots(rows=1, cols=len(PD_VS_PM_SUBFOLDERS), horizontal_spacing=0.07)
    for ii, subfolder in enumerate(PD_VS_PM_SUBFOLDERS):
        folder = os.path.join(ROOT_FOLDER, subfolder)
        files = os.listdir(folder)
        pd_ellipticity = []
        pm_ellipticity = []
        for file in files:
            fullpath = os.path.join(folder, file)
            data = np.load(fullpath)['measurement_data']
            ee, _, _, _, _ = compute_polarization_parameters(np.deg2rad(data[0,:]), data[1,:], max_intensity=CONFIG.detector_max_intensity)
            if 'PD' in file:
                pd_ellipticity.append(ee)
            elif 'PM' in file:
                pm_ellipticity.append(ee)

        fig.add_trace(go.Box(
            x=[QWP_STATES[ii]]*len(pd_ellipticity),
            y=pd_ellipticity,
            name='Photodiode',
            offsetgroup='A',
            boxpoints='all',
            showlegend=first_legend,
            marker_color=CONFIG.c5+' 255)',
            marker_opacity=0.7
        ), row=1, col=ii+1)
        fig.add_trace(go.Box(
            x=[QWP_STATES[ii]]*len(pm_ellipticity),
            y=pm_ellipticity,
            name='Powermeter',
            offsetgroup='B',
            boxpoints='all',
            showlegend=first_legend,
            marker_color=CONFIG.c4+' 255)',
            marker_opacity=0.7
        ), row=1, col=ii+1)
        center = np.median(pm_ellipticity)
        lower_range = center-LOWER_HALF_Y_RANGE_FACTOR*Y_RANGE_STEP
        upper_range = center+UPPER_HALF_Y_RANGE_FACTOR*Y_RANGE_STEP
        ticks = np.arange(lower_range, upper_range+Y_RANGE_STEP, Y_RANGE_STEP)
        ticks = np.append(ticks, 0)
        tick_texts = []
        for tick in ticks[ticks>=0]:
            if np.isclose(tick, center, atol=Y_RANGE_STEP/10):
                tick_texts.append(f"<b>{tick:.3f}</b>")
            else:
                tick_texts.append(f"{tick:.3f}")
        fig.update_yaxes(
            showgrid=True,
            range=[lower_range-0.001, upper_range],
            tickmode='array',
            tickvals=ticks[ticks>=0],
            ticktext=tick_texts,
            tickfont=dict(size=16),
            row=1,
            col=ii+1
        )
        first_legend=False
    fig.update_layout(
        width=1000,
        height=800,
        margin=dict(l=70, r=50, t=50, b=70),
        template='simple_white',
        font_family='crm12',
        legend=dict(
            font=dict(size=16),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        boxmode='group'
    )
    fig.update_xaxes(
        tickfont=dict(size=16)
    )
    fig.update_yaxes(
        title_text='Ellipticity (-)',
        title_font=dict(size=20),
        row=1, col=1
    )
    fig.show()
    # fig.write_image(r'pd_vs_pm.pdf', width=1000, height=800)

def hwp_only():
    fig = go.Figure()
    for ii, subfolder in enumerate(HWP_ONLY_SUBFOLDERS):
        folder = os.path.join(ROOT_FOLDER, subfolder)
        files = os.listdir(folder)
        polarization_angle = []
        ellipticity = []
        for file in files:
            fullpath = os.path.join(folder, file)
            data = np.load(fullpath)['measurement_data']
            ee, _, al, _, _ = compute_polarization_parameters(np.deg2rad(data[0,:]), data[1,:], max_intensity=CONFIG.detector_max_intensity)
            polarization_angle.append(al)
            ellipticity.append(ee)
        polarization_angle = np.rad2deg(polarization_angle)
        inds = np.argsort(polarization_angle)
        sorted_polarization_angle = polarization_angle[inds]
        sorted_ellipticity = np.array(ellipticity)[inds]
        fig.add_trace(go.Scatter(
            x=sorted_polarization_angle,
            y=sorted_ellipticity,
            mode='lines+markers',
            name=HWP_MEAS_LOC[ii],
            marker=dict(
                size=5,
                color=HWP_MEAS_COL[ii]
            ),
            line=dict(
                width=2,
                color=HWP_MEAS_COL[ii]
            )
        ))
        fig.add_scatter(
            x=[polarization_angle[0], polarization_angle[0]],
            y=[0, 0.26],
            mode='lines',
            line=dict(dash='dash', width=3, color=HWP_MEAS_COL_OPA[ii]),
            showlegend=False
        )
    fig.update_xaxes(
        title_text='Relative Polarization Angle (deg)',
        title_font=dict(size=20),
        showgrid=True,
        automargin=False,
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 45, 90, 135, 180],
        range=[0, 180]
    )
    fig.update_yaxes(
        title_text='Ellipticity (-)',
        title_standoff=20,
        title_font=dict(size=20),
        showgrid=True,
        automargin=False,
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 0.05, 0.1, 0.15, 0.2, 0.25],
        range=[0, 0.26]
    )
    fig.update_layout(
        width=500,
        height=400,
        margin=dict(l=70, r=50, t=50, b=70),
        template='simple_white',
        font_family='crm12',
        legend=dict(
            font=dict(size=16),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    fig.show()
    # fig.write_image(r'hwp_only.pdf', width=500, height=400)

def create_map(folder):
    hwp_motor_angles = np.linspace(0, 90, HQWP_NUM_HWP)
    qwp_motor_angles = np.linspace(0, 180, HQWP_NUM_QWP)
    pol_motor_angles = np.linspace(0, 360, NUM_POL, endpoint=False)

    ellipticity = np.full((len(hwp_motor_angles), len(qwp_motor_angles)), np.nan)
    polarization_angle = np.full((len(hwp_motor_angles), len(qwp_motor_angles)), np.nan)
    aggregated_intensities = np.zeros((HQWP_NUM_HWP*HQWP_NUM_QWP*NUM_POL))

    for hh in range(HQWP_NUM_HWP):
        for qq in range(HQWP_NUM_QWP):
            filename = f'HWP-{hh:03d}_QWP-{qq:03d}.npz'
            fullpath = os.path.join(folder, filename)
            data = np.load(fullpath)['measurement_data']
            aggregated_intensities[hh*HQWP_NUM_QWP*NUM_POL+qq*NUM_POL:hh*HQWP_NUM_QWP*NUM_POL+qq*NUM_POL+NUM_POL] = data[1,:]
            ee, _, aa, _, _ = compute_polarization_parameters(np.deg2rad(data[0,:]), data[1,:], max_intensity=CONFIG.detector_max_intensity)
            ellipticity[hh, qq] = ee
            polarization_angle[hh, qq] = aa
        
    alpha_prime = np.tile(pol_motor_angles, len(hwp_motor_angles) * len(qwp_motor_angles))
    phi_prime = np.tile(np.repeat(qwp_motor_angles, len(pol_motor_angles)), len(hwp_motor_angles))
    theta_prime = np.repeat(hwp_motor_angles, len(qwp_motor_angles) * len(pol_motor_angles))

    alpha_prime = alpha_prime.reshape(-1, 1).T
    phi_prime = phi_prime.reshape(-1, 1).T
    theta_prime = theta_prime.reshape(-1, 1).T

    primes = np.deg2rad(np.vstack((theta_prime, phi_prime, alpha_prime)))

    _, _, delta, theta_0, phi_0, _ = compute_system_parameters(primes, aggregated_intensities)
    theta_motor = np.linspace(0, np.pi/2, 91)
    initial_guess = np.deg2rad([30, 125])
    phi_motor_solution_1, phi_motor_solution_2 = phi_motor_for_linear_polarization(theta_motor, theta_0, phi_0, delta, initial_guess=initial_guess)

    theta_motor = np.rad2deg(theta_motor)
    phi_motor_solution_1 = np.rad2deg(phi_motor_solution_1)
    phi_motor_solution_2 = np.rad2deg(phi_motor_solution_2)

    if np.amin(phi_motor_solution_1) < 0:
        phi_motor_solution_1 += 180
    if np.amin(phi_motor_solution_2) < 0:
        phi_motor_solution_2 += 180

    # Ellipticity vs polarization (coarse sampling)
    ellipticity_along_fit = []
    polarization_angle_along_fit = []
    for ii, hh in enumerate(theta_motor[::5]):
        qq = round(phi_motor_solution_1[ii*5]/5)
        ellipticity_along_fit.append(ellipticity[round(hh/5), qq])
        polarization_angle_along_fit.append(polarization_angle[round(hh/5), qq])

    inds = np.argsort(polarization_angle_along_fit)
    polarization_angle_along_fit = np.rad2deg(polarization_angle_along_fit)[inds]
    ellipticity_along_fit = np.array(ellipticity_along_fit)[inds]

    return ellipticity, theta_motor, phi_motor_solution_1, phi_motor_solution_2, ellipticity_along_fit, polarization_angle_along_fit

def hqwp():
    fig = make_subplots(
        rows=len(HQWP_SUBFOLDERS),
        cols=1,shared_xaxes=True,
        x_title='QWP Motor Angle (deg)',
        y_title='HWP Motor Angle (deg)',
        subplot_titles=(HWP_MEAS_LOC[0], HWP_MEAS_LOC[1])
    )
    custom_colorscale = [
        [0.0, CONFIG.c5+' 255)'],
        [0.5, 'rgba(255,255,255, 255)'],
        [1.0, CONFIG.c4+' 255)']
    ]

    for ii, subfolder in enumerate(HQWP_SUBFOLDERS):
        folder = os.path.join(ROOT_FOLDER, subfolder)
        ellipticity, theta_motor, phi_motor_solution_1, phi_motor_solution_2, _, _ = create_map(folder)

        np.savez(COMPENSATION_FILENAME,
                 hwp=theta_motor,
                 qwp_1=phi_motor_solution_1,
                 qwp_2=phi_motor_solution_2
        )

        fig.add_trace(go.Heatmap(
            z=ellipticity,
            x=np.linspace(0, 180, HQWP_NUM_QWP),
            y=np.linspace(0, 90, HQWP_NUM_HWP),
            coloraxis='coloraxis'
        ), row=ii+1, col=1)
        fig.add_trace(go.Scatter(
            x=phi_motor_solution_1,
            y=theta_motor,
            mode='lines',
            line=dict(
                color='black',
                width=1.5,
                dash='dot'
            ),
            showlegend=False
        ), row=ii+1, col=1)
        fig.add_trace(go.Scatter(
            x=phi_motor_solution_2,
            y=theta_motor,
            mode='lines',
            line=dict(
                color='black',
                width=1.5,
                dash='dot'
            ),
            showlegend=False
        ), row=ii+1, col=1)
    fig.update_xaxes(
        tickmode='array',
        tickvals=[0, 30, 60, 90, 120, 150, 180],
        row=1, col=1
    )
    fig.update_xaxes(
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 30, 60, 90, 120, 150, 180],
        row=2, col=1
    )
    fig.update_yaxes(
        range=[0, 90],
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 30, 60, 90],
        row=1, col=1
    )
    fig.update_yaxes(
        range=[0, 90],
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 30, 60, 90],
        row=2, col=1
    )
    fig.update_layout(
        width=500,
        height=400,
        margin=dict(l=70, r=50, t=50, b=70),
        template='simple_white',
        font_family='crm12',
        coloraxis=dict(
            cmin=0,
            cmax=1,
            colorscale=custom_colorscale,
            colorbar_lenmode='pixels',
            colorbar_len=280,
            colorbar_thickness=15,
            colorbar_title='Ellipticity (-)',
            colorbar_title_font=dict(size=20),
            colorbar_tickfont=dict(size=16),
            colorbar_tickmode='array',
            colorbar_tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1],
            colorbar_ticktext=['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'],
        ),
        annotations=[
            dict(
                font=dict(size=20)
            ) for annotation in fig.layout.annotations
        ]
    )
    fig.show()
    # fig.write_image(r'hwp_qwp_map.pdf', width=500, height=400)

def before_after():
    fig = go.Figure()
    for ii, subfolder in enumerate(BEFORE_AFTER_SUBFOLDERS):
        folder = os.path.join(ROOT_FOLDER, subfolder)
        files = os.listdir(folder)
        polarization_angle = []
        ellipticity = []
        for file in files:
            fullpath = os.path.join(folder, file)
            data = np.load(fullpath)['measurement_data']
            ee, _, al, fit, _ = compute_polarization_parameters(np.deg2rad(data[0,:]), data[1,:], max_intensity=CONFIG.detector_max_intensity)
            polarization_angle.append(al)
            ellipticity.append(ee)
            # if ii==0 and file=='055.npz':
            #     fig = go.Figure()
            #     fig.add_trace(go.Scatter(
            #         x=np.deg2rad(data[0,:]),
            #         y=data[1,:]
            #     ))
            #     fig.add_trace(go.Scatter(
            #         x=np.deg2rad(data[0,:]),
            #         y=fit
            #     ))
            #     fig.update_layout(
            #         title=f'{ee} {file}'
            #     )
            #     fig.show()
        polarization_angle = np.rad2deg(polarization_angle)
        inds = np.argsort(polarization_angle)
        sorted_polarization_angle = polarization_angle[inds]
        sorted_ellipticity = np.array(ellipticity)[inds]
        fig.add_trace(go.Scatter(
            x=sorted_polarization_angle,
            y=sorted_ellipticity,
            mode='lines+markers',
            name=BEFORE_AFTER_LABELS[ii],
            marker=dict(
                size=5,
                symbol=BEFORE_AFTER_SYMBOLS[ii],
                color=BEFORE_AFTER_COL[ii]
            ),
            line=dict(
                width=2,
                color=BEFORE_AFTER_COL[ii]
            )
        ))
        fig.add_scatter(
            x=[polarization_angle[0], polarization_angle[0]],
            y=[0, 0.3],
            mode='lines',
            line=dict(dash='dash', width=3, color=HWP_MEAS_COL_OPA[ii]),
            showlegend=False
        )
    fig.update_xaxes(
        title_text='Relative Polarization Angle (deg)',
        title_font=dict(size=20),
        showgrid=True,
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 45, 90, 135, 180],
        range=[0, 180]
    )
    fig.update_yaxes(
        title_text='Ellipticity (-)',
        title_font=dict(size=20),
        showgrid=True,
        tickfont=dict(size=16),
        tickmode='array',
        tickvals=[0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3],
        range=[0, 0.30]
    )
    fig.update_layout(
        width=500,
        height=400,
        margin=dict(l=70, r=50, t=50, b=70),
        template='simple_white',
        font_family='crm12',
        legend=dict(
            font=dict(size=16),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    fig.show()
    # fig.write_image(r'before_after.pdf', width=500, height=400)

if __name__ == '__main__':
    pd_vs_pm()
    hwp_only()
    hqwp()
    before_after()