# GameBoy (dmg) Assember

GameBoy assembler/linker in Python

This is an experimental project that will compile LR35902 (Z80-ish) assembly
and create an executable that is compatible with a Game Boy (DMG) ROM that
can, in turn, be run by on-line emulators such as https://gameplaycolor.com.

This compiler is designed so that hobbyists can create/test/play their own DMG
and Game Boy Color games.

One of the goals of this project is to be able to build and run a game from an
iPad using [Pythonista](http://omz-software.com/pythonista/) or even just from the Mac.

At this point, this code is very incomplete and not even usable. It also
represents my first Python project. Proceed with caution.

If you want to play and test it you can refer to the gbasm/tests/unit_tests.py
to get an idea of how to use the various objects. Unit tests are being built
out and consist of a bunch of Label tests.

Many of the python files have a __main__ that runs a simple smoke-test of the
object(s) in the file. For example, the instruction.py file has several
allocate/print statements, some of them negative.

# Simple Example
This is nonsensical code but provides an example of how the parser/assembler is coming along:

```
SECTION "CoolStuff",WRAM0
CLOUDS_X: DB $FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00,$FF,$00
BUILDINGS_X: DS 1
FLOOR_X: DS 1
PARALLAX_DELAY_TIMER: DS 1
FADE_IN_ACTIVE:: DS 1
FADE_STEP: DS 1
ALLOW_PARALLAX:: DS 1
READ_INPUT:: DS 1
START_PLAY:: DS 1

IMAGES    EQU $10
BIGVAL    EQU 65500

SECTION "game", ROMX

.update_game:
    ld HL, BIGVAL   ; should be 0x21 dc ff
    ld HL, SP+$55   ; should be 0xf8 55
    ldhl sp, $6a    ; should be 0xf8 6a
    ld A, (HL)
    jr nz, .update_game
    jr .continue_update_1
    ld A, (HL)
    XOR D
    CP H
    CP L
.continue_update_1:
    CP A
```

The code located in the gbz80asm.py file will generate logs as to what the
assembler is doing and what binary values are being generated. Again, this is
strictly alpha software and doesn't generate a binary file (yet). It's almost
to that point though :)

Cheers,
- mitch

