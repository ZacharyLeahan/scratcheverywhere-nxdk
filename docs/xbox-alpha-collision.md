# Xbox alpha collision candidate

This Xbox-specific change is under validation on a feature branch. Broader game
and performance qualification remains separate from the collision fix.

In [Fireboy and Watergirl](https://scratch.mit.edu/projects/571560558/), walking
Fireboy into blue water ends the game in the official Scratch player, our Mac
port, and the previous Xbox build in xemu. The physical Xbox instead allowed him
to walk across it.

A bounded console trace found the correct hitbox and hazard costumes loaded, but
nine collision checks across the pool returned false. The hazard's alpha pixels,
dimensions and scale matched xemu. Sampling a world-space grid inside the
sprites' collision circles can miss a thin overlap between samples.

The candidate intersects the full source alpha pixels for axis-aligned Xbox
sprites. It handles horizontal flips and clipped intersections without
allocating another mask. Rotated sprites retain the existing collision path.
Using the reduced mask cells was insufficient in the first hardware candidate;
the current version uses the source pixels' actual boundaries.

Validation so far:

- 1,507 independent rectangle-oracle cases pass in both argument orders with
  AddressSanitizer and UndefinedBehaviorSanitizer.
- The actual baseline and candidate functions were checked against saved console
  masks: the baseline misses all nine queries; the candidate rejects the
  position before the pool and detects the eight overlaps inside it.
- The NXDK build and Original Xbox CI build pass.
- On the physical Xbox, Fireboy safely crosses red water, then dies in blue
  water. This passes twice, including a normal Black-button Retry between runs.
  Retry and return to the game list also pass. A briefly lifts the character
  under the starting ceiling; this is not an open-area jump qualification.
- The official Scratch player, xemu and the physical Xbox all clear the blue
  pool and reach the upper platform when jumping from matching takeoff points.
- Fresh xemu runs clear Level One with all seven gems, both exits and all three
  green medals: 54 seconds with the SDL renderer and 53 seconds with the native
  Xbox renderer. Both runs also pass normal B Menu, selection of the unlocked
  Level Two and its startup. An earlier exploratory clear missed the time medal.
- Level EATEN also loads after Fireboy cleanup, moves, jumps and collects one
  cube on hardware; a full Level EATEN clear was not established in that run.

The old bank route took off too far from the platform. Moving along the right
shelf before jumping reaches the platform in all three players; no movement or
jump physics were changed. The fresh full-level regression uses that route.

A full physical-Xbox clear, broader game checks, performance and audio remain
open. A timed green-pool jump failed in both the official player and on Xbox;
that takeoff is not yet qualified. A long exploratory xemu session also showed
decor artifacts after repeated attempts; the fresh full-level run rendered
normally. Its cause and relationship to the change remain unverified. No
playability-grade improvement is claimed yet.

Run the host geometry checks with:

```sh
python3 tests/collision_grid_test.py
```
