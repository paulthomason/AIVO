"""Entry point for the diagnosis UI."""


from tkinter import Tk
import argparse
from ui import DiagnosisUI


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the diagnosis UI")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()

    root = Tk()
    DiagnosisUI(root, debug=args.debug)
    root.mainloop()


if __name__ == "__main__":
    main()
