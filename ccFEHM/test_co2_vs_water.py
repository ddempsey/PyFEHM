"""
CO2 vs Water Injection Pressure Comparison — 1D Radial Model

Tests the thesis that CO2 injection causes lower pressure buildup than water
injection in a 1D radial (cylindrical wedge) geometry, comparing on equal-mass
and equal-pore-volume bases.

Setup:
- 1D radial wedge: R_well = 0.5 m, R_outer = 1000 m, 101 log-spaced r-nodes
- 1-degree wedge (radial=True), 1 m thick layer
- 101 x 2 x 2 = 404 nodes
- Water-saturated reservoir: P0 = 20 MPa, T0 = 60 C
- Porosity = 0.1, Permeability = 1e-13 m^2 (~100 mD)

Cases:
1. Water injection, closed outer, 0.001 kg/s (full-cylinder rate)
2. Water injection, open outer (fix_pressure), 0.001 kg/s
3. CO2 injection, closed outer, 0.001 kg/s (equal mass)
4. CO2 injection, open outer, 0.001 kg/s (equal mass)
5. CO2 injection, closed outer, equal pore volume rate
6. CO2 injection, open outer, equal pore volume rate
"""

import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt

PYFEHM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PYFEHM_ROOT)
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

from fdata import fdata, fmacro, fmodel, fzone
from fpost import fcontour, fhistory

# ---- Physical constants ----
R_WELL = 0.5       # wellbore radius (m)
R_OUTER = 1000.0   # outer boundary radius (m)
P0 = 20.0          # initial pressure (MPa)
T0 = 60.0          # temperature (C)
PHI = 0.1          # porosity
K_PERM = 1e-13     # permeability (m^2), ~100 mD
RHO_ROCK = 2500.0
C_ROCK = 1000.0
K_COND = 2.5       # thermal conductivity (W/m/K)

Q_WATER = 0.001    # water injection mass rate, full cylinder (kg/s)

# Grid
N_X = 101          # radial nodes (log-spaced)

# Time control
TF = 10.0          # final time (days)
DTI = 0.001        # initial timestep (days)
DTMAX = 0.1        # max timestep (days)

# Output times for contour snapshots
OUTPUT_TIMES = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
HIST_INTERVAL = 0.01  # history output interval (days)


def clean_output_files(work_dir):
    """Remove old output files."""
    for pattern in ['*.outp', '*.err', '*.chk', '*.rsto', '*_his.dat',
                    '*.avs', '*.csv', 'nop.temp', 'fehmn.err', '*.his', '*.ini',
                    '*.avs_log']:
        for f in glob.glob(os.path.join(work_dir, pattern)):
            try:
                os.remove(f)
            except:
                pass


def get_fluid_densities():
    """Get water and CO2 densities at reservoir conditions from FEHM EOS."""
    from fvars import dens
    rho_l, rho_v, rho_co2 = dens(P0, T0)
    rho_water = float(rho_l[0])
    rho_co2_val = float(rho_co2[0])
    print(f"Fluid densities at P={P0} MPa, T={T0} C:")
    print(f"  Water:  {rho_water:.1f} kg/m^3")
    print(f"  CO2:    {rho_co2_val:.1f} kg/m^3")
    print(f"  Ratio:  {rho_co2_val / rho_water:.4f}")
    return rho_water, rho_co2_val


def make_grid(dat, work_dir):
    """Create 1D radial wedge grid: 101 log-spaced r-nodes, 1-degree wedge, 1m thick."""
    x_coords = list(np.logspace(np.log10(R_WELL), np.log10(R_OUTER), N_X))
    dat.grid.make(
        gridfilename=os.path.join(work_dir, 'grid.inp'),
        x=x_coords,
        y=[0, 1],
        z=[0, 1],
        radial=True,
    )
    dat._add_boundary_zones()
    return x_coords


def add_common_properties(dat):
    """Add rock, permeability, conductivity macros."""
    dat.add(fmacro('rock', param=(
        ('density', RHO_ROCK), ('specific_heat', C_ROCK), ('porosity', PHI))))
    dat.add(fmacro('perm', param=(
        ('kx', K_PERM), ('ky', K_PERM), ('kz', K_PERM))))
    dat.add(fmacro('cond', param=(
        ('cond_x', K_COND), ('cond_y', K_COND), ('cond_z', K_COND))))


def setup_time_control(dat):
    """Configure time stepping."""
    dat.tf = TF
    dat.dti = DTI
    dat.dtmax = DTMAX
    dat.dtmin = 1e-10


def setup_history(dat, inj_nodes, mid_node, outlet_nodes):
    """Configure history output at injection, midpoint, and outlet."""
    monitor = list(set([inj_nodes[0], mid_node, outlet_nodes[0]]))
    dat.hist.nodelist = monitor
    dat.hist.variables = ['pressure', 'temperature']
    dat.hist.time_interval = HIST_INTERVAL


def setup_contour(dat, variables=None):
    """Configure contour output."""
    if variables is None:
        variables = ['pressure', 'temperature']
    dat.cont.variables = variables
    dat.cont.format = 'surf'
    dat.output_times = OUTPUT_TIMES


def get_injection_zone_nodes(dat):
    """Get XMIN zone nodes for injection (wellbore face)."""
    return list(dat.zone['XMIN'].nodelist)


def get_outlet_zone_nodes(dat):
    """Get XMAX zone nodes for outlet (outer boundary)."""
    return list(dat.zone['XMAX'].nodelist)


def get_midpoint_node(dat):
    """Get a node near the geometric midpoint of the radial domain."""
    r_mid = np.sqrt(R_WELL * R_OUTER)  # geometric mean for log-spaced grid
    best_node = None
    best_dist = float('inf')
    for n in dat.grid.nodelist:
        dist = abs(n.position[0] - r_mid)
        if dist < best_dist:
            best_dist = dist
            best_node = n.index
    return best_node


def check_simulation(work_dir, case_name):
    """Check if simulation completed successfully."""
    err_file = os.path.join(work_dir, 'fehmn.err')
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower():
                print(f"  [{case_name}] FAILED: {err[:300]}")
                return False
    print(f"  [{case_name}] Completed successfully")
    return True


def run_water_case(work_dir, case_name, root, Q_full, closed=True):
    """
    Run water injection case (no CO2 module).

    Water is injected via the flow macro at fixed mass rate on XMIN (wellbore).
    Q_full is the full-cylinder rate; actual rate applied is Q_full/360 for wedge.
    Outer boundary is either closed or held at P0 via fix_pressure.
    """
    print(f"\n--- {case_name} ---")
    os.makedirs(work_dir, exist_ok=True)
    clean_output_files(work_dir)

    dat = fdata(work_dir=work_dir)
    x_coords = make_grid(dat, work_dir)
    add_common_properties(dat)

    # Initial conditions: water-saturated at P0, T0
    dat.add(fmacro('pres', param=(
        ('pressure', P0), ('temperature', T0), ('saturation', 1))))

    # Injection at XMIN via flow macro: fixed mass rate (wedge fraction)
    inj_nodes = get_injection_zone_nodes(dat)
    n_inj = len(inj_nodes)
    Q_wedge = Q_full / 360.0
    rate_per_node = -Q_wedge / n_inj  # negative = injection
    dat.add(fmacro('flow', zone='XMIN', param=(
        ('rate', rate_per_node), ('energy', -T0), ('impedance', 0))))

    # Outer boundary
    if not closed:
        dat.zone['XMAX'].fix_pressure(P0, T=T0)

    # Time, history, contour
    setup_time_control(dat)
    mid_node = get_midpoint_node(dat)
    outlet_nodes = get_outlet_zone_nodes(dat)
    setup_history(dat, inj_nodes, mid_node, outlet_nodes)
    setup_contour(dat)

    dat.files.root = root
    input_file = os.path.join(work_dir, f'{root}.dat')

    print(f"  Full-cylinder rate: {Q_full} kg/s")
    print(f"  Wedge rate: {Q_wedge:.6e} kg/s ({rate_per_node:.6e} kg/s per node, {n_inj} nodes)")
    print(f"  Outer BC: {'closed' if closed else 'open (fix_pressure)'}")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    return check_simulation(work_dir, case_name)


def run_co2_case(work_dir, case_name, root, Q_full, closed=True):
    """
    Run CO2 injection into water-saturated reservoir (iprtype=3).

    CO2 is injected via co2flow bc_flag=6 (constant free-phase CO2 mass rate)
    on XMIN (wellbore). Q_full is the full-cylinder rate; actual rate applied
    is Q_full/360 for wedge.
    Outer boundary is either closed or held at P0 via fix_pressure + co2flow.
    """
    print(f"\n--- {case_name} ---")
    os.makedirs(work_dir, exist_ok=True)
    clean_output_files(work_dir)

    dat = fdata(work_dir=work_dir)
    x_coords = make_grid(dat, work_dir)
    add_common_properties(dat)

    # Initial conditions
    dat.add(fmacro('pres', param=(
        ('pressure', P0), ('temperature', T0), ('saturation', 1))))

    # Relative permeability for two-phase CO2-water
    dat.add(fmodel('rlp', index=17, param=[0.05, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0]))

    dat.nobr = True
    dat.carb.on(iprtype=3)

    # Global CO2 state: water-dominated
    dat.add(fmacro('co2pres', param=(
        ('pressure', P0), ('temperature', T0), ('phase', 1))))
    dat.add(fmacro('co2frac', param=(
        ('water_rich_sat', 1.0), ('co2_rich_sat', 0.0),
        ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # LHS injection zone: small initial CO2 saturation to enable injection
    dat.add(fmacro('co2frac', zone='XMIN', param=(
        ('water_rich_sat', 0.8), ('co2_rich_sat', 0.2),
        ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # CO2 injection via co2flow bc_flag=6 (constant free-phase CO2 mass rate)
    inj_nodes = get_injection_zone_nodes(dat)
    n_inj = len(inj_nodes)
    Q_wedge = Q_full / 360.0
    rate_per_node = -Q_wedge / n_inj  # negative = injection
    dat.add(fmacro('co2flow', zone='XMIN', param=(
        ('rate', rate_per_node), ('energy', -T0), ('impedance', 0), ('bc_flag', 6))))

    # Outer boundary
    if not closed:
        dat.zone['XMAX'].fix_pressure(P0, T=T0)
        dat.add(fmacro('co2flow', zone='XMAX', param=(
            ('rate', P0), ('energy', -T0), ('impedance', 1e-2), ('bc_flag', 1))))

    # Solver settings for CO2 stability
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.ctrl['number_orthogonalizations_NORTH'] = 200
    dat.ctrl['max_solver_iterations_MAXSOLVE'] = 200
    dat.ctrl['timestep_multiplier_AIAA'] = 1.3
    dat.sol['element_integration_INTG'] = -1

    # Time, history, contour
    setup_time_control(dat)
    mid_node = get_midpoint_node(dat)
    outlet_nodes = get_outlet_zone_nodes(dat)
    setup_history(dat, inj_nodes, mid_node, outlet_nodes)
    dat.hist.variables = ['pressure', 'temperature', 'saturation']
    setup_contour(dat, variables=['pressure', 'temperature', 'co2s'])

    dat.files.root = root
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')
    input_file = os.path.join(work_dir, f'{root}.dat')

    print(f"  Full-cylinder rate: {Q_full:.6f} kg/s")
    print(f"  Wedge rate: {Q_wedge:.6e} kg/s ({rate_per_node:.6e} kg/s per node, {n_inj} nodes)")
    print(f"  Outer BC: {'closed' if closed else 'open (fix_pressure + co2flow)'}")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    return check_simulation(work_dir, case_name)


def read_node_coords(work_dir):
    """Read node x-coordinates (radial distance) from grid.inp."""
    grid_file = os.path.join(work_dir, 'grid.inp')
    node_x = {}  # node_number -> x_coordinate
    with open(grid_file, 'r') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines) and not lines[i].strip().startswith('coor'):
        i += 1
    i += 1  # skip 'coor' line
    if i < len(lines):
        n_nodes = int(lines[i].strip())
        i += 1
        for _ in range(n_nodes):
            if i >= len(lines):
                break
            parts = lines[i].strip().split()
            if len(parts) >= 2:
                node_x[int(parts[0])] = float(parts[1])
            i += 1
    return node_x


def read_results(work_dir, root):
    """Read all output using fpost. Returns dict with profiles, sat_profiles, history."""
    cont = fcontour(os.path.join(work_dir, f'{root}*_sca_node.csv'))
    node_x = read_node_coords(work_dir)

    # Build x-coordinate array matching contour node ordering (0-indexed)
    # cont[t]['n'] gives node numbers; use node_x to map to radial distance
    sample_t = cont.times[0]
    node_nums = cont[sample_t]['n']
    x_all = np.array([node_x[int(n)] for n in node_nums])

    # Build pressure profiles: {time: (r_array, P_array)}
    profiles = {}
    for t in cont.times:
        if t <= 0:
            continue
        P_all = cont[t]['P']
        # Average over y,z at each unique x (radius)
        r_unique = np.unique(x_all)
        P_avg = np.array([np.mean(P_all[x_all == r]) for r in r_unique])
        profiles[t] = (r_unique, P_avg)

    # Build CO2 saturation profiles (CO2 cases only)
    sat_profiles = {}
    if 'co2_liquid' in cont.variables:
        for t in cont.times:
            if t <= 0:
                continue
            sco2 = cont[t]['co2_liquid']
            r_unique = np.unique(x_all)
            sco2_avg = np.array([np.mean(sco2[x_all == r]) for r in r_unique])
            sat_profiles[t] = (r_unique, sco2_avg)

    # History: find pressure history file and extract injection node data
    hist_data = None
    for suffix in ['presWAT', 'presCAP', 'presCO2']:
        path = os.path.join(work_dir, f'{root}_{suffix}_his.dat')
        if os.path.exists(path):
            hist = fhistory(path)
            inj_node = min(hist.nodes)  # smallest node = XMIN = wellbore
            var_key = hist.variables[0]
            hist_data = (hist.times, hist[var_key][inj_node])
            break

    return {'profiles': profiles, 'sat_profiles': sat_profiles, 'history': hist_data}


def compute_integrated_delta_P(profiles, P0):
    """
    Compute radially-weighted integrated pressure perturbation vs time.

    integral of (P(r,t) - P0) * 2*pi*r dr over the radial domain.
    """
    times = sorted(profiles.keys())
    integrals = []
    for t in times:
        r, P = profiles[t]
        integral = np.trapezoid((P - P0) * 2 * np.pi * r, r)
        integrals.append(integral)
    return np.array(times), np.array(integrals)


def create_plots(results, save_path):
    """
    Create 4x2 comparison plot.

    Row 1: P(r) profiles at t=1,5,10 days
    Row 2: P(t) at injection well
    Row 3: Integrated delta-P vs time
    Row 4: CO2 saturation S_co2(r) at t=1,5,10 days
    """
    fig, axes = plt.subplots(4, 2, figsize=(14, 18))

    plot_times = [1.0, 5.0, 10.0]  # days for profile plots

    colors = {
        'water': '#1f77b4',
        'co2_equal_mass': '#d62728',
        'co2_equal_vol': '#2ca02c',
    }
    linestyles = {
        'water': '-',
        'co2_equal_mass': '--',
        'co2_equal_vol': ':',
    }

    for col, bc_type in enumerate(['closed', 'open']):
        # ---- Row 1: Pressure profiles P(r) ----
        ax = axes[0, col]

        for case_key, label_prefix, color, ls in [
            (f'water_{bc_type}', 'Water', colors['water'], linestyles['water']),
            (f'co2_equal_mass_{bc_type}', 'CO2 (= mass)', colors['co2_equal_mass'], linestyles['co2_equal_mass']),
            (f'co2_equal_vol_{bc_type}', 'CO2 (= vol)', colors['co2_equal_vol'], linestyles['co2_equal_vol']),
        ]:
            if case_key not in results or 'profiles' not in results[case_key]:
                continue
            profiles = results[case_key]['profiles']

            for i, t_target in enumerate(plot_times):
                available_times = sorted(profiles.keys())
                if not available_times:
                    continue
                t_closest = min(available_times, key=lambda t: abs(t - t_target))
                if abs(t_closest - t_target) > 0.5:
                    continue
                r, P = profiles[t_closest]
                alpha = 0.4 + 0.6 * (i / (len(plot_times) - 1))
                label = f'{label_prefix}, t={t_closest:.0f}d' if i == len(plot_times) - 1 else None
                ax.plot(r, P, color=color, linestyle=ls, alpha=alpha, linewidth=1.5,
                        label=label)

        ax.axhline(y=P0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
        ax.set_xscale('log')
        ax.set_xlabel('Radial distance (m)')
        ax.set_ylabel('Pressure (MPa)')
        ax.set_title(f'Pressure Profiles ({bc_type.upper()} outer)\n'
                     f'Increasing opacity: t = {", ".join(str(int(t)) for t in plot_times)} days')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # ---- Row 2: P(t) at injection point ----
        ax = axes[1, col]

        for case_key, label, color, ls in [
            (f'water_{bc_type}', 'Water', colors['water'], linestyles['water']),
            (f'co2_equal_mass_{bc_type}', 'CO2 (= mass)', colors['co2_equal_mass'], linestyles['co2_equal_mass']),
            (f'co2_equal_vol_{bc_type}', 'CO2 (= vol)', colors['co2_equal_vol'], linestyles['co2_equal_vol']),
        ]:
            if case_key not in results or 'history' not in results[case_key]:
                continue
            hist = results[case_key]['history']
            if hist is None:
                continue
            t, p = hist
            ax.plot(t, p, color=color, linestyle=ls, linewidth=1.5, label=label)

        ax.axhline(y=P0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Injection Pressure (MPa)')
        ax.set_title(f'Pressure at Injection Well ({bc_type.upper()} outer)')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # ---- Row 3: Integrated delta-P vs time ----
        ax = axes[2, col]

        for case_key, label, color, ls in [
            (f'water_{bc_type}', 'Water', colors['water'], linestyles['water']),
            (f'co2_equal_mass_{bc_type}', 'CO2 (= mass)', colors['co2_equal_mass'], linestyles['co2_equal_mass']),
            (f'co2_equal_vol_{bc_type}', 'CO2 (= vol)', colors['co2_equal_vol'], linestyles['co2_equal_vol']),
        ]:
            if case_key not in results or 'profiles' not in results[case_key]:
                continue
            profiles = results[case_key]['profiles']
            if not profiles:
                continue
            t_int, dp_int = compute_integrated_delta_P(profiles, P0)
            ax.plot(t_int, dp_int, color=color, linestyle=ls, linewidth=1.5, label=label)

        ax.axhline(y=0, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
        ax.set_xlabel('Time (days)')
        ax.set_ylabel(r'$\int (P - P_0) \, 2\pi r \, dr$ (MPa$\cdot$m$^2$)')
        ax.set_title(f'Radial Integrated Pressure Perturbation ({bc_type.upper()} outer)')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # ---- Row 4: CO2 saturation profiles ----
        ax = axes[3, col]

        for case_key, label_prefix, color, ls in [
            (f'co2_equal_mass_{bc_type}', 'CO2 (= mass)', colors['co2_equal_mass'], linestyles['co2_equal_mass']),
            (f'co2_equal_vol_{bc_type}', 'CO2 (= vol)', colors['co2_equal_vol'], linestyles['co2_equal_vol']),
        ]:
            if case_key not in results or 'sat_profiles' not in results[case_key]:
                continue
            sat_profiles = results[case_key]['sat_profiles']
            if not sat_profiles:
                continue

            for i, t_target in enumerate(plot_times):
                available_times = sorted(sat_profiles.keys())
                if not available_times:
                    continue
                t_closest = min(available_times, key=lambda t: abs(t - t_target))
                if abs(t_closest - t_target) > 0.5:
                    continue
                r, sco2 = sat_profiles[t_closest]
                alpha = 0.4 + 0.6 * (i / (len(plot_times) - 1))
                label = f'{label_prefix}, t={t_closest:.0f}d' if i == len(plot_times) - 1 else None
                ax.plot(r, sco2, color=color, linestyle=ls, alpha=alpha, linewidth=1.5,
                        label=label)

        ax.set_xscale('log')
        ax.set_xlabel('Radial distance (m)')
        ax.set_ylabel('CO2 Saturation')
        ax.set_title(f'CO2 Saturation Profiles ({bc_type.upper()} outer)\n'
                     f'Increasing opacity: t = {", ".join(str(int(t)) for t in plot_times)} days')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {save_path}")
    plt.close()


def main():
    print("=" * 70)
    print("CO2 vs Water Injection Pressure Comparison (1D Radial)")
    print("=" * 70)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get fluid densities
    rho_water, rho_co2 = get_fluid_densities()

    # Equal-volume injection rate (full cylinder)
    Q_co2_equal_vol = Q_WATER * (rho_co2 / rho_water)
    print(f"\nFull-cylinder injection rates:")
    print(f"  Water:           {Q_WATER:.6f} kg/s")
    print(f"  CO2 equal mass:  {Q_WATER:.6f} kg/s")
    print(f"  CO2 equal vol:   {Q_co2_equal_vol:.6f} kg/s")
    print(f"\nWedge (1/360) rates applied to FEHM:")
    print(f"  Water:           {Q_WATER/360:.6e} kg/s")
    print(f"  CO2 equal mass:  {Q_WATER/360:.6e} kg/s")
    print(f"  CO2 equal vol:   {Q_co2_equal_vol/360:.6e} kg/s")

    # Case definitions
    cases = {
        'water_closed': {
            'runner': run_water_case,
            'dir': os.path.join(script_dir, 'test_co2_vs_water_wc'),
            'name': 'Case 1: Water, Closed',
            'root': 'water_closed',
            'Q': Q_WATER,
            'closed': True,
        },
        'water_open': {
            'runner': run_water_case,
            'dir': os.path.join(script_dir, 'test_co2_vs_water_wo'),
            'name': 'Case 2: Water, Open',
            'root': 'water_open',
            'Q': Q_WATER,
            'closed': False,
        },
        'co2_equal_mass_closed': {
            'runner': run_co2_case,
            'dir': os.path.join(script_dir, 'test_co2_vs_water_cc'),
            'name': 'Case 3: CO2 Equal Mass, Closed',
            'root': 'co2_em_closed',
            'Q': Q_WATER,
            'closed': True,
        },
        'co2_equal_mass_open': {
            'runner': run_co2_case,
            'dir': os.path.join(script_dir, 'test_co2_vs_water_co'),
            'name': 'Case 4: CO2 Equal Mass, Open',
            'root': 'co2_em_open',
            'Q': Q_WATER,
            'closed': False,
        },
        'co2_equal_vol_closed': {
            'runner': run_co2_case,
            'dir': os.path.join(script_dir, 'test_co2_vs_water_vc'),
            'name': 'Case 5: CO2 Equal Vol, Closed',
            'root': 'co2_ev_closed',
            'Q': Q_co2_equal_vol,
            'closed': True,
        },
        'co2_equal_vol_open': {
            'runner': run_co2_case,
            'dir': os.path.join(script_dir, 'test_co2_vs_water_vo'),
            'name': 'Case 6: CO2 Equal Vol, Open',
            'root': 'co2_ev_open',
            'Q': Q_co2_equal_vol,
            'closed': False,
        },
    }

    # Run all cases
    results = {}
    for key, cfg in cases.items():
        success = cfg['runner'](
            cfg['dir'], cfg['name'], cfg['root'], cfg['Q'], closed=cfg['closed'])

        results[key] = {'success': success}

        if success:
            res = read_results(cfg['dir'], cfg['root'])
            results[key].update(res)

            n_profiles = len(res['profiles'])
            n_sat = len(res['sat_profiles'])
            print(f"  Read {n_profiles} pressure profiles, {n_sat} CO2 saturation profiles")
            if res['history'] is not None:
                t, p = res['history']
                print(f"  Injection pressure: {p[0]:.2f} -> {p[-1]:.2f} MPa")
        else:
            results[key]['profiles'] = {}
            results[key]['sat_profiles'] = {}
            results[key]['history'] = None

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Case':<40} {'Status':<10} {'P_inj final (MPa)':<20}")
    print("-" * 70)
    for key, cfg in cases.items():
        r = results[key]
        status = 'OK' if r['success'] else 'FAIL'
        if r['history'] is not None:
            _, p = r['history']
            p_final = f"{p[-1]:.3f}"
        else:
            p_final = "N/A"
        print(f"{cfg['name']:<40} {status:<10} {p_final:<20}")

    # Create plots
    plot_path = os.path.join(script_dir, 'test_co2_vs_water_results.png')
    create_plots(results, plot_path)


if __name__ == '__main__':
    main()
