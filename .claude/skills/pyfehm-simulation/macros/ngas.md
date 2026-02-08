# ngas - Noncondensible Gas Transport

**Status**: Optional

## Purpose

Noncondensible gas transport. Used to model air or other gases that do not condense (unlike water vapor).

## Input Format

```
ngas
ICO2D
JA  JB  JC  PCO2
...
JA  JB  JC  CPNK
...
JA  JB  JC  QCD
...
```

Note: All Group 2 values are entered first, followed by Group 3 values, followed by Group 4 values.

## Parameters

### Group 1 - Solution Control

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| ICO2D | integer | 3 | Solution descriptor (see table) |

### Group 2 - Initial Gas Pressure

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| PCO2 | real | 0. | Initial partial pressure of noncondensible gas (MPa). If PCO2 < 0, ABS(PCO2) is temperature and partial pressure calculated as: PCO2 = PT - PSAT(T) |

### Group 3 - Humidity/Pressure Control

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| CPNK | real | 0. | If CPNK ≤ 0: ABS(CPNK) is specified gas pressure held constant. If CPNK > 0: CPNK is specified relative humidity and saturation calculated from vapor pressure lowering and capillary pressure. |

### Group 4 - Gas Source

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| QCD | real | 0. | Specified air source strength (kg/sec) |

## ICO2D Values

| ICO2D | Description |
|-------|-------------|
| 1 | 3 DOF solution reduced to 1 DOF (also sets ICOUPL=5 in **iter**) |
| 2 | 3 DOF solution reduced to 2 DOF (also sets ICOUPL=5 in **iter**) |
| 3 | Full 3 DOF solution |

## Humidity Calculation

When CPNK > 0 (specifying relative humidity), saturation is calculated using:

```
Pcap(Sl) = ln(h) × ρl × R × T
```

where:
- Pcap = capillary pressure function
- h = humidity (CPNK)
- R = gas constant
- T = temperature
- ρl = liquid density

The humidity condition is only enabled for the van Genuchten capillary function model (see **rlp** macro).

## Example

```
ngas
    3
    1       800        1       -20

    1       800        1        0.

    1       800        1        0.

```

In this example:
- Full 3 DOF solution (ICO2D=3)
- Initial temperature 20°C at all nodes (PCO2=-20, so gas pressure calculated from saturation pressure)
- No fixed gas pressure (CPNK=0)
- No gas source (QCD=0)

## Notes

- The ngas macro enables air-water-heat simulations
- For isothermal air-water, use **airwater** macro instead
- Gas pressure adds to total pressure: Ptotal = Pwater + Pgas
- Negative PCO2 calculates initial gas pressure from temperature
- Gas is assumed ideal for property calculations
- Commonly used for vadose zone simulations with air
