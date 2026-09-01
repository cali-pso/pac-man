from typing import Any

from mlx import Mlx
from src.app import App



# Keycode d'Echap (keysym X11). Si Echap ne ferme pas, decommente le print
# dans on_key pour lire le vrai code, puis remplace cette valeur.
KEY_ESCAPE: int = 65307

# Evenement "fermeture de la fenetre" (DestroyNotify sous X11).
EVENT_DESTROY: int = 17

# Couleurs au format 0xRRGGBB
COLOR_GRID: int = 0x303048
COLOR_TEXT: int = 0xFFFFFF





def main() -> None:
    app = App(WIDTH, HEIGHT, "Pacman - test MLX")
    app.run()


if __name__ == "__main__":
    main()