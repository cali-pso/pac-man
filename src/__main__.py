
from src.app import App

WIDTH: int = 800
HEIGHT: int = 600

def main() -> None:
    app = App(WIDTH, HEIGHT, "Pacman - test MLX")
    app.run()


if __name__ == "__main__":
    main()