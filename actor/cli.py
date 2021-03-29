import argparse
import json
from actor.harness import Harness


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bootstrap a Python actor framework program"
    )
    parser.add_argument("-a", "--actor", help="actor to load.", required=True)
    parser.add_argument("-p", "--pid", help="pid of spawning process.")
    return parser.parse_args()


def main():
    args = parse_args()
    package = ".".join(args.actor.split(".")[:-1])
    actor = args.actor.split(".")[-1]
    harness = Harness()
    harness.launch_actor(pkg, actor)
