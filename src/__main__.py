from src.app import App
from src.utils import WIDTH, HEIGHT


def main() -> None:
     app = App(WIDTH, HEIGHT, "Pacman - test MLX")
     app.run()


if __name__ == "__main__":
    main()
