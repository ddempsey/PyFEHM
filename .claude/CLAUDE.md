# PyFEHM Project Instructions

## FEHM Executable

The FEHM executable is located at:
```
bin/fehm.exe
```

When running simulations with PyFEHM, use this path:
```python
import os
PYFEHM_ROOT = os.path.dirname(os.path.abspath(__file__))  # or appropriate path
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

dat.run('input.dat', exe=FEHM_EXE, verbose=False)
```

## Test Files

Tests are located in the `ccFEHM/` directory. Run tests with:
```bash
python ccFEHM/test_single_block.py
```

## Simulation Skill

The PyFEHM simulation builder skill is available at `.claude/skills/pyfehm-simulation/`.
Read `SKILL.md` for workflows on building and debugging simulations.

## Lessons Learned

> *These lessons capture past patterns that helped. They are starting points, not guarantees. If a remembered approach fails, investigate fresh—the situation may differ.*

### [2026-02-05] [Python] Code consistency across sections

**Context**: Writing a test script with simulation code and a separate plotting/analysis section
**Mistake**: Wrote the simulation section with `D = k / (phi * mu * c_f_Pa)` but the plotting section with `c_t_Pa = phi * c_water * 1e-6` then `D = k / (phi * mu * c_t_Pa)`, introducing phi² instead of phi
**Resolution**: Found the inconsistency by comparing numerical results (which matched analytical) against the plot (which showed factor-of-10 offset)
**Remember**: When duplicating physics calculations across different sections of a file, copy-paste and verify rather than rewriting from memory. Inconsistent formulas in different code sections cause bugs that are hard to trace.

### [2026-02-05] [FEHM] [CO2] CO2-only mode requires pressure-based injection

**Context**: Setting up CO2 injection in a closed single-block model
**Mistake**: Used fixed mass rate injection (bc_flag=0) for CO2-only mode (iprtype=2); output showed "Total co2 injected = 0.000000E+00"
**Resolution**: Changed to pressure-based injection (bc_flag=1) with impedance parameter
**Remember**: For CO2-only mode (iprtype=2), must use bc_flag=1 (pressure-based injection). Fixed mass rate (bc_flag=0) does not work for CO2-only.

### [2026-02-05] [FEHM] [CO2] Two-phase closed systems cause singular matrix

**Context**: Running water+CO2 simulation in closed system
**Mistake**: Attempted closed water+CO2 simulation without pressure boundary; got "singular matrix found during normalization"
**Resolution**: CO2-only (iprtype=2) works closed; water+CO2 (iprtype=3,4) requires pressure boundary condition
**Remember**: Water+CO2 modes (iprtype=3,4) need a pressure BC to avoid singular matrix. CO2-only (iprtype=2) can run in closed systems.

### [2026-02-05] [FEHM] [CO2] Zero CO2 saturation blocks CO2 injection

**Context**: Injecting CO2 into water-saturated block
**Mistake**: Started with 0% CO2 saturation; no CO2 flowed despite injection source
**Resolution**: CO2 relative permeability is zero at zero saturation. Must initialize with some CO2 saturation via co2frac with override_flag=1
**Remember**: CO2 injection requires non-zero initial CO2 saturation due to relative permeability. Use co2frac with override_flag=1 to set initial CO2 presence.

### [2026-02-05] [FEHM] [CO2] CO2 property table must be specified explicitly

**Context**: Running CO2 simulation
**Mistake**: Simulation failed because CO2 property table not found
**Resolution**: Added `dat.files.co2in = os.path.join(PYFEHM_ROOT, 'co2_interp_table.txt')`
**Remember**: CO2 simulations require explicit path to co2_interp_table.txt via dat.files.co2in
