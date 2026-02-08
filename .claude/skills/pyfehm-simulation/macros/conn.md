# conn - Print Node Connections

**Status**: Optional (diagnostic)

## Purpose

Print number of connections for each node (after simplification of connectivity based on porosity) and stop. This macro is used to diagnose grid connectivity issues.

## Input Format

```
conn
```

No additional input required.

## Behavior

When invoked:
1. FEHM reads the grid and connectivity
2. Simplifies connectivity based on porosity (zero-porosity nodes disconnected)
3. Prints connection count for each node
4. **Stops execution**

## Use Cases

- Determine if isolated nodes are left active after setting porosity to zero
- Debug problems with particle tracking algorithms (which fail with poorly connected nodes)
- Verify grid quality before running full simulation
- Check that deactivated regions are properly disconnected

## Example

```
conn

```

## Notes

- This is a diagnostic macro - simulation does not continue after
- Run separately from actual simulation
- Useful when troubleshooting unexpected flow paths
- Poorly connected nodes can cause issues in:
  - Particle tracking
  - Transport calculations
  - Solver convergence
