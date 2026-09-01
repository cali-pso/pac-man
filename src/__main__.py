from mlx import Mlx
from src.menu_manager import MenuManager

def key_hook(keycode: int, manager: MenuManager) -> None:
    manager.handle_key(keycode)

def main() -> None:
    mlx = Mlx()
    mlx_ptr = mlx.mlx_init()
    win_ptr = mlx.mlx_new_window(mlx_ptr, 440, 320, "Pac-Man")

    manager = MenuManager(mlx, mlx_ptr, win_ptr)
    manager.render()

    mlx.mlx_key_hook(win_ptr, key_hook, manager)
    mlx.mlx_loop(mlx_ptr)

if __name__ == "__main__":
    main()
