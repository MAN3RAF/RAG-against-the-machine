import sys
import fire
from .cli import Cli


def main() -> int:
    try:
        fire.Fire(Cli)

    except (ValueError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
    except KeyboardInterrupt as e:
        print(e)


if __name__ == "__main__":
    raise SystemExit(main())
