Seven-language quine relay: shared SMATINY subroutines

Befunge-98 -> Fish -> Muriel -> Underload -> Self-modifying Brainfuck
           -> SMATINY -> Piet -> original Befunge-98

This version replaces the unrolled SMATINY output encoding with reusable,
reversible subroutines. The complete cycle is verified byte for byte.
Every stage emits the next source without stdin or external source access.
Piet's canonical source is the exact P3 PPM file, including its whitespace.
There is no decoder, decompressor or image-conversion adapter in the cycle.
SMATINY is used instead of SMETANA because SMETANA has no output operation.

Before / after (bytes):
  Befunge/Fish seed, each        2,885           5,075
  Muriel                       13,945          24,895
  Underload             1,054,434,920       2,709,003
  SMBF                  1,036,016,198       2,642,148
  SMATINY               1,036,015,917       2,641,867
  Piet image                6,139,600      11,076,316

The source compiler grew, so the seed and its Piet rendering grew. Sharing
SMATINY output code nevertheless cuts the total source size by over 99%.
All seven source files now fit in the included archive; none is omitted.
Exact byte counts and SHA-256 hashes are in manifest.json, and before/after
measurements are in comparison.json. The earlier version remains separate.

Run and rebuild:
    cd quine-relay/optimized
    python run_relay.py
Requires Python 3, g++, make and zlib development headers. Add --fixtures
for comparisons with included published/reference implementations; that also
requires Perl and Node. The native runner interprets each generated source,
not a shortcut that constructs the following program outside its language.
Allow about 50 MB of working disk space including optional fixtures.

How the compression works in SMATINY:
There are 13 colour-token routines: six light colours, six normal colours,
and black. Each emits one 12-byte PPM pixel token. Its seven-step output
sequence restores its source instructions after use.
Each colour also has doubling routines D1 through D21. Dj calls D(j-1)
twice; D0 is the colour-token routine. A run of n pixels becomes calls to
these routines according to the set bits in n, rather than a fresh output
program for every image byte. Header characters still use short one-shot
output sequences.

A four-step call, with entry a and return slot e, is:
    k.   Swap k+2 with e.
    k+1. Swap k+1 with a-1.
    k+2. Swap e with k+2.
    k+3. Swap k+1 with a-1.
These are schematic indices, not literal SMATINY syntax. The first swap
installs the return instruction. The second moves the current instruction,
so the program counter moves with it and execution enters the callee. At
the return slot, the third instruction moves control back to k+3. The last
swap restores the jump instruction and the callee's entry guard. Return
slots are distinct at every doubling level, allowing nested calls.
The routines restore their state and can be called again. The finite main
program supplies the call sequence; this does not assume an infinite loop
or change SMATINY's reversible control-flow rules.

The other languages retain their roles:
- Befunge/Fish use opposite directions and grid reflection. Fish normalizes
  blank grid cells to spaces and emits packed source bytes plus Muriel code.
- Muriel serializes an escaped copy of its template into replacement source.
  A library-generation phase emits the reusable SMATINY routines; a run-based
  phase emits calls selected by each run length's binary decomposition.
  The full stage uses 217,148 replacements, down from 6,139,602.
- Underload quotation, concatenation and 40 duplications build the SMBF
  arithmetic runs, then stream its source and embedded data.
- SMBF scans and restores source-tape bytes, rewrites a future colon into an
  opening bracket, prints SMATINY and executes that new bracket to halt.
- Piet still uses block areas and hue/lightness transitions to push and emit
  the seed bytes. A rectangular final block traps all eight DP/CC exits.
  This version's image is a 307,675 by 3 strip; its long geometry remains an
  obvious future optimization target.

Verification:
The full Fish stage runs in the published interpreter and the full Piet
image runs in npiet 1.3f. The closing output equals the Befunge source byte
for byte, and an independent layout calculation verifies the Piet raster.
The native streaming interpreters execute the large intermediate programs.
Their Muriel optimization recognizes the exact generated serializer and
transfers only explicitly serialized state to the replacement environment.
Complete fixtures compare its output against the published Perl interpreter.
Further complete fixtures check Underload/SMBF against published interpreters
and SMATINY against an independent dictionary implementation. The fixtures
exercise repeated calls, nested doubling, all six colour families and the
image's header and terminal trap. Native tools cover the operations used by
this relay; they are not complete implementations of every language dialect.

Sources / attribution:
Fish: https://gist.github.com/anonymous/6392418
Muriel: Chris Pressey / Cat's Eye Technologies, via graue/esofiles on GitHub.
Underload: public-domain interpreter from graue/esofiles/underload/underload.html.
SMBF: https://none-none1.github.io/Interpret-Esolangs-Online/smbf.js
SMATINY: David House's reference Haskell implementation is included for study.
npiet 1.3f: https://www.bertnase.de/npiet/ ; see npiet-1.3f/COPYING.
