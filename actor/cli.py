import argparse
import json
import uuid
from actor.harness import Harness
import actor.system.objects


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bootstrap a Python actor framework program"
    )
    parser.add_argument("-a", "--actor", help="actor to load.", required=True)
    parser.add_argument("-rp", "--r_pid", help="pid of spawning process.")
    parser.add_argument("-np", "--n_pid", help="pid of the spawned process")
    parser.add_argument(
        "-l",
        "--log_level",
        help="log level of logging",
        choices=["info", "debug", "error"],
        default="info",
    )
    parser.add_argument(
        "-lf", "--log_file", help="log file location", default="/var/log/pyactor/"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    pkg = ".".join(args.actor.split(".")[:-1])
    act = args.actor.split(".")[-1]
    if not args.n_pid:
        pid = actor.system.objects.Pid(int=uuid.uuid4().int)
    else:
        pid = actor.system.objects.Pid(args.n_pid)
    harness = Harness(pid, args.log_level, args.log_file)
    harness.launch_actor(pkg, act)
