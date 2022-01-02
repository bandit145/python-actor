import uuid
import pickle
import os
import subprocess
import pathlib

INFO_MSG = 1
RCE_MSG = 2
KILL_MSG = 3
DEATH_MSG = 4
UP_MSG = 5
ERR_MSG = 6
LINK_MSG = 7


def load_env(pid=None):
    import builtins

    builtins.FIFO_DIR = "/tmp/actor"
    builtins.MAILBOX = []
    if not pid:
        builtins.PID = uuid.uuid4()
    else:
        builtins.PID = pid
    builtins.FIFO = create_pipe()


def create_pipe():
    fifo = pathlib.Path(f"{FIFO_DIR}/{PID}")
    os.mkfifo(fifo)
    return fifo


def async_msg(pid, msg, **kwargs):
    msg["r_pid"] = PID
    msg["sync"] = False
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    with open(f"{FIFO_DIR}/{pid}", "ab") as fifo:
        pickle.dump(msg, fifo)


def sync_msg(pid, msg, **kwargs):
    msg["r_pid"] = PID
    msg["sync"] = True
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    # create a pipe to block for sync msg
    with open(f"{FIFO_DIR}/{pid}", "wb") as fifo:
        pickle.dump(msg, fifo)
    with FIFO.open(mode="rb") as r_pipe:
        data = pickle.load(r_pipe)
    return data


def spawn(actor):
    n_pid = uuid.uuid4()
    subprocess.Popen(
        [
            "python",
            "-m",
            "actor",
            "--actor",
            actor,
            "--r_pid",
            str(PID),
            "--n_pid",
            str(n_pid),
        ]
    )
    return n_pid
