# stop - End of Input

**Status**: REQUIRED

## Purpose

Signal the end of input. This macro must always appear as the last line of an FEHM input deck.

## Input Format

```
stop
```

## Parameters

None. No input is associated with this control statement.

## Example

```
... (other macros)

rock
    1        100          1       2500.       1000.       0.20

time
    1.0     1000.0        100          1        2024          1        0.0

stop
```

## Notes

- This macro is always required
- It must be the last macro in the input file
- No data follows the `stop` keyword
- The word "stop" must appear in the first 4 columns
- After reading `stop`, FEHM begins execution of the simulation
