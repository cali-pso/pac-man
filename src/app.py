import random
import time
import traceback
from typing import Any, Optional, Tuple
from collections import deque
from mlx import Mlx
from src.menu_manager import MenuManager
from src.intro import IntroScene
from src.audio import AudioManager
from src.config_parser import ConfigParser
from src.maze_loader import MazeLoader
from src.maze_renderer import MazeRenderer
from src.game_session import GameSession
from src.highscore import HighscoreStore
from src.mode_shadow import ShadowMode
from src import mode_hardcore
from src import mega_pacgum
from src.utils import GameState, Key, center_x_str
from src import mode_2players
from src import mode_roguelite

GHOST_INTERVAL: float = 0.38  # cadence des fantomes
HOLD_GRACE: float = 0.15  # delai sans repetition avant de considerer relache
STEP_INTERVAL: float = 0.21  # cadence min entre 2 cases (vitesse de Pac-Man)
FRAME_INTERVAL: float = 0.016  # rendu continu (~60 fps) pour le lissage
PAUSE_OPTIONS = ["Continue", "Quit"]
BACKSPACE: int = 65288


class App:
    def __init__(
        self, width: int, height: int, title: str, config_filename: str
    ) -> None:
        self.width = width
        self.height = height
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.width, self.height, title
        )
        self.audio = AudioManager()
        self.music_tracks = {
            "Normal": "normal_mode.mp3",
            "Hardcore": "hardcore_mode.mp3",
            "Shadow": "shadow_mode.mp3",
            "Roguelite": "roguelite_mode.mp3",
        }
        config_parser = ConfigParser()
        self.rulesets = config_parser.load_config(config_filename)
        self.highscores = HighscoreStore("highscores.json")
        self.state = GameState.INTRO
        self.intro = IntroScene(self.mlx, self.mlx_ptr, self.win_ptr)
        self.menu = MenuManager(
            self.mlx, self.mlx_ptr, self.win_ptr, self.state, self.highscores
        )
        self.maze_loader = MazeLoader()
        self.maze_renderer = MazeRenderer(
            self.mlx, self.mlx_ptr, self.win_ptr, self.width, self.height
        )

        self.session: Optional[GameSession] = None
        self.shadow: Optional[ShadowMode] = None
        self._last_ghost: float = 0.0
        self._finish_handled: bool = False
        self._entering_name: bool = False
        self._name_buffer: str = ""
        self._current_mode: str = "Normal"
        self._level: int = 1
        self._total_levels: int = 1
        # Deplacement Pac-Man
        self._move_dir: Tuple[int, int] = (0, 0)
        self._next_dir: Tuple[int, int] = (0, 0)
        self._active_player: int = 1
        self._next_switch: float = 0.0
        self._switch_min: float = mode_2players.SWITCH_MIN
        self._switch_max: float = mode_2players.SWITCH_MAX
        self._last_step: float = 0.0
        self._ghost_speed: float = GHOST_INTERVAL
        self._pac_speed: float = STEP_INTERVAL
        self._base_ghost_speed: float = GHOST_INTERVAL
        self._base_pac_speed: float = STEP_INTERVAL
        self._last_frame: float = 0.0
        # Roguelite
        self._run = None
        self._roguelite = None
        self._choosing: bool = False
        self._choices: list = []
        self._choice_index: int = 0
        self._temp_msg: str = ""
        self._temp_msg_until: float = 0.0
        self._temp_msg_color: int = 0xFFFFFF
        self._pause_index: int = 0
        self.konami_sequence = [
            Key.UP,
            Key.UP,
            Key.DOWN,
            Key.DOWN,
            Key.LEFT,
            Key.RIGHT,
            Key.LEFT,
            Key.RIGHT,
            98,
            Key.Ab,  # 'b' is 98, Key.Ab is 97
        ]
        # Initialize the sliding window
        self.input_buffer = deque(maxlen=len(self.konami_sequence))

    # --- Transitions -------------------------------------------------------

    def _reset_move(self) -> None:
        """Stoppe le deplacement de Pac-Man (direction et buffer a zero)."""
        self._move_dir = (0, 0)
        self._next_dir = (0, 0)

    def _go_to_menu(self) -> None:
        self.audio.stop_music()
        self.audio.play_music("menu.mp3")
        self.session = None
        self._entering_name = False
        self._name_buffer = ""
        self.state = GameState.MAIN_MENU
        self.menu.state = GameState.MAIN_MENU
        self.menu.selected_index = 0
        self.menu.render()

    def _ruleset_key(self, mode: str) -> str:
        """Les sous-modes 2 joueurs partagent le ruleset '2 Players'."""
        if mode in ("Versus", "Coop", "Random"):
            return "2 Players"
        return mode

    def _start_game(self, mode: str) -> None:
        self.mode = mode
        self.audio.stop_music()
        track = self.music_tracks.get(mode, "normal_mode.mp3")
        self.audio.play_music(track)
        self._current_mode = mode
        try:
            ruleset = self.rulesets[self._ruleset_key(mode)]
            self._ghost_speed = ruleset.ghost_speed
            self._pac_speed = ruleset.pac_speed
            self._base_ghost_speed = ruleset.ghost_speed
            self._base_pac_speed = ruleset.pac_speed
            maze = self.maze_loader.load(
                (ruleset.width, ruleset.height), ruleset.seed
            )
            self._level = 1
            self._total_levels = max(1, int(getattr(ruleset, "level", 10)))
            self.session = GameSession(maze, **self._session_kwargs(ruleset))
            self.session.level = self._level
            self.session.mode = self._current_mode
            self._attach_mode()
            self._init_random()
            self._init_roguelite(ruleset)
            self._apply_run(self.session)
            if self.session.mega_pos is not None:
                self.audio.play_sound("mega_alert.wav")
            self._finish_handled = False
            self._entering_name = False
            self._name_buffer = ""
            self.maze_renderer.prepare(maze)
            self._render_game()
            self._last_ghost = time.time()
        except Exception as exc:
            print("[start_game] ECHEC:", repr(exc))
            traceback.print_exc()
            self.session = None
            self._go_to_menu()  # on ne reste pas bloque en PLAYING sans partie

    def _session_kwargs(self, ruleset) -> dict:
        """Parametres de GameSession pour le mode courant (presets inclus)."""
        kw = dict(
            points_per_pacgum=ruleset.points_per_pacgum,
            points_per_super_pacgum=ruleset.points_per_super_pacgum,
            points_per_ghost=ruleset.points_per_ghost,
            lives=ruleset.lives,
            max_time=ruleset.max_level_time,
            mode=self._current_mode,
            power_duration=ruleset.power_duration,
            ghost_respawn_delay=ruleset.ghost_respawn_delay,
            mega_spawn_chance=ruleset.mega_spawn_chance,
            mega_score_multiplier=ruleset.mega_score_multiplier,
        )
        if self._current_mode == "Hardcore":
            kw = mode_hardcore.apply_to_ruleset_kwargs(kw, ruleset)
            kw["no_supers"] = mode_hardcore.no_supers_for(ruleset)
        return kw

    def _attach_mode(self) -> None:
        """Cree le controleur du mode choisi et l'attache a la session."""
        if self._current_mode == "Shadow":
            rs = self.rulesets.get("Shadow")
            self.shadow = ShadowMode(
                radius_start=getattr(rs, "flashlight_radius", 3.5),
                radius_min=getattr(rs, "flashlight_radius_min", 2.0),
                radius_max=getattr(rs, "flashlight_radius_max", 8.0),
                pacgum_gain=getattr(rs, "flashlight_augmentation_step", 0.5),
                decay_interval=getattr(rs, "flashlight_reduction_time", 1.0),
                decay_step=getattr(rs, "flashlight_reduction_step", 1.1),
                shine_duration=getattr(rs, "shine_duration", 8.0),
            )
        else:
            self.shadow = None
        if self.session is not None:
            self.session.shadow = self.shadow

    # --- Progression de niveau --------------------------------------------

    def _next_level(self) -> None:
        self._level += 1
        ruleset = self.rulesets[self._ruleset_key(self._current_mode)]
        self._ghost_speed = ruleset.ghost_speed
        self._pac_speed = ruleset.pac_speed
        self._base_ghost_speed = ruleset.ghost_speed
        self._base_pac_speed = ruleset.pac_speed
        seed = random.randint(1, 2_000_000_000)  # niveaux 2+ : aleatoire
        maze = self.maze_loader.load((ruleset.width, ruleset.height), seed)
        kw = self._session_kwargs(ruleset)
        kw["lives"] = self.session.lives  # on garde les vies
        if self._run is not None:
            kw["lives"] = self._run.lives  # roguelite : vies de la run
        kw["start_score"] = self.session.score  # on garde le score
        cheat = self.session.cheat
        self.session = GameSession(maze, **kw)
        self.session.cheat = cheat
        self.session.level = self._level
        self.session.mode = self._current_mode
        self._attach_mode()
        self._init_random()
        self._apply_run(self.session)
        self._finish_handled = False
        self._entering_name = False
        self._name_buffer = ""
        if self.session.mega_pos is not None:
            self.audio.play_sound("mega_alert.wav")
        self.maze_renderer.prepare(maze)
        self._last_ghost = time.time()
        self._render_game()

    def _progress(self) -> None:
        s = self.session
        if s is None or self._choosing:
            return
        if s.won and self._level < self._total_levels:
            if self._current_mode == "Roguelite":
                self._enter_choice()
            else:
                self._next_level()
            return
        if s.won or s.game_over:
            self._on_finish()
        self._render_game()

    # --- Fin de partie -----------------------------------------------------

    def _on_finish(self) -> None:
        if self._finish_handled or self.session is None:
            return
        self._finish_handled = True
        self.audio.stop_music()
        self.audio.stop_eating_loop()
        if self.session.game_over:
            self.audio.play_sound("death.wav")
        self._entering_name = self.highscores.qualifies(
            self._current_mode, self.session.score
        )
        self._name_buffer = ""

    # --- Rendu -------------------------------------------------------------

    def _put_center(self, text: str, y: int, color: int) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, center_x_str(text), y, color, text
        )

    def _render_game(self) -> None:
        if self._choosing:
            self._render_choice()
            return
        if self.session is None:
            return
        if self.session.won or self.session.game_over:
            self._render_finish()
            return

        now = time.time()
        pac_prog = max(
            0.0, min(1.0, (now - self._last_step) / self._pac_speed)
        )
        ghost_prog = max(
            0.0, min(1.0, (now - self._last_ghost) / self._ghost_speed)
        )

        self.maze_renderer.render(self.session, pac_prog, ghost_prog)
        if time.time() < self._temp_msg_until:
            self._put_center(self._temp_msg, 54, self._temp_msg_color)
            try:
                self.mlx.mlx_do_sync(self.mlx_ptr)
            except Exception:
                pass

    def _render_finish(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        s = self.session
        cy = self.height // 2
        if self._entering_name:
            self._put_center("NEW HIGHSCORE!", cy - 60, 0xFFFF00)
            self._put_center(f"Score: {s.score}", cy - 30, 0xFFFFFF)
            self._put_center(f"Name: {self._name_buffer}_", cy, 0x00FFFF)
            self._put_center(
                "Type your name  -  ENTER to confirm  -  ESC to skip",
                cy + 40,
                0x888888,
            )
        else:
            if s.won:
                self._put_center(
                    f"YOU WIN!  Score: {s.score}", cy - 10, 0xFFFF00
                )
            else:
                self._put_center(
                    f"GAME OVER  Score: {s.score}", cy - 10, 0xFF4444
                )
            self._put_center("Press ESC to return to menu", cy + 20, 0x888888)
        try:
            self.mlx.mlx_do_sync(self.mlx_ptr)
        except Exception:
            pass

    def _finished(self) -> bool:
        return self.session is not None and (
            self.session.won or self.session.game_over
        )

    # --- Deplacement Pac-Man ----------------------------------------------

    def _init_random(self) -> None:
        self._active_player = 1
        if self.session is not None:
            self.session.active_player = 1
        if self._current_mode == "Random":
            rs = self.rulesets.get("2 Players")
            rng = getattr(rs, "control_switch_time_range", None) or (
                mode_2players.SWITCH_MIN,
                mode_2players.SWITCH_MAX,
            )
            self._switch_min = float(rng[0])
            self._switch_max = float(rng[1])
            self._next_switch = time.time() + random.uniform(
                self._switch_min, self._switch_max
            )
        else:
            self._next_switch = 0.0
        if self._current_mode == "Versus" and self.session is not None:
            idx = (self._level - 1) % len(self.session.ghosts)
            self.session.set_player_ghost(idx)

    def _pac_dir_for(self, keycode: int):
        """Direction de Pac-Man selon le sous-mode 2 joueurs."""
        if self._current_mode == "Coop":
            return mode_2players.coop_dir(keycode)
        if self._current_mode == "Random":
            return mode_2players.player_dir(keycode, self._active_player)
        if self._current_mode == "Versus":
            return mode_2players.player_dir(keycode, 1)  # J1 = WASD
        return self._dir_for(keycode)

    @staticmethod
    def _dir_for(keycode: int) -> Optional[Tuple[int, int]]:
        if keycode in (Key.UP, Key.Wb):
            return (0, -1)
        if keycode in (Key.DOWN, Key.Sb):
            return (0, 1)
        if keycode in (Key.LEFT, Key.Ab):
            return (-1, 0)
        if keycode in (Key.RIGHT, Key.Db):
            return (1, 0)
        return None

    def _step_pac(self) -> None:
        if self.session is None or self._finished():
            return
        self.session.pacman.prev_x = self.session.pacman.x
        self.session.pacman.prev_y = self.session.pacman.y
        next_dir = self._next_dir
        moved = False
        if next_dir != (0, 0) and self.session.try_move(
            next_dir[0], next_dir[1]
        ):
            self._move_dir = next_dir
            moved = True
        elif self._move_dir != (0, 0) and self.session.try_move(
            self._move_dir[0], self._move_dir[1]
        ):
            moved = True
        if moved:
            if self.session.last_ate_mega:
                self.audio.stop_eating_loop()  # Stop normal eating loop
                self.audio.play_sound("mega_pickup.wav")
                self.audio.stop_music()
                self.audio.play_music("mega_active.wav")
            elif self.session.last_ate:
                self.audio.play_eating_loop("pacgum.wav")  # Trigger the loop
                if self.shadow is not None:
                    self.shadow.on_pacgum()
            elif self.session.last_ate_super:
                self.audio.play_sound("mega_pickup.wav")
                if self.shadow is not None:
                    self.shadow.on_shine()
                if self._current_mode == "Roguelite":
                    eff = mode_roguelite.random_temp_effect()
                    self._apply_temp_effect(eff["spec"])
                    is_bonus = eff["kind"] == "bonus"
                    self.audio.play_sound(
                        "roguelite_bonus.wav"
                        if is_bonus
                        else "roguelite_malus.wav"
                    )
                    tag = "BONUS" if is_bonus else "MALUS"
                    self._temp_msg = f"{tag}: {eff['label']}"
                    self._temp_msg_color = 0x00DD00 if is_bonus else 0xFF6600
                    self._temp_msg_until = time.time() + 2.5
            else:
                self.audio.stop_eating_loop()  # Stop if moving but empty cell
            self._progress()
        else:
            self.audio.stop_eating_loop()  # Stop if hitting a wall
            self._progress()

    # --- Entrees -----------------------------------------------------------

    def _handle_name_key(self, keycode: int) -> None:
        if keycode == Key.ENTER:
            if self.session is not None:
                self.highscores.add(
                    self._current_mode, self._name_buffer, self.session.score
                )
            self._go_to_menu()
        elif keycode == Key.ESC:
            self._go_to_menu()
        elif keycode == BACKSPACE:
            self._name_buffer = self._name_buffer[:-1]
            self._render_finish()
        elif 32 <= keycode <= 126:
            ch = chr(keycode)
            if (ch.isalnum() or ch == " ") and len(self._name_buffer) < 10:
                self._name_buffer += ch
                self._render_finish()

    def _init_roguelite(self, ruleset: object) -> None:
        if self._current_mode == "Roguelite":
            self._run = mode_roguelite.RunState(ruleset.lives)
            self._roguelite = mode_roguelite.RogueliteEngine()
        else:
            self._run = None
            self._roguelite = None
        self._choosing = False
        self._choices = []
        self._choice_index = 0

    def _apply_run(self, session: object) -> None:
        run = self._run
        if run is None or session is None:
            return
        self._pac_speed = self._base_pac_speed * run.pac_speed_factor
        self._ghost_speed = self._base_ghost_speed * run.ghost_speed_factor
        session.power_duration *= run.power_duration_factor
        session.run_score_multiplier = run.score_multiplier
        session.magnet_range = run.magnet_range
        session.shield_count = run.shields
        session.max_time = max(10, session.max_time + run.time_bonus)
        session.set_start_freeze(run.next_freeze_ghosts, run.next_freeze_pac)
        run.next_freeze_ghosts = 0.0
        run.next_freeze_pac = 0.0

    def _apply_temp_effect(self, spec: dict) -> None:
        """Applique un effet directement sur la partie en cours (super-pacgum
        roguelite). Non memorise dans la run -> disparait au niveau suivant."""
        s = self.session
        if s is None:
            return
        field, op, val = spec["field"], spec["op"], spec["value"]
        if field == "pac_speed_factor" and op == "mul":
            self._pac_speed *= val
        elif field == "ghost_speed_factor" and op == "mul":
            self._ghost_speed *= val
        elif field == "lives":
            s.lives = max(1, s.lives + val)
        elif field == "power_duration_factor" and op == "mul":
            s.power_duration *= val
        elif field == "score_multiplier" and op == "mul":
            s.run_score_multiplier *= val
        elif field == "magnet_range":
            s.magnet_range = max(0, s.magnet_range + val)
        elif field == "shields":
            s.shield_count = max(0, s.shield_count + val)
        elif field == "time_bonus":
            s.max_time = max(10, s.max_time + val)
        elif field == "next_freeze_ghosts":
            s.set_start_freeze(val, 0)
        elif field == "next_freeze_pac":
            s.set_start_freeze(0, val)

    def _enter_choice(self) -> None:
        if self._run is None or self._roguelite is None:
            self._next_level()
            return
        self._run.lives = self.session.lives
        self._run.shields = self.session.shield_count
        self._choices = self._roguelite.draw(self._run)
        self._choice_index = 0
        self._choosing = True
        self._reset_move()
        self._render_choice()

    def _render_choice(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        cy = self.height // 2
        self._put_center("LEVEL CLEARED - CHOOSE A CARD", cy - 90, 0xFFFF00)
        for i, ch in enumerate(self._choices):
            selected = i == self._choice_index
            prefix = "> " if selected else "  "
            if ch.get("hidden"):
                color = 0xFFFFFF if selected else 0xAAAAAA
                text = prefix + "[ ??? ]  ???"
            else:
                if ch["kind"] == "bonus":
                    base, tag = 0x00DD00, "[BONUS] "
                else:
                    base, tag = 0xFF4444, "[MALUS] "
                color = 0xFFFFFF if selected else base
                text = prefix + tag + ch["label"]
            self._put_center(text, cy - 40 + i * 30, color)
        self._put_center("Up/Down + ENTER to choose", cy + 90, 0x888888)
        try:
            self.mlx.mlx_do_sync(self.mlx_ptr)
        except Exception:
            pass

    def _handle_choice_key(self, keycode: int) -> None:
        if keycode in (Key.UP, Key.Wb):
            self._choice_index = (self._choice_index - 1) % len(self._choices)
            self._render_choice()
        elif keycode in (Key.DOWN, Key.Sb):
            self._choice_index = (self._choice_index + 1) % len(self._choices)
            self._render_choice()
        elif keycode in (Key.ENTER, Key.SPACE):
            self._roguelite.apply(self._run, self._choices[self._choice_index])
            self._choosing = False
            self._next_level()

    def _handle_play_key(self, keycode: int) -> None:
        if self._choosing:
            self._handle_choice_key(keycode)
            return
        self.input_buffer.append(keycode)

        if list(self.input_buffer) == self.konami_sequence:
            self.session.cheat = not self.session.cheat
            if self.session.cheat is False:
                self.session.invicible = False
            self.input_buffer.clear()
        if self._entering_name:
            self._handle_name_key(keycode)
            return
        if self._finished():
            if keycode == Key.ESC:
                self._go_to_menu()
            return
        if keycode == Key.ESC:
            self._enter_pause()
            return
        elif keycode == Key.Ib and self.session.cheat:
            self.session.invicible = not self.session.invicible
        elif keycode == Key.Nb and self.session.cheat:
            self._skip_level()
        if self.session is None:
            return
        if self._current_mode == "Versus":
            gd = mode_2players.player_dir(
                keycode, 2
            )  # J2 = fleches -> fantome
            if gd is not None:
                self.session.set_ghost_direction(*gd)
                return
        d = self._pac_dir_for(keycode)
        if d is not None:
            self._next_dir = d

    def _skip_level(self) -> None:
        self.session.won = True
        self._progress()

    # --- Pause -------------------------------------------------------------

    def _enter_pause(self) -> None:
        if self.session is None:
            return
        self.session.pause()
        self.audio.stop_eating_loop()
        self._pause_index = 0
        self.state = GameState.PAUSED
        self._render_pause()

    def _resume_game(self) -> None:
        if self.session is None:
            self._go_to_menu()
            return
        self.session.resume()
        self.state = GameState.PLAYING
        self._render_game()

    def _render_pause(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        cy = self.height // 2
        self._put_center("PAUSED", cy - 60, 0xFFFF00)
        for i, opt in enumerate(PAUSE_OPTIONS):
            selected = i == self._pause_index
            color = 0xFFFF00 if selected else 0xFFFFFF
            prefix = "> " if selected else "  "
            self._put_center(f"{prefix}{opt}", cy - 10 + i * 30, color)
        self._put_center(
            "Up/Down + ENTER  -  ESC to resume", cy + 70, 0x888888
        )
        # Roguelite : effets actifs de la run
        if self._current_mode == "Roguelite" and self._run is not None:
            self._put_center("--- Active effects ---", cy + 110, 0x00FFFF)
            for i, line in enumerate(self._run.summary()):
                self._put_center(line, cy + 134 + i * 20, 0xFFFFFF)
        try:
            self.mlx.mlx_do_sync(self.mlx_ptr)
        except Exception:
            pass

    def _handle_pause_key(self, keycode: int) -> None:
        if keycode in (Key.UP, Key.Wb):
            self._pause_index = (self._pause_index - 1) % len(PAUSE_OPTIONS)
            self._render_pause()
        elif keycode in (Key.DOWN, Key.Sb):
            self._pause_index = (self._pause_index + 1) % len(PAUSE_OPTIONS)
            self._render_pause()
        elif keycode in (Key.ENTER, Key.SPACE):
            if PAUSE_OPTIONS[self._pause_index] == "Continue":
                self._resume_game()
            else:
                self._go_to_menu()
        elif keycode == Key.ESC:
            self._resume_game()

    # --- Hooks -------------------------------------------------------------

    def _key_hook(self, keycode: int, param: Any = None) -> int:
        if self.state == GameState.INTRO:
            self.intro.skip()
            self._go_to_menu()
            return 0
        elif self.state == GameState.PLAYING:
            self._handle_play_key(keycode)
            return 0
        elif self.state == GameState.PAUSED:
            self._handle_pause_key(keycode)
            return 0
        prev = self.state
        self.menu.handle_key(keycode, self.state)
        self.state = self.menu.state
        if prev != GameState.PLAYING and self.state == GameState.PLAYING:
            self._start_game(self.menu.chosen_mode)
        return 0

    def _resolve_visual_collisions(self, now: float) -> None:
        """Verifie la collision fantome/Pac-Man sur les positions AFFICHEES."""
        s = self.session
        if s is None or self._finished():
            return
        pac_prog = max(
            0.0, min(1.0, (now - self._last_step) / self._pac_speed)
        )
        ghost_prog = max(
            0.0, min(1.0, (now - self._last_ghost) / self._ghost_speed)
        )
        pm = s.pacman
        pfx = pm.prev_x + (pm.x - pm.prev_x) * pac_prog
        pfy = pm.prev_y + (pm.y - pm.prev_y) * pac_prog
        if s.resolve_collisions(pfx, pfy, ghost_prog):
            self._reset_move()  # Pac-Man est mort : on stoppe le mouvement

    def _loop_hook(self, *args: Any) -> int:
        if self.state == GameState.INTRO:
            if self.intro.update():
                self._go_to_menu()
            return 0
        if (
            self.state == GameState.PLAYING
            and self.session is not None
            and not self._finished()
        ):
            now = time.time()
            if self._current_mode == "Random" and now >= self._next_switch:
                self._active_player = 2 if self._active_player == 1 else 1
                self.session.active_player = self._active_player
                self._next_switch = now + random.uniform(
                    self._switch_min, self._switch_max
                )
                self._reset_move()
            # Pac-Man en maintien : avance a SA cadence tant que ca repete
            if now - self._last_step >= self._pac_speed:
                self._last_step = now
                self._step_pac()
            if self.shadow is not None:
                self.shadow.update()
            # Fin du mode POWERED
            if self.session is not None and not self._finished():
                self.session.update_power()
            # Fantomes
            if (
                self.session is not None
                and not self._finished()
                and now - self._last_ghost >= self._ghost_speed
            ):
                self._last_ghost = now
                self.session.check_timeout()
                if not self.session.game_over:
                    self.session.update_ghosts()
                self._progress()
            # Collision visuelle + rendu continu (lissage)
            if now - self._last_frame >= FRAME_INTERVAL:
                self._last_frame = now
                self._resolve_visual_collisions(now)
                if self._finished() and not self._choosing:
                    self._on_finish()
                self._render_game()
        return 0

    def run(self) -> None:
        self.audio.play_music("shadow_mode.mp3")
        self.intro.render()

        self.mlx.mlx_key_hook(self.win_ptr, self._key_hook, 0)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self._loop_hook, 0)

        self.mlx.mlx_loop(self.mlx_ptr)

        self.audio.stop_music()
        try:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        except Exception:
            pass
        try:
            self.mlx.mlx_release(self.mlx_ptr)
        except Exception:
            pass
