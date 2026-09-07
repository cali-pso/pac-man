import argparse
import sys
from src.app import App
from src.utils import WIDTH, HEIGHT


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            prog="pac-man", description="Waka-Waka!"
        )
        parser.add_argument("config_filename")
        args = parser.parse_args()
        app = App(WIDTH, HEIGHT, "pac-man", args.config_filename)
        app.run()
    except Exception as e:
        print(f"An error occured: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
