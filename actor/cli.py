import argparse
import json
import uuid
from actor.harness import Harness


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bootstrap a Python actor framework program"
    )
    parser.add_argument("-a", "--actor", help="actor to load.", required=True)
    parser.add_argument("-rp", "--r_pid", help="pid of spawning process.")
    parser.add_argument("-np", "--n_pid", help="pid of the spawned process")
    return parser.parse_args()


def main():
    args = parse_args()
    pkg = ".".join(args.actor.split(".")[:-1])
    actor = args.actor.split(".")[-1]
    if not args.n_pid:
        pid = uuid.uuid4()
    else:
        pid = args.n_pid
    harness = Harness(pid)
    harness.launch_actor(pkg, actor)
