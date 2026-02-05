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
