"""
CO2 Injection Test for PyFEHM

Test: CO2 injection into closed single block
- CO2-only mode (iprtype=2) - simplest case that works closed
- Pressure-based injection (bc_flag=1) - fixed rate doesn't work for CO2-only
- Monitors pressure rise as CO2 accumulates

Grid: 2x2x2 nodes = 1 element of 1 m³
"""

import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt

PYFEHM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PYFEHM_ROOT)
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

from fdata import fdata, fmacro, fmodel
from fvars import dens


def clean_output_files(work_dir):
    """Remove old output files to avoid confusion."""
    for pattern in ['*.outp', '*.err', '*.chk', '*.rsto', '*_his.dat', '*.avs', '*.csv', 'nop.temp', 'fehmn.err']:
        for f in glob.glob(os.path.join(work_dir, pattern)):
            try:
                os.remove(f)
            except:
                pass


def run_co2_injection_test(work_dir='test_co2'):
    """
    Test: CO2 injection into closed block.

    Uses CO2-only mode (iprtype=2) which works in closed systems.
    Pressure-based injection (bc_flag=1) since fixed rate doesn't work for CO2-only.
    """
    print("\n" + "="*60)
    print("CO2 INJECTION TEST: Closed System Pressure Rise")
    print("="*60)

    # Parameters
    V = 1.0  # m³
    phi = 0.3  # porosity
    V_pore = V * phi

    P0 = 10.0  # MPa
    T0 = 50.0  # °C

    # CO2 properties at initial conditions
    rho_co2 = dens(P0, T0)[2][0]
    m_co2_init = V_pore * rho_co2

    print(f"\nInitial conditions:")
    print(f"  P0 = {P0} MPa, T0 = {T0} °C")
    print(f"  Porosity = {phi}, Pore volume = {V_pore} m³")
    print(f"  CO2 density = {rho_co2:.1f} kg/m³")
    print(f"  Initial CO2 mass = {m_co2_init:.1f} kg")

    # Injection parameters
    injection_pressure = P0 + 2.0  # 2 MPa above initial
    aiped = 1e-2  # impedance

    print(f"\nCO2 Injection:")
    print(f"  Injection pressure = {injection_pressure} MPa")
    print(f"  Impedance = {aiped}")

    tf = 10.0  # days
    print(f"\nSimulation time = {tf} days")

    # Setup simulation
    os.makedirs(work_dir, exist_ok=True)
    clean_output_files(work_dir)

    dat = fdata(work_dir=work_dir)
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    print(f"\nGrid: {dat.grid.number_nodes} nodes")

    # Material properties
    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', 1e-14), ('ky', 1e-14), ('kz', 1e-14))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))

    dat.nobr = True

    # CO2-only mode (works in closed systems)
    dat.carb.on(iprtype=2)
    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 4))))
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 0.0), ('co2_rich_sat', 1.0),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # CO2 injection - must use bc_flag=1 (pressure-based) for CO2-only
    # bc_flag=0 (fixed rate) doesn't work for CO2-only mode
    dat.new_zone(index=100, nodelist=[1])
    dat.add(fmacro('co2flow', zone=100, param=(
        ('rate', injection_pressure), ('energy', -T0), ('impedance', aiped), ('bc_flag', 1))))

    # Time control
    dat.tf = tf
    dat.dti = 0.001
    dat.dtmax = 0.1
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.sol['element_integration_INTG'] = -1

    # Output
    dat.hist.nodelist = [1]
    dat.hist.variables = ['pressure', 'temperature', 'saturation']
    dat.hist.time_interval = 0.1

    dat.cont.variables = ['pressure', 'temperature', 'co2s']
    dat.cont.time_interval = 1.0

    dat.files.root = 'co2_test'
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')

    input_file = os.path.join(work_dir, 'co2_test.dat')
    print(f"\nRunning simulation...")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Check for errors
    err_file = os.path.join(work_dir, 'fehmn.err')
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print(f"ERROR: {err[:500]}")
                return None

    # Read results
    results = read_history(work_dir)
    return results


def read_history(work_dir):
    """Read history files."""
    results = {}
    print("\nReading history files...")

    for filename in os.listdir(work_dir):
        if filename.endswith('_his.dat') and filename.startswith('co2_test_'):
            filepath = os.path.join(work_dir, filename)
            varname = filename.replace('co2_test_', '').replace('_his.dat', '')

            times, values = [], []
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(('TITLE', 'var', 'text', 'zone')) or not line:
                        continue
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            times.append(float(parts[0]))
                            values.append(float(parts[1]))
                    except ValueError:
                        continue

            if times:
                results[varname] = {'time': np.array(times), 'values': np.array(values)}
                print(f"  {varname}: {len(times)} points")

    return results


def create_plot(results, save_path):
    """Create results plot."""
    if not results:
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Pressure plot
    if 'presCO2' in results:
        ax = axes[0]
        data = results['presCO2']
        ax.plot(data['time'], data['values'], 'b-', linewidth=2)
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('CO2 Pressure (MPa)')
        ax.set_title('Pressure Rise in Closed System')
        ax.grid(True, alpha=0.3)

    # Temperature plot
    if 'temp' in results:
        ax = axes[1]
        data = results['temp']
        ax.plot(data['time'], data['values'], 'r-', linewidth=2)
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Temperature Change')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {save_path}")
    plt.close()


def main():
    print("\n" + "="*60)
    print("PyFEHM CO2 Injection Test")
    print("="*60)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = os.path.join(script_dir, 'test_co2')

    results = run_co2_injection_test(work_dir)

    if results:
        plot_path = os.path.join(script_dir, 'test_co2_results.png')
        create_plot(results, plot_path)

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        if 'presCO2' in results:
            P = results['presCO2']['values']
            print(f"\nCO2 Pressure:")
            print(f"  Initial: {P[0]:.3f} MPa")
            print(f"  Final:   {P[-1]:.3f} MPa")
            print(f"  Change:  {P[-1]-P[0]:.3f} MPa")

        if 'temp' in results:
            T = results['temp']['values']
            print(f"\nTemperature:")
            print(f"  Initial: {T[0]:.3f} °C")
            print(f"  Final:   {T[-1]:.3f} °C")
            print(f"  Change:  {T[-1]-T[0]:.3f} °C")
    else:
        print("\nSimulation failed. Check output files.")


if __name__ == '__main__':
    main()
