"""
Single Block Verification Tests for PyFEHM

Test 1: Mass injection into closed block - verify pressure rise matches compressibility
Test 2: Heat injection into closed block - verify temperature rise matches heat capacity

Grid: 2x2x2 nodes = 1 element of 1 m³
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Add parent directory to path for PyFEHM imports
PYFEHM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PYFEHM_ROOT)

# FEHM executable path (relative to PyFEHM root)
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

from fdata import fdata, fmacro
from fvars import dens, enth
from fpost import fhistory


def compute_compressibility(P, T):
    """
    Compute isothermal compressibility of water: beta = (1/ρ)(dρ/dP)

    Parameters:
        P: Pressure in MPa
        T: Temperature in °C

    Returns:
        beta: Compressibility in 1/MPa
    """
    rho_result = dens(P, T)[0]  # liquid density result
    drho_dP_result = dens(P, T, 'P')[0]  # dρ/dP result

    # Handle both scalar and array returns
    rho = float(np.atleast_1d(rho_result)[0])  # kg/m³
    drho_dP = float(np.atleast_1d(drho_dP_result)[0])  # kg/m³/MPa

    beta = drho_dP / rho  # 1/MPa
    return beta, rho


def compute_water_heat_capacity(P, T):
    """
    Compute specific heat capacity of water: c_p = dh/dT

    Parameters:
        P: Pressure in MPa
        T: Temperature in °C

    Returns:
        c_p: Specific heat capacity in MJ/kg/K (FEHM units)
    """
    # dh/dT gives specific heat in MJ/kg/K (FEHM enthalpy units)
    dh_dT_result = enth(P, T, 'T')[0]
    dh_dT = float(np.atleast_1d(dh_dT_result)[0])
    return dh_dT


def run_mass_injection_test(work_dir='test_mass'):
    """
    Test 1: Mass injection into closed block

    Physics:
        - Closed system, isothermal (approximately)
        - Mass injection rate: ṁ kg/s
        - dP/dt = ṁ / (V_pore × ρ(P) × beta(P))
        - where V_pore = φ × V, beta = compressibility (pressure-dependent)
    """
    print("\n" + "="*60)
    print("TEST 1: Mass Injection - Compressibility Verification")
    print("="*60)

    # Parameters
    V = 1.0  # m³ (block volume)
    phi = 0.1  # porosity
    V_pore = V * phi  # pore volume in m³

    P0 = 1.0  # initial pressure (MPa)
    T0 = 25.0  # initial temperature (°C)

    # Compute compressibility at initial conditions
    beta0, rho0 = compute_compressibility(P0, T0)
    print(f"\nInitial conditions:")
    print(f"  P0 = {P0} MPa")
    print(f"  T0 = {T0} °C")
    print(f"  Porosity = {phi}")
    print(f"  Pore volume = {V_pore} m³")
    print(f"  Water density = {rho0:.2f} kg/m³")
    print(f"  Compressibility = {beta0:.6e} 1/MPa")

    # Mass injection rate (kg/s) - use very small rate for reasonable dP
    # Target: ~1 MPa increase over 1 day
    # dP/dt = ṁ_total / (V_pore × ρ × beta)
    # ṁ_total = dP/dt × V_pore × ρ × beta
    # NOTE: FEHM flow macro applied to zone 0 applies rate to EACH of the 8 nodes
    n_nodes = 8  # 2x2x2 grid
    target_dP_per_day = 1.0  # MPa/day
    mass_rate_total = target_dP_per_day / 86400 * V_pore * rho0 * beta0  # total kg/s
    mass_rate_per_node = mass_rate_total / n_nodes  # rate per node

    # Expected pressure rise rate assuming CONSTANT compressibility (old method)
    dP_dt_constant = mass_rate_total / (V_pore * rho0 * beta0)  # MPa/s
    dP_dt_constant_per_day = dP_dt_constant * 86400  # MPa/day

    print(f"\nTotal mass injection rate = {mass_rate_total:.6e} kg/s")
    print(f"Rate per node = {mass_rate_per_node:.6e} kg/s")

    # Simulation time (days)
    tf = 1.0  # days
    expected_dP_constant = dP_dt_constant_per_day * tf

    # Integrate ODE with VARIABLE compressibility: dP/dt = ṁ / (V_pore × ρ(P) × beta(P))
    def dP_dt_ode(t, P):
        """ODE for pressure evolution with pressure-dependent compressibility."""
        beta_P, rho_P = compute_compressibility(P[0], T0)
        return mass_rate_total / (V_pore * rho_P * beta_P)

    # Solve ODE
    t_span = (0, tf * 86400)  # convert days to seconds
    t_eval = np.linspace(0, tf * 86400, 100)
    sol = solve_ivp(dP_dt_ode, t_span, [P0], t_eval=t_eval, method='RK45')

    expected_P_variable = sol.y[0]
    expected_time_days = sol.t / 86400
    expected_dP_variable = expected_P_variable[-1] - P0

    print(f"\nSimulation time = {tf} days")
    print(f"Expected dP (constant beta) = {expected_dP_constant:.6f} MPa")
    print(f"Expected dP (variable beta) = {expected_dP_variable:.6f} MPa")

    # Create simulation
    dat = fdata(work_dir=work_dir)

    # Create 2x2x2 grid (1 element)
    # Note: first positional arg is gridfilename, then x, y, z are keyword args
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    print(f"\nGrid: {dat.grid.number_nodes} nodes, {dat.grid.number_elems} elements")

    # Rock properties (using reasonable values)
    rock = fmacro('rock', param=(
        ('density', 2500),  # kg/m³
        ('specific_heat', 1000),  # J/kg/K
        ('porosity', phi),
    ))
    dat.add(rock)

    # Very low permeability - effectively closed (no flow between nodes)
    perm = fmacro('perm', param=(
        ('kx', 1e-25),  # m² (essentially zero)
        ('ky', 1e-25),
        ('kz', 1e-25),
    ))
    dat.add(perm)

    # Initial conditions
    pres = fmacro('pres', param=(
        ('pressure', P0),
        ('temperature', T0),
        ('saturation', 1),  # fully saturated
    ))
    dat.add(pres)

    # Mass injection using flow macro
    # rate < 0 = injection, energy < 0 = temperature in °C
    # Note: rate is applied to each node in zone 0, so use per-node rate
    flow = fmacro('flow', zone=0, param=(
        ('rate', -mass_rate_per_node),  # negative = injection (kg/s per node)
        ('energy', -T0),  # negative = temperature (°C)
        ('impedance', 0),  # fixed rate
    ))
    dat.add(flow)

    # Time control
    dat.tf = tf
    dat.dti = 0.001  # initial timestep (days)
    dat.dtmax = 0.01  # max timestep (days)

    # History output - track pressure at center node
    center_node = 1  # first node
    dat.hist.nodelist = [center_node]
    dat.hist.variables = ['pressure', 'temperature']
    dat.hist.time_interval = 0.01  # output every 0.01 days

    # Contour output
    dat.cont.variables = ['pressure', 'temperature']
    dat.cont.time_interval = 0.1

    # File settings and run
    dat.files.root = 'mass_test'
    input_file = os.path.join(work_dir, 'mass_test.dat')

    print(f"\nRunning simulation...")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Check for errors in output file
    outp_file = os.path.join(work_dir, 'mass_test.outp')
    if os.path.exists(outp_file):
        with open(outp_file, 'r') as f:
            content = f.read().lower()
            if 'error' in content:
                print("WARNING: Errors found in output file")
                # Extract error lines
                for line in content.split('\n'):
                    if 'error' in line:
                        print(f"  {line}")

    # Read history output from individual Tecplot-format files
    try:
        pres_file = os.path.join(work_dir, 'mass_test_presWAT_his.dat')
        temp_file = os.path.join(work_dir, 'mass_test_temp_his.dat')

        # Parse Tecplot-format history files
        def read_tecplot_history(filepath):
            times, values = [], []
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip header lines
                    if line.startswith(('TITLE', 'variables', 'text', 'zone')) or not line:
                        continue
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            times.append(float(parts[0]))
                            values.append(float(parts[1]))
                    except ValueError:
                        continue
            return np.array(times), np.array(values)

        time, pressure = read_tecplot_history(pres_file)
        _, temperature = read_tecplot_history(temp_file)
        print(f"Read {len(time)} history points")
    except Exception as e:
        print(f"Error reading history: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Compute results
    P_final = pressure[-1]
    dP_actual = P_final - P0

    print(f"\nResults:")
    print(f"  Final pressure = {P_final:.6f} MPa")
    print(f"  Actual dP = {dP_actual:.6f} MPa")
    print(f"  Expected dP (constant beta) = {expected_dP_constant:.6f} MPa")
    print(f"  Expected dP (variable beta) = {expected_dP_variable:.6f} MPa")
    print(f"  Ratio (actual/constant beta) = {dP_actual/expected_dP_constant:.6f}")
    print(f"  Ratio (actual/variable beta) = {dP_actual/expected_dP_variable:.6f}")

    return {
        'time': time,
        'pressure': pressure,
        'temperature': temperature,
        'expected_dP_constant': expected_dP_constant,
        'expected_dP_variable': expected_dP_variable,
        'expected_time_days': expected_time_days,
        'expected_P_variable': expected_P_variable,
        'P0': P0,
        'T0': T0,
    }


def run_heat_injection_test(work_dir='test_heat'):
    """
    Test 2: Heat injection into closed block

    Physics:
        - Closed system, no mass flow
        - Heat injection rate: Q (MW)
        - dT/dt = Q / C_total
        - C_total = V×(1-φ)×ρ_rock×c_rock + V×φ×ρ_water×c_water
    """
    print("\n" + "="*60)
    print("TEST 2: Heat Injection - Heat Capacity Verification")
    print("="*60)

    # Parameters
    V = 1.0  # m³
    phi = 0.1  # porosity

    P0 = 1.0  # MPa
    T0 = 25.0  # °C

    # Rock properties
    rho_rock = 2500  # kg/m³
    c_rock = 1000  # J/kg/K

    # Water properties at initial conditions
    rho_water = dens(P0, T0)[0][0]  # kg/m³
    c_water_MJ = compute_water_heat_capacity(P0, T0)  # MJ/kg/K
    c_water = c_water_MJ * 1e6  # J/kg/K

    print(f"\nInitial conditions:")
    print(f"  P0 = {P0} MPa")
    print(f"  T0 = {T0} °C")
    print(f"  Porosity = {phi}")
    print(f"  Rock density = {rho_rock} kg/m³")
    print(f"  Rock specific heat = {c_rock} J/kg/K")
    print(f"  Water density = {rho_water:.2f} kg/m³")
    print(f"  Water specific heat = {c_water:.2f} J/kg/K")

    # Total heat capacity (J/K)
    m_rock = V * (1 - phi) * rho_rock
    m_water = V * phi * rho_water
    C_rock = m_rock * c_rock
    C_water = m_water * c_water
    C_total = C_rock + C_water

    print(f"\nHeat capacities:")
    print(f"  Rock mass = {m_rock:.2f} kg")
    print(f"  Water mass = {m_water:.2f} kg")
    print(f"  Rock heat capacity = {C_rock:.2f} J/K = {C_rock/1e6:.6f} MJ/K")
    print(f"  Water heat capacity = {C_water:.2f} J/K = {C_water/1e6:.6f} MJ/K")
    print(f"  Total heat capacity = {C_total:.2f} J/K = {C_total/1e6:.6f} MJ/K")

    # Heat injection rate
    # NOTE: hflx macro applied to zone 0 applies to EACH of the 8 nodes
    n_nodes = 8  # 2x2x2 grid

    # Target about 1°C increase over 1 day
    # Q = C_total * dT/dt = 2.67e6 J/K * (1°C / 86400s) = 30.9 W
    Q_total_MW = 3e-5  # MW total (30 W)
    Q_per_node_MW = Q_total_MW / n_nodes  # MW per node
    Q_W = Q_total_MW * 1e6  # W total

    # Expected temperature rise rate: dT/dt = Q_total / C_total
    dT_dt_expected = Q_W / C_total  # K/s or °C/s
    dT_dt_expected_per_day = dT_dt_expected * 86400  # °C/day

    print(f"\nTotal heat injection rate = {Q_total_MW} MW = {Q_W} W")
    print(f"Rate per node = {Q_per_node_MW:.6e} MW")
    print(f"Expected dT/dt = {dT_dt_expected:.6e} °C/s")
    print(f"Expected dT/dt = {dT_dt_expected_per_day:.6f} °C/day")

    # Simulation time
    tf = 1.0  # days
    expected_dT = dT_dt_expected_per_day * tf
    print(f"\nSimulation time = {tf} days")
    print(f"Expected temperature increase = {expected_dT:.4f} °C")

    # Create simulation
    dat = fdata(work_dir=work_dir)

    # Create 2x2x2 grid
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    print(f"\nGrid: {dat.grid.number_nodes} nodes, {dat.grid.number_elems} elements")

    # Rock properties
    rock = fmacro('rock', param=(
        ('density', rho_rock),
        ('specific_heat', c_rock),
        ('porosity', phi),
    ))
    dat.add(rock)

    # Very low permeability - closed system
    perm = fmacro('perm', param=(
        ('kx', 1e-25),
        ('ky', 1e-25),
        ('kz', 1e-25),
    ))
    dat.add(perm)

    # Initial conditions
    pres = fmacro('pres', param=(
        ('pressure', P0),
        ('temperature', T0),
        ('saturation', 1),
    ))
    dat.add(pres)

    # Heat injection using fix_heating_rate() method on zone 0
    # This method ensures multiplier=0 for fixed heat flow (not temperature-dependent)
    # and uses intuitive sign convention: positive = heat INTO reservoir
    # Note: applied to zone 0, which distributes across all 8 nodes
    dat.zone[0].fix_heating_rate(Q_per_node_MW)  # MW per node, positive = heat in

    # Time control
    dat.tf = tf
    dat.dti = 0.01
    dat.dtmax = 0.5

    # History output
    center_node = 1
    dat.hist.nodelist = [center_node]
    dat.hist.variables = ['pressure', 'temperature']
    dat.hist.time_interval = 0.1  # output every 0.1 days

    # Contour output
    dat.cont.variables = ['pressure', 'temperature']
    dat.cont.time_interval = 1.0

    # File settings and run
    dat.files.root = 'heat_test'
    input_file = os.path.join(work_dir, 'heat_test.dat')

    print(f"\nRunning simulation...")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Check for errors
    outp_file = os.path.join(work_dir, 'heat_test.outp')
    if os.path.exists(outp_file):
        with open(outp_file, 'r') as f:
            content = f.read().lower()
            if 'error' in content:
                print("WARNING: Errors found in output file")
                for line in content.split('\n'):
                    if 'error' in line:
                        print(f"  {line}")

    # Read history output from individual Tecplot-format files
    try:
        pres_file = os.path.join(work_dir, 'heat_test_presWAT_his.dat')
        temp_file = os.path.join(work_dir, 'heat_test_temp_his.dat')

        # Parse Tecplot-format history files
        def read_tecplot_history(filepath):
            times, values = [], []
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(('TITLE', 'variables', 'text', 'zone')) or not line:
                        continue
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            times.append(float(parts[0]))
                            values.append(float(parts[1]))
                    except ValueError:
                        continue
            return np.array(times), np.array(values)

        time, pressure = read_tecplot_history(pres_file)
        _, temperature = read_tecplot_history(temp_file)
        print(f"Read {len(time)} history points")
    except Exception as e:
        print(f"Error reading history: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Compute results
    T_final = temperature[-1]
    dT_actual = T_final - T0
    dT_dt_actual = dT_actual / tf

    print(f"\nResults:")
    print(f"  Final temperature = {T_final:.6f} °C")
    print(f"  Actual dT = {dT_actual:.6f} °C")
    print(f"  Expected dT = {expected_dT:.6f} °C")
    print(f"  Ratio (actual/expected) = {dT_actual/expected_dT:.4f}")

    return {
        'time': time,
        'pressure': pressure,
        'temperature': temperature,
        'expected_dT_dt': dT_dt_expected_per_day,
        'P0': P0,
        'T0': T0,
    }


def create_summary_plot(mass_results, heat_results, save_path='test_single_block_results.png'):
    """Create summary plot comparing simulation results to expected values."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Mass injection - Pressure vs Time
    ax1 = axes[0, 0]
    if mass_results is not None:
        time = mass_results['time']
        pressure = mass_results['pressure']
        P0 = mass_results['P0']
        expected_dP_constant = mass_results['expected_dP_constant']
        expected_time_days = mass_results['expected_time_days']
        expected_P_variable = mass_results['expected_P_variable']

        # Linear expectation (constant compressibility)
        expected_P_constant = P0 + (expected_dP_constant / time[-1]) * np.array(time)

        ax1.plot(time, pressure, 'b-', linewidth=2, label='FEHM Simulation')
        ax1.plot(time, expected_P_constant, 'r--', linewidth=2, label='Expected (constant beta)')
        ax1.plot(expected_time_days, expected_P_variable, 'g:', linewidth=2, label='Expected (variable beta)')
        ax1.set_xlabel('Time (days)')
        ax1.set_ylabel('Pressure (MPa)')
        ax1.set_title('Mass Injection Test: Pressure Rise')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(0.5, 0.5, 'Mass test failed', ha='center', va='center', transform=ax1.transAxes)

    # Plot 2: Mass injection - Pressure error (vs variable beta expectation)
    ax2 = axes[0, 1]
    if mass_results is not None:
        time = mass_results['time']
        pressure = mass_results['pressure']
        P0 = mass_results['P0']
        expected_time_days = mass_results['expected_time_days']
        expected_P_variable = mass_results['expected_P_variable']

        # Interpolate expected variable-beta pressure to simulation times
        expected_P_interp = np.interp(time, expected_time_days, expected_P_variable)
        error_pct = (pressure - expected_P_interp) / (expected_P_interp - P0 + 1e-10) * 100

        ax2.plot(time, error_pct, 'b-', linewidth=2)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Time (days)')
        ax2.set_ylabel('Relative Error (%)')
        ax2.set_title('Mass Injection Test: Error vs Variable beta')
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'Mass test failed', ha='center', va='center', transform=ax2.transAxes)

    # Plot 3: Heat injection - Temperature vs Time
    ax3 = axes[1, 0]
    if heat_results is not None:
        time = heat_results['time']
        temperature = heat_results['temperature']
        T0 = heat_results['T0']
        dT_dt = heat_results['expected_dT_dt']

        expected_T = T0 + dT_dt * np.array(time)

        ax3.plot(time, temperature, 'b-', linewidth=2, label='Simulation')
        ax3.plot(time, expected_T, 'r--', linewidth=2, label='Expected (linear)')
        ax3.set_xlabel('Time (days)')
        ax3.set_ylabel('Temperature (°C)')
        ax3.set_title('Heat Injection Test: Temperature Rise')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Heat test failed', ha='center', va='center', transform=ax3.transAxes)

    # Plot 4: Heat injection - Temperature error
    ax4 = axes[1, 1]
    if heat_results is not None:
        time = heat_results['time']
        temperature = heat_results['temperature']
        T0 = heat_results['T0']
        dT_dt = heat_results['expected_dT_dt']

        expected_T = T0 + dT_dt * np.array(time)
        error_pct = (temperature - expected_T) / (expected_T - T0 + 1e-10) * 100

        ax4.plot(time, error_pct, 'b-', linewidth=2)
        ax4.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax4.set_xlabel('Time (days)')
        ax4.set_ylabel('Relative Error (%)')
        ax4.set_title('Heat Injection Test: Temperature Error')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Heat test failed', ha='center', va='center', transform=ax4.transAxes)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nSummary plot saved to: {save_path}")
    plt.close()


def main():
    """Run both verification tests and create summary plot."""

    print("\n" + "="*60)
    print("PyFEHM Single Block Verification Tests")
    print("="*60)

    # Get script directory for output
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Run mass injection test
    mass_work_dir = os.path.join(script_dir, 'test_mass')
    os.makedirs(mass_work_dir, exist_ok=True)
    mass_results = run_mass_injection_test(mass_work_dir)

    # Run heat injection test
    heat_work_dir = os.path.join(script_dir, 'test_heat')
    os.makedirs(heat_work_dir, exist_ok=True)
    heat_results = run_heat_injection_test(heat_work_dir)

    # Create summary plot
    plot_path = os.path.join(script_dir, 'test_single_block_results.png')
    create_summary_plot(mass_results, heat_results, plot_path)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if mass_results is not None:
        P_final = mass_results['pressure'][-1]
        P0 = mass_results['P0']
        expected_dP_constant = mass_results['expected_dP_constant']
        expected_dP_variable = mass_results['expected_dP_variable']
        actual_dP = P_final - P0
        print(f"\nMass Injection Test:")
        print(f"  Actual dP:                {actual_dP:.6f} MPa")
        print(f"  Expected dP (constant beta): {expected_dP_constant:.6f} MPa  ->  {actual_dP/expected_dP_constant*100:.2f}%")
        print(f"  Expected dP (variable beta): {expected_dP_variable:.6f} MPa  ->  {actual_dP/expected_dP_variable*100:.2f}%")
    else:
        print("\nMass Injection Test: FAILED")

    if heat_results is not None:
        T_final = heat_results['temperature'][-1]
        T0 = heat_results['T0']
        dT_dt = heat_results['expected_dT_dt']
        tf = heat_results['time'][-1]
        expected_dT = dT_dt * tf
        actual_dT = T_final - T0
        print(f"\nHeat Injection Test:")
        print(f"  Expected dT: {expected_dT:.6f} °C")
        print(f"  Actual dT:   {actual_dT:.6f} °C")
        print(f"  Agreement:   {actual_dT/expected_dT*100:.1f}%")
    else:
        print("\nHeat Injection Test: FAILED")


if __name__ == '__main__':
    main()
