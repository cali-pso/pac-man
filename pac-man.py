import sys
import subprocess


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        subprocess.run(
            ["uv", "run", "python", "-m", "src", config_file], check=True
        )
    except FileNotFoundError:
        print("Error: 'uv' package manager is not installed or not in PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
