"""
CO2 Debug Tests - Process of elimination

Test 1: Static water-only for 1 timestep, then restart with CO2
Test 2: Static CO2 problem with initial saturation but NO injection
"""

import os
import sys
import glob

PYFEHM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PYFEHM_ROOT)
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

from fdata import fdata, fmacro, fmodel


def clean_output_files(work_dir):
    """Remove old output files."""
    for pattern in ['*.outp', '*.err', '*.chk', '*.rsto', '*_his.dat', '*.avs', '*.csv', 'nop.temp', 'fehmn.err', '*.ini']:
        for f in glob.glob(os.path.join(work_dir, pattern)):
            try:
                os.remove(f)
            except:
                pass


def test1_restart_approach(work_dir='test_co2_debug'):
    """
    Test 1: Water-only first, then restart with CO2
    """
    print("\n" + "="*60)
    print("TEST 1: Water-only -> Restart with CO2")
    print("="*60)

    os.makedirs(work_dir, exist_ok=True)
    clean_output_files(work_dir)

    P0, T0, phi = 10.0, 50.0, 0.3

    # --- STEP 1: Water-only for 1 timestep ---
    print("\nStep 1: Running water-only initialization...")

    dat = fdata(work_dir=work_dir)
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])

    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', 1e-14), ('ky', 1e-14), ('kz', 1e-14))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))

    # Water-only CO2 module
    dat.carb.on(iprtype=1)
    dat.nobr = True

    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 1))))
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 1.0), ('co2_rich_sat', 0.0),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # Just 1 timestep
    dat.time['max_timestep_NSTEP'] = 1
    dat.tf = 0.001
    dat.dti = 0.001

    dat.files.root = 'test1_init'
    dat.files.rsto = 'test1_init.ini'
    co2_table_path = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')
    dat.files.co2in = co2_table_path

    input_file = os.path.join(work_dir, 'test1_init.dat')
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Check if it ran
    err_file = os.path.join(work_dir, 'fehmn.err')
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED: Water-only initialization failed")
                print(f"  Error: {err[:500]}")
                return False

    # Check restart file exists
    rsto_file = os.path.join(work_dir, 'test1_init.ini')
    if not os.path.exists(rsto_file):
        print("  FAILED: No restart file created")
        return False

    print("  SUCCESS: Water-only initialization completed")

    # --- STEP 2: Restart with CO2 ---
    print("\nStep 2: Restarting with CO2 (iprtype=3)...")

    # Read the restart file
    dat.incon.read(rsto_file)

    # Switch to water+CO2 mode
    dat.carb.on(iprtype=3)

    # Add initial CO2 saturation (50/50)
    dat.delete(dat.co2fraclist)
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 0.5), ('co2_rich_sat', 0.5),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # Update co2pres for two-phase
    dat.delete(dat.co2preslist)
    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 2))))

    # Run for a few more timesteps (no injection yet)
    dat.time['max_timestep_NSTEP'] = 10
    dat.tf = 1.0
    dat.dti = 0.01

    dat.files.root = 'test1_co2'

    # Clean old files for step 2
    for f in glob.glob(os.path.join(work_dir, 'test1_co2*')):
        try:
            os.remove(f)
        except:
            pass

    input_file = os.path.join(work_dir, 'test1_co2.dat')
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Check result
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED: CO2 restart failed")
                print(f"  Error: {err[:500]}")
                return False

    print("  SUCCESS: CO2 restart completed")
    return True


def test2_static_co2(work_dir='test_co2_debug'):
    """
    Test 2a: Static CO2-only (iprtype=2) - WORKS
    Test 2b: Static water+CO2 (iprtype=3) with pressure BC
    """
    print("\n" + "="*60)
    print("TEST 2a: Static CO2-only (iprtype=2)")
    print("="*60)

    os.makedirs(work_dir, exist_ok=True)
    clean_output_files(work_dir)

    P0, T0, phi = 10.0, 50.0, 0.3

    # Test 2a: CO2-only
    dat = fdata(work_dir=work_dir)
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', 1e-14), ('ky', 1e-14), ('kz', 1e-14))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))
    dat.nobr = True
    dat.carb.on(iprtype=2)
    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 4))))
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 0.0), ('co2_rich_sat', 1.0),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))
    dat.tf = 1.0
    dat.dti = 0.01
    dat.dtmax = 0.1
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.sol['element_integration_INTG'] = -1
    dat.files.root = 'test2a'
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')

    print("\nRunning CO2-only static...")
    dat.run(os.path.join(work_dir, 'test2a.dat'), exe=FEHM_EXE, verbose=False)

    err_file = os.path.join(work_dir, 'fehmn.err')
    test2a_pass = True
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED")
                test2a_pass = False
    if test2a_pass:
        print("  PASSED")

    # Test 2b: Water+CO2 with pressure BC
    print("\n" + "="*60)
    print("TEST 2b: Static water+CO2 (iprtype=3) with pressure BC")
    print("="*60)

    clean_output_files(work_dir)
    dat = fdata(work_dir=work_dir)
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', 1e-14), ('ky', 1e-14), ('kz', 1e-14))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))
    dat.add(fmodel('rlp', index=17, param=[.05, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0]))
    dat.nobr = True

    # Water+CO2, no solubility
    dat.carb.on(iprtype=3)

    # Try phase=1 (liquid/water-dominated) instead of phase=2
    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 1))))
    # Start mostly water with small CO2
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 0.8), ('co2_rich_sat', 0.2),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # Pressure BC on one node
    dat.new_zone(index=200, nodelist=[8])
    dat.zone[200].fix_pressure(P0, T0)
    dat.add(fmacro('co2flow', zone=200, param=(
        ('rate', P0), ('energy', -T0), ('impedance', 1e-2), ('bc_flag', 1))))

    dat.tf = 1.0
    dat.dti = 0.01
    dat.dtmax = 0.1
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.sol['element_integration_INTG'] = -1
    dat.files.root = 'test2b'
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')

    print("\nRunning water+CO2 static with pressure BC...")
    dat.run(os.path.join(work_dir, 'test2b.dat'), exe=FEHM_EXE, verbose=False)

    test2b_pass = True
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED")
                test2b_pass = False
    if test2b_pass:
        print("  PASSED")

    # Test 2c: Water+CO2 WITH injection
    print("\n" + "="*60)
    print("TEST 2c: Water+CO2 (iprtype=3) WITH CO2 injection")
    print("="*60)

    clean_output_files(work_dir)
    dat = fdata(work_dir=work_dir)
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', 1e-14), ('ky', 1e-14), ('kz', 1e-14))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))
    dat.add(fmodel('rlp', index=17, param=[.05, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0]))
    dat.nobr = True

    dat.carb.on(iprtype=3)
    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 1))))
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 0.8), ('co2_rich_sat', 0.2),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # Injection zone
    dat.new_zone(index=100, nodelist=[1])
    dat.add(fmacro('co2flow', zone=100, param=(
        ('rate', P0 + 2.0), ('energy', -T0), ('impedance', 1e-2), ('bc_flag', 1))))
    # High CO2 sat at injector
    dat.add(fmacro('co2frac', zone=100, param=(('water_rich_sat', 0.2), ('co2_rich_sat', 0.8),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # Pressure BC outlet
    dat.new_zone(index=200, nodelist=[8])
    dat.zone[200].fix_pressure(P0, T0)
    dat.add(fmacro('co2flow', zone=200, param=(
        ('rate', P0), ('energy', -T0), ('impedance', 1e-2), ('bc_flag', 1))))

    dat.tf = 10.0
    dat.dti = 0.01
    dat.dtmax = 0.1
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.sol['element_integration_INTG'] = -1

    dat.hist.nodelist = [1]
    dat.hist.variables = ['pressure', 'temperature', 'saturation']
    dat.hist.time_interval = 0.1

    dat.files.root = 'test2c'
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')

    print("\nRunning water+CO2 WITH injection...")
    dat.run(os.path.join(work_dir, 'test2c.dat'), exe=FEHM_EXE, verbose=False)

    test2c_pass = True
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED")
                test2c_pass = False
    if test2c_pass:
        print("  PASSED")
        # Read results
        his_file = os.path.join(work_dir, 'test2c_satr_his.dat')
        if os.path.exists(his_file):
            with open(his_file, 'r') as f:
                lines = [l for l in f.readlines() if not l.startswith(('TITLE', 'var', 'text', 'zone')) and l.strip()]
                if len(lines) > 1:
                    first = float(lines[0].split()[1])
                    last = float(lines[-1].split()[1])
                    print(f"  Water saturation: {first:.3f} -> {last:.3f}")

    # Test 2d: CO2-only CLOSED with injection - see pressure rise
    print("\n" + "="*60)
    print("TEST 2d: CO2-only CLOSED with injection (pressure rise)")
    print("="*60)

    clean_output_files(work_dir)
    dat = fdata(work_dir=work_dir)
    dat.grid.make(gridfilename=os.path.join(work_dir, 'grid.inp'), x=[0, 1], y=[0, 1], z=[0, 1])
    dat.add(fmacro('rock', param=(('density', 2500), ('specific_heat', 1000), ('porosity', phi))))
    dat.add(fmacro('perm', param=(('kx', 1e-14), ('ky', 1e-14), ('kz', 1e-14))))
    dat.add(fmacro('cond', param=(('cond_x', 2.0), ('cond_y', 2.0), ('cond_z', 2.0))))
    dat.add(fmacro('pres', param=(('pressure', P0), ('temperature', T0), ('saturation', 1))))
    dat.nobr = True

    dat.carb.on(iprtype=2)  # CO2 only
    dat.add(fmacro('co2pres', param=(('pressure', P0), ('temperature', T0), ('phase', 4))))
    dat.add(fmacro('co2frac', param=(('water_rich_sat', 0.0), ('co2_rich_sat', 1.0),
                                      ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

    # Injection - use pressure-based (bc_flag=1) since fixed rate doesn't work for CO2-only
    # Inject at higher pressure to drive flow
    dat.new_zone(index=100, nodelist=[1])
    injection_pressure = P0 + 5.0  # 5 MPa above initial
    aiped = 1e-3  # small impedance for faster flow
    dat.add(fmacro('co2flow', zone=100, param=(
        ('rate', injection_pressure), ('energy', -T0), ('impedance', aiped), ('bc_flag', 1))))

    # NO outlet - closed system

    dat.tf = 10.0
    dat.dti = 0.001
    dat.dtmax = 0.1
    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.sol['element_integration_INTG'] = -1

    dat.hist.nodelist = [1]
    dat.hist.variables = ['pressure', 'temperature', 'saturation']
    dat.hist.time_interval = 0.1

    dat.files.root = 'test2d'
    dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')

    print("\nRunning CO2-only CLOSED with injection...")
    dat.run(os.path.join(work_dir, 'test2d.dat'), exe=FEHM_EXE, verbose=False)

    test2d_pass = True
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED")
                print(f"  Error: {err[:300]}")
                test2d_pass = False
    if test2d_pass:
        print("  PASSED")
        # Read pressure results
        his_file = os.path.join(work_dir, 'test2d_presCO2_his.dat')
        if os.path.exists(his_file):
            with open(his_file, 'r') as f:
                lines = [l for l in f.readlines() if not l.startswith(('TITLE', 'var', 'text', 'zone')) and l.strip()]
                if len(lines) > 1:
                    first = float(lines[0].split()[1])
                    last = float(lines[-1].split()[1])
                    print(f"  CO2 Pressure: {first:.3f} -> {last:.3f} MPa (change: {last-first:.3f})")

    return test2a_pass and test2b_pass and test2c_pass and test2d_pass
    dat.tf = 1.0
    dat.dti = 0.01
    dat.dtmax = 0.1

    dat.ctrl['max_newton_iterations_MAXIT'] = 100
    dat.sol['element_integration_INTG'] = -1

    dat.files.root = 'test2_static'
    co2_table_path = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')
    dat.files.co2in = co2_table_path

    input_file = os.path.join(work_dir, 'test2_static.dat')

    print("\nRunning static CO2 (no injection)...")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Check result
    err_file = os.path.join(work_dir, 'fehmn.err')
    if os.path.exists(err_file):
        with open(err_file, 'r') as f:
            err = f.read()
            if 'stopping' in err.lower() or 'nan' in err.lower():
                print("  FAILED: Static CO2 failed")
                print(f"  Error: {err[:500]}")
                return False

    print("  SUCCESS: Static CO2 completed")
    return True


def main():
    print("\n" + "="*60)
    print("CO2 DEBUG TESTS - Process of Elimination")
    print("="*60)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = os.path.join(script_dir, 'test_co2_debug')

    # Run tests
    # Skip test1 for now - PyFEHM has a bug reading CO2 restart files
    result1 = None  # test1_restart_approach(work_dir)
    result2 = test2_static_co2(work_dir)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Test 1 (restart approach): {'SKIPPED - PyFEHM restart bug' if result1 is None else ('PASS' if result1 else 'FAIL')}")
    print(f"Test 2 (static CO2, no injection): {'PASS' if result2 else 'FAIL'}")

    if not result2:
        print("\n-> Problem is with static two-phase setup (not injection)")
    elif result2:
        print("\n-> Static CO2 works! Problem may be specifically with injection")


if __name__ == '__main__':
    main()
