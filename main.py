"""Entry point for the diagnosis UI."""


from tkinter import Tk, TclError
import sys
import os
import argparse
from ui import DiagnosisUI


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the diagnosis UI")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()

    if os.name != "nt" and not os.getenv("DISPLAY"):
        sys.exit("Error: no DISPLAY environment variable set")
    try:
        root = Tk()
    except TclError as exc:
        sys.exit(f"Error initializing Tkinter: {exc}")

    DiagnosisUI(root, debug=args.debug)
    root.mainloop()


if __name__ == "__main__":
    main()
