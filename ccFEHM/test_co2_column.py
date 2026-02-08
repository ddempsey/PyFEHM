"""
CO2 Column Diffusion Test for PyFEHM

Test: CO2 diffusion in a vertical column
- 3 blocks stacked vertically (z = 0 to 3 m)
- Top block: CO2-saturated
- Middle and bottom blocks: water
- Gravity enabled
- Goal: observe dissolved CO2 diffusing downward

Physics: CO2 dissolves at the CO2-water interface,
then diffuses downward through the water column.
"""

import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt

PYFEHM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PYFEHM_ROOT)
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

from fdata import fdata, fmacro, fmodel, frlpm


def clean_output_files(work_dir):
    """Remove old output files to avoid confusion."""
    for pattern in ['*.outp', '*.err', '*.chk', '*.rsto', '*_his.dat',
                    '*.avs', '*.csv', 'nop.temp', 'fehmn.err', '*.his']:
        for f in glob.glob(os.path.join(work_dir, pattern)):
            try:
                os.remove(f)
            except:
                pass


def run_co2_column_test(work_dir='test_co2_column'):
    """
    Test: CO2 diffusion in vertical column.

    Setup:
    - 3 vertical blocks (z = 0, 1, 2, 3 m)
    - Top block (z=2-3): CO2
    - Middle/bottom blocks (z=0-2): water
    - Pressure BC at bottom to stabilize numerics
    - Gravity enabled for realistic density effects
    """
    print("\n" + "="*60)
    print("CO2 COLUMN DIFFUSION TEST")
    print("="*60)

    # Parameters
    P0 = 10.0  # MPa - reservoir pressure
    T0 = 50.0  # °C - temperature
    phi = 0.3  # porosity
    k = 1e-14  # m² - permeability

    # Diffusion coefficient for CO2 in water
    D_co2 = 2e-9  # m²/s typical value

    print(f"\nParameters:")
    print(f"  P0 = {P0} MPa, T0 = {T0} °C")
    print(f"  Porosity = {phi}")
    print(f"  Permeability = {k} m²")
    print(f"  CO2 diffusivity = {D_co2} m²/s")

    # Simulation time - diffusion is slow
    # Characteristic time: L²/D = (1m)²/(2e-9 m²/s) = 5e8 s ≈ 5787 days
    # Run for 1000 days to see meaningful diffusion
    tf = 1000.0  # days
    print(f"\nSimulation time = {tf} days")

    # Setup
    os.makedirs(work_dir, exist_ok=True)
    clean_output_files(work_dir)

    dat = fdata(work_dir=work_dir)

    # Grid: 2x2x4 nodes = 3 vertical elements
    # z coordinates: 0, 1, 2, 3 m (bottom to top)
    dat.grid.make(
        gridfilename=os.path.join(work_dir, 'grid.inp'),
        x=[0, 1],
        y=[0, 1],
        z=[0, 1, 2, 3]
    )
    print(f"\nGrid: {dat.grid.number_nodes} nodes, 3 vertical blocks")

    # Identify node layers by z-coordinate
    z_coords = np.array([n.position[2] for n in dat.grid.nodelist])
    bottom_nodes = [n.index for n in dat.grid.nodelist if n.position[2] == 0]
    top_nodes = [n.index for n in dat.grid.nodelist if n.position[2] == 3]
    water_nodes = [n.index for n in dat.grid.nodelist if n.position[2] < 2.5]
    co2_nodes = [n.index for n in dat.grid.nodelist if n.position[2] > 2.5]

    print(f"  Bottom nodes (z=0): {bottom_nodes}")
    print(f"  Top nodes (z=3): {top_nodes}")
    print(f"  Water region nodes: {water_nodes}")
    print(f"  CO2 region nodes: {co2_nodes}")

    # Material properties - apply to all nodes
    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', k), ('ky', k), ('kz', k))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))

    # Initial P,T for water phase
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))

    # Gravity direction: 3 = z-axis (default), negative z is down
    dat.ctrl['gravity_direction_AGRAV'] = 3

    # Disable boiling
    dat.nobr = True

    # Relative permeability model - required for two-phase CO2-water flow
    # Model index 17: linear relperm for CO2 systems
    # params: [Slr, Sgr, alpha_w, alpha_g, ...]
    rlp = fmodel('rlp', index=17, param=[0.05, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0])
    dat.add(rlp)

    # CO2 module with dissolution (iprtype=4)
    dat.carb.on(iprtype=4)

    # CO2 diffusion - enables molecular diffusion in liquid phase
    # Parameters: diffusion (m²/s), tortuosity (dimensionless, typically ~0.5-0.7)
    dat.add(fmacro('co2diff', param=(('diffusion', D_co2), ('tortuosity', 0.5))))

    # Initial CO2 conditions - water region (100% water)
    dat.new_zone(index=10, nodelist=water_nodes)
    dat.add(fmacro('co2pres', zone=10, param=(('pressure', P0), ('temperature', T0), ('phase', 1))))
    dat.add(fmacro('co2frac', zone=10, param=(
        ('water_rich_sat', 1.0),      # 100% water saturation
        ('co2_rich_sat', 0.0),        # 0% CO2 saturation
        ('co2_mass_frac', 0.0),       # no dissolved CO2
        ('init_salt_conc', 0.0),
        ('override_flag', 1)
    )))

    # Initial CO2 conditions - CO2 region (80% CO2, 20% water for numerical stability)
    dat.new_zone(index=20, nodelist=co2_nodes)
    dat.add(fmacro('co2pres', zone=20, param=(('pressure', P0), ('temperature', T0), ('phase', 4))))
    dat.add(fmacro('co2frac', zone=20, param=(
        ('water_rich_sat', 0.2),      # 20% water saturation (for stability)
        ('co2_rich_sat', 0.8),        # 80% CO2 saturation
        ('co2_mass_frac', 0.0),       # dissolved CO2 fraction (in water phase)
        ('init_salt_conc', 0.0),
        ('override_flag', 1)
    )))

    # Pressure BC at bottom to stabilize (required for water+CO2 modes)
    dat.new_zone(index=100, nodelist=bottom_nodes)
    dat.zone[100].fix_pressure(P0, T0)

    # Time control
    dat.tf = tf
    dat.dti = 1e-4  # smaller initial timestep
    dat.dtmax = 1.0

    # Solver parameters for stability
    dat.ctrl['min_timestep_DAYMIN'] = 1e-10
    dat.ctrl['max_timestep_DAYMAX'] = 10.0
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.ctrl['max_multiply_iterations_IAMM'] = 100
    dat.ctrl['number_orthogonalizations_NORTH'] = 200
    dat.ctrl['max_solver_iterations_MAXSOLVE'] = 200
    dat.ctrl['timestep_multiplier_AIAA'] = 1.3
    dat.sol['element_integration_INTG'] = -1

    # Iteration tolerances
    dat.iter['stop_criteria_NRmult_G3'] = 0.001
    dat.iter['machine_tolerance_TMCH'] = -0.001

    # History output - monitor a node in each layer
    # Pick one node from each z-level for monitoring
    monitor_nodes = []
    for z_val in [0, 1, 2, 3]:
        for n in dat.grid.nodelist:
            if abs(n.position[2] - z_val) < 0.1:
                monitor_nodes.append(n.index)
                break

    print(f"  Monitor nodes: {monitor_nodes}")

    dat.hist.nodelist = monitor_nodes
    dat.hist.variables = ['pressure', 'temperature', 'saturation', 'co2m']  # co2m = dissolved CO2 mass fraction
    dat.hist.time_interval = 10.0

    # Contour output
    dat.cont.variables = ['pressure', 'temperature', 'co2s', 'co2m']  # co2s=saturation, co2m=dissolved
    dat.cont.time_interval = 100.0

    # Files
    dat.files.root = 'co2_column'
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')

    # Run
    input_file = os.path.join(work_dir, 'co2_column.dat')
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

    # Check output file for issues
    outp_file = os.path.join(work_dir, 'co2_column.outp')
    if os.path.exists(outp_file):
        with open(outp_file, 'r') as f:
            outp = f.read()
            if 'singular matrix' in outp.lower():
                print("WARNING: Singular matrix detected")
            if 'error' in outp.lower():
                # Find error lines
                for line in outp.split('\n'):
                    if 'error' in line.lower():
                        print(f"  {line.strip()}")

    results = read_history(work_dir)
    return results


def read_history(work_dir):
    """Read history files."""
    results = {}
    print("\nReading history files...")

    for filename in os.listdir(work_dir):
        if filename.endswith('_his.dat') and filename.startswith('co2_column_'):
            filepath = os.path.join(work_dir, filename)
            varname = filename.replace('co2_column_', '').replace('_his.dat', '')

            times, values = [], []
            node_data = {}

            with open(filepath, 'r') as f:
                lines = f.readlines()

            # Parse header to get node columns
            for i, line in enumerate(lines):
                if line.strip().startswith('zone'):
                    # Next line has data
                    pass
                elif line.strip() and not line.startswith(('TITLE', 'var', 'text', 'zone')):
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            t = float(parts[0])
                            vals = [float(p) for p in parts[1:]]
                            times.append(t)
                            values.append(vals)
                    except ValueError:
                        continue

            if times:
                results[varname] = {
                    'time': np.array(times),
                    'values': np.array(values)
                }
                print(f"  {varname}: {len(times)} time points, {len(values[0]) if values else 0} nodes")

    return results


def create_plot(results, save_path):
    """Create results plot."""
    if not results:
        print("No results to plot")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Pressure
    if 'presCO2' in results or 'presWAT' in results:
        ax = axes[0, 0]
        key = 'presCO2' if 'presCO2' in results else 'presWAT'
        data = results[key]
        for i in range(data['values'].shape[1]):
            ax.plot(data['time'], data['values'][:, i], label=f'Node {i+1}')
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Pressure (MPa)')
        ax.set_title('Pressure vs Time')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # Temperature
    if 'temp' in results:
        ax = axes[0, 1]
        data = results['temp']
        for i in range(data['values'].shape[1]):
            ax.plot(data['time'], data['values'][:, i], label=f'Node {i+1}')
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Temperature vs Time')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # CO2 saturation
    if 'satr' in results:
        ax = axes[1, 0]
        data = results['satr']
        for i in range(data['values'].shape[1]):
            ax.plot(data['time'], data['values'][:, i], label=f'Node {i+1}')
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('CO2 Saturation')
        ax.set_title('CO2 Saturation vs Time')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # Total CO2 mass (co2mt) - shows diffusion better
    if 'co2mt' in results:
        ax = axes[1, 1]
        data = results['co2mt']
        for i in range(data['values'].shape[1]):
            ax.plot(data['time'], data['values'][:, i], label=f'Node {i+1}')
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Total CO2 Mass (kg)')
        ax.set_title('CO2 Mass vs Time (diffusion)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {save_path}")
    plt.close()


def main():
    print("\n" + "="*60)
    print("PyFEHM CO2 Column Diffusion Test")
    print("="*60)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = os.path.join(script_dir, 'test_co2_column')

    results = run_co2_column_test(work_dir)

    if results:
        plot_path = os.path.join(script_dir, 'test_co2_column_results.png')
        create_plot(results, plot_path)

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        for key in results:
            data = results[key]
            print(f"\n{key}:")
            if len(data['values'].shape) > 1:
                for i in range(min(4, data['values'].shape[1])):
                    print(f"  Node {i+1}: {data['values'][0, i]:.4f} -> {data['values'][-1, i]:.4f}")
            else:
                print(f"  {data['values'][0]:.4f} -> {data['values'][-1]:.4f}")
    else:
        print("\nSimulation failed. Check output files.")


if __name__ == '__main__':
    main()
