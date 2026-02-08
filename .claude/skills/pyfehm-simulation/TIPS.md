# PyFEHM Troubleshooting Tips

This file collects lessons learned from debugging FEHM simulations. New tips are appended as issues are resolved.

---

## How to Use This File

1. **Search first**: Before extensive debugging, search this file for similar symptoms
2. **Apply solutions**: Try documented fixes for matching error patterns
3. **Contribute**: When you resolve a new issue, append a tip using the format below

---

## Tip Format

When adding new tips, use this structure:

```markdown
### [YYYY-MM-DD] [Context] Brief descriptive title

**Symptom**: What error or unexpected behavior occurred
**Root Cause**: Why it happened (the underlying issue)
**Resolution**: What fixed it (specific code or parameter changes)
**Remember**: Key insight for future reference
```

---

## Tips

<!-- New tips are appended below this line -->

### [2026-02-05] [Temperature BCs] fix_pressure() doesn't fix temperature with low permeability

**Symptom**: Temperatures settle to the average of IC values instead of boundary values
**Root Cause**: `fix_pressure()` uses the `flow` macro which controls T via fluid injection. With very low permeability (e.g., 1e-20 m²), no fluid can flow so temperature cannot be controlled.
**Resolution**: Use `fix_temperature(T, multiplier=...)` which uses the `hflx` macro to directly control heat flow. Scale the multiplier inversely with grid spacing: `multiplier = base * (dx_ref / dx)`
**Remember**: For pure heat conduction problems, always use `fix_temperature()`, not `fix_pressure()`

### [2026-02-05] [HFLX stability] Large hflx multipliers cause numerical instability

**Symptom**: "timestep restarted because of balance errors or variable out of bounds", negative pressures
**Root Cause**: The hflx multiplier of 1e10 (default) produces heat flows of ~1e11 MW which overwhelms the coupled mass-energy equations
**Resolution**: Use physics-based multiplier scaling: `multiplier = 5e-5 * (0.05 / dx)` where dx is grid spacing. This ensures the hflx heat flow is ~10x the conductive heat flow while remaining stable.
**Remember**: Never use the default `fix_temperature()` multiplier (1e10) - always compute an appropriate value based on problem physics

### [2026-02-05] [Verification] Always verify grid convergence when claiming "numerical error"

**Symptom**: Large discrepancy between numerical and analytical solutions
**Root Cause**: Could be BC implementation issue, wrong analytical solution, or genuine numerical error
**Resolution**:
1. Check boundary values in output files to verify BCs are applied
2. Skip t=0 when comparing (IC ≠ BC solution)
3. Run multiple grid resolutions and verify error decreases with refinement
**Remember**: Saying "it's numerical error" requires evidence - at minimum run 2-3 grid resolutions and show error converges
