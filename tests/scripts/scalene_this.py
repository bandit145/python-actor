import actor.utils
import queue
import time

actor.utils.load_env(None, "DEBUG")


def main():
    msg_amnt = 1500
    pid1 = actor.utils.spawn("actor.actors.SpamActor", "debug")
    pid2 = actor.utils.spawn("actor.actors.SpamActor", "debug")
    pid3 = actor.utils.spawn("actor.actors.SpamActor", "debug")
    msgs_recvd = {pid1: 0, pid2: 0, pid3: 0}
    std_msg(data=dict(begin=True)) > pid1
    std_msg(data=dict(begin=True)) > pid2
    std_msg(data=dict(begin=True)) > pid3
    start = time.time()
    while sum([x for x in msgs_recvd.values()]) < msg_amnt:
        try:
            msg = MAILBOX.get(block=False)
            msgs_recvd[msg["r_pid"]] += 1
        except queue.Empty:
            pass
    assert sum([x for x in msgs_recvd.values()]) == msg_amnt
    assert msgs_recvd[pid1] == 500
    assert msgs_recvd[pid2] == 500
    assert msgs_recvd[pid3] == 500
    kill_msg() > pid1
    kill_msg() > pid2
    kill_msg() > pid3


if __name__ == "__main__":
    main()
