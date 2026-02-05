import numpy as np
from numpy import sin, cos
import os, re
import plotly.graph_objects as go
from scipy.optimize import curve_fit, root


def linear_polarization(phi, theta, delta):
    return np.tan(2*phi) + np.tan(delta) * np.sin(2 * (2*theta - phi))

def phi_motor_for_linear_polarization(theta_motor, theta_0, phi_0, delta, initial_guess=[0, 0]):
    theta = theta_motor - theta_0

    phi_motor_solution_1 = []
    phi_motor_solution_2 = []

    for t in theta:
        phi_solution_1 = root(linear_polarization, initial_guess[0], args=(t, delta), method='lm')['x'][0]
        phi_solution_2 = root(linear_polarization, initial_guess[1], args=(t, delta), method='lm')['x'][0]
        phi_motor_solution_1.append(phi_solution_1+phi_0)
        phi_motor_solution_2.append(phi_solution_2+phi_0)

    phi_motor_solution_1 = np.array(phi_motor_solution_1)
    phi_motor_solution_2 = np.array(phi_motor_solution_2)

    return phi_motor_solution_1, phi_motor_solution_2

def polarimeter_intensity(alpha: float, alpha_max: float, k: float, e_min: float) -> float:
    e_max = e_min + k**2
    return e_max**2 * cos(alpha_max - alpha)**2 + e_min**2 * sin(alpha_max - alpha)**2

def compute_polarization_parameters(angles: np.ndarray, intensity: np.ndarray, fit_factor: float = 1E4, max_intensity: float = 10):
    scaled_intensity = intensity * fit_factor
    max_scaled_intensity = max_intensity * fit_factor

    try:
        popt, _ = curve_fit(
            polarimeter_intensity, 
            angles, 
            scaled_intensity, 
            bounds=((0, 0, 0), (np.pi, max_scaled_intensity**0.5, max_scaled_intensity**0.5))
        )
    except RuntimeError:
        return -1, -1, None, np.inf

    alpha_max, k, scaled_e_min = popt

    scaled_e_max = k**2 + scaled_e_min
    ellipticity = scaled_e_min / scaled_e_max
    e_max = scaled_e_max / fit_factor**0.5

    fitted_intensity = polarimeter_intensity(angles, *popt) / fit_factor

    rmse = np.sqrt(np.mean((intensity - fitted_intensity) ** 2))
    nrmse = rmse / np.mean(intensity)

    return ellipticity, e_max, alpha_max, fitted_intensity, nrmse

def general_intensity(primes, intensity_0, gamma, delta, theta_0, phi_0, alpha_0):
    theta_prime, phi_prime, alpha_prime = primes

    theta = theta_prime - theta_0
    phi = phi_prime - phi_0
    alpha = alpha_prime - alpha_0

    two_theta_minus_phi = 2*theta - phi

    d_1 = -gamma * ( cos(delta)*sin(phi)*sin(two_theta_minus_phi) + sin(delta)*cos(phi)*cos(two_theta_minus_phi) )
    d_2 = -gamma * ( sin(delta)*sin(phi)*sin(two_theta_minus_phi) - cos(delta)*cos(phi)*cos(two_theta_minus_phi) )
    d_3 = sin(phi)*cos(two_theta_minus_phi)
    d_4 = cos(phi)*sin(two_theta_minus_phi)

    return intensity_0 * ( (d_1**2 + d_2**2)*cos(alpha)**2 + (d_3**2 + d_4**2)*sin(alpha)**2 + 2*(d_1*d_3 + d_2*d_4)*sin(alpha)*cos(alpha) )

def compute_system_parameters(primes, aggregated_intensities, fit_factor=1E4, max_intensity=10):
    scaled_aggregated_intensities = aggregated_intensities * fit_factor
    max_scaled_intensity = max_intensity * fit_factor
    popt, _, _, msg, _ = curve_fit(
        general_intensity,
        primes,
        scaled_aggregated_intensities,
        p0 = [fit_factor, 1, 0, 0, 0, 0],
        bounds=([0, 0, -np.pi, -np.pi, -np.pi, -np.pi], [max_scaled_intensity, np.inf, np.pi, np.pi, np.pi, np.pi]),
        full_output=True
    )

    fit = general_intensity(primes, *popt)
    rmse = np.sqrt(np.mean((aggregated_intensities - fit) ** 2))

    # print(popt, rmse)
    # print(msg)

    # fig = go.Figure(data=go.Scatter(x=np.arange(len(aggregated_intensities)), y=aggregated_intensities))
    # fig.add_trace(go.Scatter(x=np.arange(len(aggregated_intensities)), y=fit))
    # fig.show()

    intensity_0 = popt[0] / fit_factor
    gamma = popt[1]
    delta = popt[2]
    theta_0 = popt[3]
    phi_0 = popt[4]
    alpha_0 = popt[5]

    print(f"Intensity_0: {intensity_0:.2f}, Gamma: {gamma:.2f}, Delta: {np.rad2deg(delta):.2f}, Theta_0: {np.rad2deg(theta_0):.2f}, Phi_0: {np.rad2deg(phi_0):.2f}, Alpha_0: {np.rad2deg(alpha_0):.2f}")


    return intensity_0, gamma, delta, theta_0, phi_0, alpha_0

def process_hwp_map(folder):
    data_files = [ff for ff in os.listdir(folder) if re.match(r"\d{3}.npz", ff)]
    number_of_files = len(data_files)

    hwp_angles = np.linspace(0, np.pi, number_of_files, endpoint=False)
    ellipticity = np.zeros(number_of_files)

    for ii in range(number_of_files):
        measurement_data = np.load(os.path.join(folder, data_files[ii]))['measurement_data']
        ellipticity[ii], _, _, _ = compute_polarization_parameters(np.deg2rad(measurement_data[0, :]), measurement_data[1, :])

    return hwp_angles, ellipticity

def compare_hwp_map(powermeter_hwp_angles, powermeter_ellipticity, photodiode_hwp_angles, photodiode_ellipticity):
    fig = go.Figure(data=go.Scatter(name='Powermeter', x=powermeter_hwp_angles, y=powermeter_ellipticity, mode='markers'), layout_yaxis_range=[0, 1])
    fig.add_trace(go.Scatter(name='Photodiode', x=photodiode_hwp_angles, y=photodiode_ellipticity, mode='markers'))
    fig.update_layout(template='plotly_dark', xaxis=dict(title=dict(text='HWP Rotation Stage Angle [deg]')), yaxis=dict(title=dict(text='Degree of Polarization')), legend=dict(font=dict(size=20)))
    fig.show()
    