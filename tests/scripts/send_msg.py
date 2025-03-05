from actor.utils import *
import sys


def main():
    load_env()
    # pid = utils.spawn('actor.actors.Actor')
    print(sys.argv[1])
    data = sync_msg(
        sys.argv[1], {"msg_type": RCE_MSG, "method": "sync_msg"}, fifo_dir="/tmp/"
    )
    print(data)


if __name__ == "__main__":
    main()
