# time - Time Stepping

**Status**: REQUIRED

## Purpose

Control simulation time step and duration. This macro specifies the initial time step size, final simulation time, maximum number of time steps, and output intervals.

## Input Format

```
time
DAY  TIMS  NSTEP  IPRTOUT  YEAR  MONTH  INITTIME
DIT1  DIT2  DIT3  ITC  [DIT4]
...
(blank line to end Group 2)
```

## Parameters

### Group 1 - Basic Time Control

| Variable | Format | Description |
|----------|--------|-------------|
| DAY | real | Initial time step size (days). Must be larger than DAYMIN defined in **ctrl** macro |
| TIMS | real | Final simulation time (days) |
| NSTEP | integer | Maximum number of time steps allowed |
| IPRTOUT | integer | Print-out interval for nodal information (number of time steps) |
| YEAR | integer | Year that simulation starts |
| MONTH | integer | Month that simulation starts |
| INITTIME | real | Initial time of simulation (days). Default is 0 if no restart file, or time from restart file |

### Group 2 - Time Step Changes (repeated as needed)

| Variable | Format | Description |
|----------|--------|-------------|
| DIT1 | real | Time (days) at which time step change occurs |
| DIT2 | real | New time step size (days). If DIT2 < 0, then ABS(DIT2) is the new time step multiplier |
| DIT3 | real | Implicitness factor: ≤1.0 = backward Euler, >1.0 = second-order implicit scheme |
| ITC | integer | New print-out interval (number of time steps) |
| DIT4 | real | Maximum time step size for this interval (days). Optional - defaults to **ctrl** value |

## Output Timing

- Contour plot output is written at each DIT1 time regardless of **cont** macro settings
- Restart file is written (or rewritten) at each DIT1 time
- Group 2 can be used to generate output at specific times by using multiple entries

## Example

```
time
   30.0     3650.0         20          5        1989         10        0.0
    1.0       -1.2        1.0         10

```

In this example:
- Initial time step: 30 days
- Final simulation time: 3650 days (10 years)
- Maximum 20 time steps allowed
- Print every 5th time step
- Simulation starts October 1989
- Initial time = 0 days
- At day 1.0: time step multiplier becomes 1.2 (DIT2=-1.2), backward Euler (DIT3=1.0), print every 10 steps

## Steady-State Example

For steady-state problems, use large final time and allow many time steps:

```
time
    1.0       1.e12       1000          1        2024          1        0.0

```

## Notes

- DAY should be larger than DAYMIN from the **ctrl** macro
- If DIT4 is omitted, the maximum time step from **ctrl** is used
- The time step multiplier from **ctrl** (AITEFAC) controls automatic time step adjustment
- For transient problems, choose initial time step based on expected rate of change
- When using **stea** macro, time parameters pertain to the transient portion after steady state
- Multiple Group 2 entries can force output at specific times of interest
- IPRTOUT controls terminal and .out file output frequency
