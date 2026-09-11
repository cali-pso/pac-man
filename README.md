*This project has been created as part of the 42 curriculum by ssayada, rapoggi.*

# Pac-Man — Ghosts! More ghosts!

## Description

This project is a complete, playable recreation of the arcade classic **Pac-Man**,
written in Python with an object-oriented, modular architecture. On top of the
faithful base game, it adds several original game modes (Shadow, Hardcore,
Roguelite and a 2-player mode with three sub-modes), a per-mode persistent
high-score system, procedurally generated mazes, original music and sound
effects, a pause menu, a cheat mode for evaluation, and a fully
configuration-driven design (every gameplay value can be tuned from a single
`config.json` file).

The player clears each level by eating all the pacgums while avoiding the ghosts,
progresses through multiple levels (score and lives are carried over), and can
compete for the top-10 scoreboard of each mode.

### Game modes

**Normal** — The faithful base game. Clear each level by eating every pacgum
while avoiding the four ghosts; a super-pacgum in each corner makes ghosts
edible for a short time. The HUD shows only the level, score, lives and timer.

**Hardcore** — A hard preset: a single life, level
time reduced by a factor, and no super-pacgums (ghosts are a permanent threat,
and pacgums are the only source of points). The scoring is the same as other
modes — the difficulty is reflected by its own leaderboard, not by inflated
points.

**Shadow** — The corridors are dark: only a circular **light zone** around
Pac-Man reveals the pacgums, super-pacgums, ghosts and walls. The radius
**grows** with every pacgum eaten and **shrinks** over time. Eating a
super-pacgum triggers a **shine bright** that lights up the whole map for a few
seconds. All shadow parameters are configurable.

**Roguelite** — After each cleared level, a screen offers **3 cards**
(bonus/malus), one of which is a **mystery card (`???`)**. The draw is
**anti-streak**: picking a bonus makes bonuses rarer next time, and vice versa.
Effects **accumulate over the run**: Pac-Man/ghost speed, extra lives, a shield
(absorbs a hit by granting a few seconds of invincibility during which Pac-Man
passes through ghosts), a pacgum **magnet**, super-pacgum duration, per-level
time, a permanent reveal/hide of the mystery card, a start-of-level freeze, and
a score multiplier. In this mode, each super-pacgum also grants a **temporary**
bonus/malus for the current level, announced on screen. The pause menu (ESC)
lists all active effects.

**2 Players** — A sub-menu offers three sub-modes, each with its own
leaderboard. Player 1 uses **WASD**, Player 2 uses the **arrow keys**.

- **Versus** — P1 controls Pac-Man, P2 controls one ghost (which changes every
  level); the other three are AI. P2 wins when Pac-Man runs out of lives; P1
  wins by completing the levels.
- **Coop** — One shared Pac-Man: P1 controls the vertical axis, P2 the
  horizontal axis.
- **Random** — One shared Pac-Man, with control switching randomly between P1
  and P2 (the HUD shows who is currently playing).

### Special items

- **Pacgum** — base points; clearing them all ends the level.
- **Super-pacgum** — makes ghosts edible for a short time (they flee and score
  points if eaten).
- **Mega-pacgum** — a **rare** spawn (configurable), in every mode **except
  Normal**. Until the end of the level it freezes the timer, freezes and makes
  the ghosts edible (eaten ones do not respawn), lights up the whole map, speeds
  Pac-Man up and multiplies the score. A warning sound announces its presence.

## Instructions

### Requirements

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)** (dependency and environment manager)
- The **MLX** graphics library (the `mlx_CLXV` build provided on the 42 intranet)
- The assigned **`mazegenerator`** package (A-Maze-ing wheel)
- **pygame** (audio) and **pydantic** (configuration validation)

### Build the MLX library

The MLX library is an external dependency compiled once. Download `mlx_CLXV`
from the intranet, unpack it, then inside its folder:

```bash
make                 # checks config, compiles, packages the Python module
pip install mlx-*.whl   # install the produced wheel in your environment
```

### Install and run the game

```bash
uv sync                              # install project dependencies
uv run python3 -m src config.json    # launch the game with a config file
```

The program takes **exactly one argument**: the path to a JSON configuration
file. Any error (missing file, invalid value, missing key) is handled gracefully
with a clear message — never a Python traceback.

## Resources

- Original Pac-Man (Namco, 1980) — game design reference.
- MLX / MiniLibX documentation: `man man/man3/mlx.3` and the `mlx.h` header.
- The assigned **A-Maze-ing** package documentation (constructor, `maze`
  attribute, wall encoding).
- Python standard library: `json`, `random`, `time`, `typing`.
- Third-party libraries: pydantic (config validation), pygame (audio).

### Use of AI

AI was used as an assistant, always under our review and understanding — never
as a substitute for it. Concretely, AI helped with:

- **Architecture discussion**: exploring how to structure modes, the game loop
  and the input layer before writing code.
- **Boilerplate and scaffolding**: generating first drafts of repetitive
  modules (renderer helpers, config models, menu screens) that we then read,
  adapted and integrated ourselves.
- **Debugging**: investigating platform-specific MLX quirks (image rendering,
  key handling), the ghost/Pac-Man collision alignment with interpolation, and
  configuration edge cases.
- **Documentation**: drafting parts of this README and inline comments.

Every piece of AI-assisted code was reviewed, tested, and cross-checked between
the two of us so that we can fully explain and defend it.

## Configuration

The game is driven by a JSON file (`config.json`) that also supports comments
(`#`, `//`, `/* */`). It contains one `global` section and one section per mode.
Values are validated through **pydantic** models (`src/models.py`), which supply
safe defaults for any missing key and log what falls back to a default. Unknown
keys are ignored, and a malformed configuration never crashes the game.

Common per-mode keys: `level`, `width`, `height`, `lives`,
`points_per_pacgum`, `points_per_super_pacgum`, `points_per_ghost`, `seed`,
`max_level_time`, `ghost_speed`, `pac_speed`, `power_duration`,
`ghost_respawn_delay`, `mega_spawn_chance`, `mega_score_multiplier`.

Mode-specific keys: the Shadow section adds the flashlight parameters
(`flashlight_radius`, `flashlight_radius_min/max`, `flashlight_reduction_time`,
`flashlight_reduction_step`, `flashlight_augmentation_step`, `shine_duration`);
the Hardcore section adds `hardcore_lives`, `time_factor`, `no_super_pacgums`;
the 2-player section adds `control_switch_time_range`.

Defaults are chosen so the game behaves identically whether or not a key is
present, and every value can be changed from the file without touching the code.

## Highscore

The high-score system is **persistent** and stored in a single JSON file, keyed
by mode: `{ "Normal": [["name", score], ...], "Hardcore": [...], ... }`.

- A **top 10 per mode** is kept, with player names and scores.
- Scores are loaded at startup and saved at the end of each game.
- At the end of a game (win or loss), if the score qualifies, the player is
  prompted to enter a name (max 10 characters, alphanumeric and spaces only);
  scores are stored as non-negative integers.
- The main menu shows the scoreboards, one page per mode (the 2-player page
  displays the Versus / Coop / Random tables side by side).

**Why this design.** Each mode is treated as its own leaderboard, so a score's
value is read from *which* table it appears in rather than from an artificial
multiplier — the scoring stays identical across modes. A single JSON file keyed
by mode keeps loading, saving and error handling simple: a missing, unreadable
or corrupted file falls back cleanly to empty tables, and every entry is
sanitised on load (name filtering, integer coercion, sorting, truncation to 10).

## Maze Generation

Mazes are **not** generated by us: we use the assigned A-Maze-ing package as-is,
through a thin adapter (`src/maze_loader.py`). Key points our loader handles:

- The generator is called with **keyword arguments** (`size`, `perfect=False`,
  `seed=...`) to be robust to constructor argument order.
- The maze is a grid of cells with **walls encoded as bits** per cell
  (N=1, E=2, S=4, W=8); a set bit means a wall on that side.
- The grid is indexed **`maze[y][x]`**, while entry/exit are returned as
  **`(x, y)`** tuples — our loader keeps the two conventions straight.
- `perfect=False` produces braided mazes (no dead ends), suitable for Pac-Man.
- **Seed policy** (per the subject): the **first level** uses a fixed seed from
  the config; **subsequent levels** use a random seed. Because the generator
  seeds Python's global RNG for reproducibility, the loader calls `random.seed()`
  right after generation to restore non-deterministic randomness for the rest of
  the game (mega placement, ghost AI, etc.).

## Implementation

- **Rendering** uses an MLX image: the full-screen frame is drawn into an
  in-memory buffer (walls, pacgums, entities) and blitted in one call, with the
  HUD drawn on top via `mlx_string_put`. The maze template is precomputed for
  normal mode; in Shadow mode, walls and items are drawn dynamically and clipped
  to the light zone.
- **Game loop**: the app runs a continuous loop that advances Pac-Man and the
  ghosts on their own cadences and renders at ~60 fps. Positions are
  **interpolated** between cells for smooth motion, and **collisions are computed
  on the displayed (interpolated) positions** so that contact matches what the
  player sees.
- **State**: `GameSession` owns a single level (Pac-Man, pacgums, super-pacgums,
  ghosts, score, lives, timer, power/mega state). `App` orchestrates progression
  across levels, menus, pause and end screens, and applies each mode's rules.
- **Modes** live in dedicated files so each is self-contained and easy to tune.
- **Config** is parsed and validated once at startup; **audio** is handled by
  pygame and degrades silently if unavailable.

## General Software Architecture

High-level overview of the modules under `src/`:

- `__main__.py` — entry point (`python3 -m src config.json`).
- `app.py` — central orchestrator: game states (intro, menus, playing, paused),
  the main loop, input routing, and level progression.
- `game_session.py` — state and rules of a single level (entities, collisions,
  scoring, timer, power/mega/roguelite effects).
- `entities.py` — `Entity` base class with `PacMan` and `Ghost` (movement, AI).
- `maze_loader.py` / `maze_renderer.py` — maze adapter and rendering.
- `menu_manager.py` — all menus (main, mode selection, high scores,
  instructions).
- `intro.py` — intro cinematic. `audio.py` — music and sound effects.
- `highscore.py` — persistent per-mode scoreboards.
- `config_parser.py` + `models.py` — configuration loading and pydantic models.
- `utils.py` — constants, colors, key codes, helpers.
- `mode_shadow.py`, `mode_hardcore.py`, `mode_2players.py`,
  `mode_roguelite.py`, `mega_pacgum.py` — mode-specific logic and tunables.

`App` depends on all the subsystems and wires them together; `GameSession`
stays mode-agnostic and is parameterised by the active rule set, while the
`mode_*` modules plug their behaviour in through `App` and the session.

## Cheat mode

A cheat mode is available to help the evaluator test the game. During a game,
entering the **Konami code** (↑ ↑ ↓ ↓ ← → ← → A B) toggles it; then `I` grants
invincibility (god mode) and `N` skips to the next level. Runs played with the
cheat mode are not meant for the leaderboard.

## Project Management

We managed the project incrementally: a solid faithful base first, then each
mode added and validated one at a time, with regular peer review between the two
of us and continuous testing after every feature. Task ownership, planning,
progress tracking and acceptance tests are documented in the dedicated
project-management directory.

➡️ See [`project-management/`](./project-management/) for the planning, task
distribution, risk analysis and acceptance-test notes.

### Authors

- **ssayada** (Sébastien)
- **rapoggi** (Raphaël)
