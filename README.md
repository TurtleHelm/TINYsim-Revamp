# TINYsim

Simulation program for Conor McBride's TINY Machine.

```f
Enter input queue (Format: x, x, x, x...): 0, 0, 1, C, 0, 7, C, A
Enter TINY configuration (Format: x x x x  xxxxxxxxxxxxxxx): 0 0 0 0 65F65E65D65C8F70
I L F A  Memory----------  Action---
P I R C  0123456789ABCDEF  OPR & ? !
-------  ----------------  ---------
0 0 0 0  65F65E65D65C8F70  GET - 0 -
1 . 2 .  ................  STA F - -
3 . . .  ................  GET - 0 -
4 . . .  ................  STA E - -
6 . . .  ..............0.  GET - 1 -
7 . 0 1  ................  STA D - -
9 . . .  .............1..  GET - C -
A . . C  ................  STA C - -
C . . .  ............C...  SCF - - -
D . 1 .  ................  JMP 0 - -
0 . . .  ................  GET - 0 -
1 . 3 0  ................  STA F - -
3 . . .  ................  GET - 7 -
4 . 1 7  ................  STA E - -
6 . . .  ..............7.  GET - C -
7 . . C  ................  STA D - -
9 . . .  .............C..  GET - A -
A . . A  ................  STA C - -
C . . .  ............A...  ADC C - -
E . 5 5  ................  PUT - - 5
F . . .  ................  HLT - - -
0 . D .  ................
-------  ----------------  ---------
Halted Normally
```

## How To Use

+ Run the script with Python 3 (3.10 tested)
+ Input a TINY input queue in the format "x, x, x, x..."
+ Input a TINY configuration in the format "x x x x  xxxxxxxxxxxxxxx"
+ The program should then print a trace and state how the TINY program halted.

## Notes

+ This script halts after 500 operations, and assumes that the TINY program loops indefinitely
+ This can be changed by editing the main loop of the program, line 298. Set count to a desired value.

## Known Bugs

### Index out of Range error once reaching end of instruction pointer before a loop

