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
