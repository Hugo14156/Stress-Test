"""
Stress Test - A 2D train logistics game.

Entry point for the application. Run with no arguments for local singleplayer.

  python main.py              # singleplayer
  python main.py --host       # headless server (LAN host)
  python main.py --join IP    # connect to a server at the given IP address
"""

import argparse
import runpy
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stress Test — Train logistics game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--host",
        action="store_true",
        help="Run a headless authoritative server on this machine (LAN host)",
    )
    group.add_argument(
        "--join",
        metavar="IP",
        help="Connect to a server running at the given IP address",
    )
    args = parser.parse_args()

    if args.host:
        runpy.run_module("app.networking.server", run_name="__main__", alter_sys=True)
    elif args.join:
        import os
        os.environ["STRESS_TEST_SERVER_IP"] = args.join
        runpy.run_module("app.networking.client", run_name="__main__", alter_sys=True)
    else:
        from app.game import Game
        game = Game()
        game.run_game()


if __name__ == "__main__":
    main()
