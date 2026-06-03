import argparse
import json
import sys

from . import parse_project_file


def main():
    parser = argparse.ArgumentParser(
        description="Parse an Avidemux TinyPY project file to JSON."
    )
    parser.add_argument("input", help="Path to the Avidemux project file (.py)")
    parser.add_argument(
        "-o", "--output",
        help="Path to write JSON output (default: stdout)",
    )
    args = parser.parse_args()

    try:
        project = parse_project_file(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(project.to_dict(), indent=4)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
