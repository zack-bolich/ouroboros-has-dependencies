# Ouroboros Has Dependencies

![A seven-esolang quine relay. Seven esolangs. One deeply unnecessary round trip.](assets/banner.png)

**Seven esolangs. One deeply unnecessary round trip.**

Some nonsense programmed entirely on my phone: a seven-esolang quine relay where the snake eats its tail after compiling it into a picture.

```text
Befunge-98 → Fish → Muriel → Underload → Self-modifying Brainfuck
    ↑                                               ↓
   Piet ←─────────────────────── SMATINY ←────────────┘
```

Each program prints the complete source of the next. The final program is an actual executable Piet image, and it prints the original 5,075-byte Befunge program exactly. No input, source-file reading, or external decoder is used by the programs in the cycle.

## Why this is ridiculous

- Befunge and Fish traverse a shared program grid in opposite directions.
- Muriel repeatedly replaces itself, carrying its state in an escaped copy of its program template.
- Underload performs quotation and stack gymnastics to generate an SMBF program.
- SMBF rewrites an instruction it subsequently executes.
- SMATINY builds calls and returns out of instruction swaps, then nests them into binary doubling routines.
- Piet executes a 307,675 × 3 image whose geometry, block sizes, and color transitions reproduce the starting program.

The first implementation inflated a 2,885-byte seed into **3.13 GB** of source. Reusable SMATINY routines brought the total down to **19.1 MB**—a **99.39% reduction**. The seed grew to 5,075 bytes. Progress, technically.

| Stage | Source bytes |
|---|---:|
| [Befunge-98](optimized/seven.b98) | 5,075 |
| [Fish](optimized/seven.fish) | 5,075 |
| [Muriel](optimized/seven.mur) | 24,895 |
| [Underload](optimized/seven.ul) | 2,709,003 |
| [Self-modifying Brainfuck](optimized/seven.smbf) | 2,642,148 |
| [SMATINY](optimized/seven.smatiny) | 2,641,867 |
| [Piet image](optimized/seven.ppm) | 11,076,316 |

SMATINY is the output-capable relative of SMETANA. Plain SMETANA has no output instruction, which would make this particular bad idea less convenient.

## Run the entire unnecessary round trip

Requires Python 3, a C++17 compiler (`g++`), `make`, and zlib development headers.

```sh
python optimized/run_relay.py
```

To include comparisons against published and independent reference interpreters, also install Perl and Node, then run:

```sh
python optimized/run_relay.py --fixtures
```

The runner rebuilds and executes the stages, checks the closing bytes, and independently verifies the Piet raster. It uses published Fish and npiet interpreters plus checked native streaming runners for the intermediate languages. The Muriel runner compiles the exact generated state serializer to avoid reparsing the same template on every replacement.

All seven source programs are included. Their exact hashes are in [manifest.json](optimized/manifest.json). Keep their whitespace intact: the cycle closes on bytes, not artistic interpretation.

## Further questionable details

See [the implementation notes](optimized/README.txt) for the reversible SMATINY calling convention, the native runners' supported operations, verification details, and third-party interpreter attribution. The included interpreter sources retain their original license notices; npiet's license is in [COPYING](npiet-1.3f/COPYING).

The Piet image remains a very long output strip. There is still ample room to make this nonsense smaller or stranger.
