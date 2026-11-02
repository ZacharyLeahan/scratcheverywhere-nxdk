# Xbox alpha collision

This Xbox-specific repair fixes missed thin overlaps between axis-aligned
sprites. Broader game and quality qualification remains separate from the
collision fix.

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
- The combined collision and current-main build also clears Level One on the
  physical Xbox with all seven gems and both exits. The time medal is missed
  during the stop-and-inspect run. B Menu, selection and startup of the
  naturally unlocked Level Two, runtime pause and return to the game list all
  pass. Normal movement, fresh jumps and the authored crate are used; no
  checkpoint or gameplay state is injected.
- Level EATEN clears Level One and reaches Level Two on the physical Xbox.
  Native xemu also clears its earned Level Two, resets Level Three with Y, and
  returns to the browser with zero remaining sprites.

The old bank route took off too far from the platform. Moving along the right
shelf before jumping reaches the platform in all three players; no movement or
jump physics were changed. The fresh full-level regression uses that route.

Later physical levels, broader game checks, whole-game performance and audio
remain open. Both characters now pass the physical green-pool jump after a
running approach; earlier timed takeoffs failed in both the official player and
on Xbox. One xemu guest shows decor artifacts already in its first gameplay
capture; this predates its retries. Other fresh full-level runs render normally.
The affected decor has intact CPU pixels and a correctly decoded GPU allocation;
composition, other textures and its relationship to this change remain open. No
playability-grade improvement is claimed yet.

Run the host geometry checks with:

```sh
python3 tests/collision_grid_test.py
```

## Bounded hardware performance — November 2, 2026

Two matching Release builds on the physical 128MB Xbox compare current main
`89a23e4d` with this fix. Profiling flags and CMake cache bytes match; only the
collision implementation differs. The existing frame profiler is enabled,
detailed thread tracing is off, and test video streams are closed during each
measurement. Projects, profiles and saved settings are unchanged.

Fireboy stays at the initial Level One spawn for 50 seconds. Appel repeats eight
Left 1.5-second / Right 2-second cycles at its first wall with one apple, for 28
seconds. Both scenes are visually checked before and after. Every complete
120-frame interval enclosed by the action is included, with 0.5-second boundary
guards; loading/menu intervals are excluded.

| Scene / build         | Measured frames |   FPS | Mean script ms/frame | Median window p95 ms |
| --------------------- | --------------: | ----: | -------------------: | -------------------: |
| Fireboy spawn / main  |            1200 | 29.84 |                10.41 |                34.59 |
| Fireboy spawn / fix   |            1320 | 29.89 |                11.23 |                34.60 |
| Appel movement / main |             600 | 27.03 |                16.62 |                52.69 |
| Appel movement / fix  |             600 | 26.54 |                17.32 |                52.87 |

The fix costs about 0.8 ms of script time per frame in Fireboy and 0.7 ms in
Appel in these samples. Fireboy's average frame rate is unchanged; Appel is
about 0.5 FPS lower. These short samples do not establish a general performance
improvement. Both Fireboy samples contain one roughly 267 ms hitch. Appel's
maximum periods are 151.8 ms on main and 151.2 ms with the fix; slow frames
remain. Window p95 values are not pooled frame percentiles. No 60 FPS,
Mac-equivalent smoothness, retail-64MB or audio qualification is claimed.

All 75 candidate and 155 main frame reports match the retrieved console logs.
Received UDP sequences are contiguous within each run; initial network messages
are retained in the disk logs. Both runs return through the browser to XBMC.
Main's return leaves the dashboard responsive but FTP unavailable; one verified
XBMC software Reboot restores FTP. This repeats an earlier network-handoff
issue; its cause remains open. No DMA or out-of-memory error is logged.

The ordinary combined build also passes Appel's three-apple terrain/scroll/jump
check and Ninja Climb's natural spike death/respawn, first-course clear, earned
second-course startup and browser return. These checks do not qualify later
levels or independent two-controller play.

The profiling XBEs are `bef0bd96…` (main) and `8f15c424…` (fix). Local evidence
is under ignored `build-xbox/hardware/pack30-20261101/`:
`collision-performance-143/`, `performance-results-143.json`,
`performance-scene-review-143.json` and `performance-log-verification-143.json`.
The normal build is restored with profiling and UDP logging off; the regular
dashboard launcher is preserved.
