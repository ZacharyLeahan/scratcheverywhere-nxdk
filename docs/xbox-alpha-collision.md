# Xbox alpha collision candidate

This change is under validation on a feature branch. It is not ready to merge.

In [Fireboy and Watergirl](https://scratch.mit.edu/projects/571560558/), walking
Fireboy into blue water ends the game in the official Scratch player, our Mac
port, and the previous Xbox build in xemu. The physical Xbox instead allowed
him to walk across it.

A bounded console trace found the correct hitbox and hazard costumes loaded,
but nine collision checks across the pool returned false. The hazard's alpha
pixels, dimensions and scale matched xemu. Sampling a world-space grid inside
the sprites' collision circles can miss a thin overlap between samples.

The candidate intersects the full source alpha pixels for axis-aligned Xbox
sprites. It handles horizontal flips and clipped intersections without
allocating another mask. Rotated sprites retain the existing collision path.
Using the reduced mask cells was insufficient in the first hardware candidate;
the current version uses the source pixels' actual boundaries.

Validation so far:

- 1,507 independent rectangle-oracle cases pass in both argument orders with
  AddressSanitizer and UndefinedBehaviorSanitizer.
- The actual baseline and candidate functions were checked against saved
  console masks: the baseline misses all nine queries; the candidate rejects
  the position before the pool and detects the eight overlaps inside it.
- The NXDK build passes.
- On the physical Xbox, Fireboy safely crosses red water, then dies in blue
  water. This passes twice, including a normal Black-button Retry between runs.
  Retry and return to the game list also pass. A briefly lifts the character
  under the starting ceiling; this is not an open-area jump qualification.

The full-level regression is still open. In xemu, the established route clears
the lower pools but fails to stay on the upper bank; an earlier turn also falls
back to the lower floor. Input timing, terrain contact and a matched reference
comparison still need investigation. No full-level clear, performance, audio,
other-game compatibility or playability-grade improvement is claimed yet.

Run the host geometry checks with:

```sh
python3 tests/collision_grid_test.py
```
