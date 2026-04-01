"""A-Maze-ing: maze generator entry point."""

import sys
from config_parser import parse_config


def main() -> None:
    """Main function of the project
    """
    if len(sys.argv) <= 1:
        print(f"[config error] missing file, Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        sys.exit(1)
    result = parse_config(sys.argv[1])
    print(f"{result}")


if __name__ == "__main__":
    main()
