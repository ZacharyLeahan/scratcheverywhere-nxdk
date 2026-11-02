# Xbox controller reference

The fork keeps upstream's menu appearance. Controller help lives here rather
than in gameplay popups, pause-screen help text or added project banners.

## Homebrew controls

| Action                               | Control                                                   |
| ------------------------------------ | --------------------------------------------------------- |
| Pause / resume                       | Back / Select                                             |
| Leave a project                      | Pause → Return to game list                               |
| Dashboard, reboot or power off       | Pause → Exit / System, or B / Y from the game list        |
| Restart a project that used Stop All | Short Start press; otherwise use pause → Click Green Flag |
| Reboot shortcut                      | Hold LT + RT + Back + Start for two seconds               |
| Move the emulated mouse              | Hold White + D-pad / left stick                           |
| Click the emulated mouse             | Keep White held + RT; Black also clicks                   |

System actions require confirmation. The reset shortcut needs a responsive
runtime and connected controller; it cannot recover every hard hang.

## Prepared game shortcuts

| Game                  | Controls retained without the added instruction banners                                                                                                                                                     |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Beach Volleyball      | X starts Easy CPU; D-pad moves, A jumps. X replays after the title returns.                                                                                                                                 |
| GlowBall              | X starts CPU; directions move, A jumps; X replays from the title.                                                                                                                                           |
| Mushroom Valley       | Hold/release A to jump; A activates the original Retry action after a loss.                                                                                                                                 |
| Fireboy and Watergirl | D-pad selects a level; A starts it. The selected-level label remains. Fireboy uses D-pad/A; Watergirl uses B/Y to move and X to jump, or the right stick. B opens the level menu on results; Black retries. |

These are separate prepared projects and controller profiles. Original gameplay,
assets, level locks and mouse controls remain. Independent two-controller
binding is still open; two keysets on one controller are not two-pad support.

The installed game list still opens directly at startup and after leaving a
project. See [current installation and test limits](xbox-game-status.md).
