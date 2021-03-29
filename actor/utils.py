import uuid
import pickle
import os
import subprocess

INFO_MSG = 1
RCE_MSG = 2
KILL_MSG = 3
DEATH_MSG = 4
UP_MSG = 5
ERR_MSG = 6
LINK_MSG = 7


def load_env():
    global fifo_dir
    global PID
    fifo_dir = "/tmp/"
    PID = uuid.uuid4()


def async_msg(pid, msg, **kwargs):
    msg["r_pid"] = PID
    msg["sync"] = False
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    if "fifo_dir" in kwargs.keys():
        fifo_dir = kwargs["fifo_dir"]
    with open(f"/tmp/{pid}", "a") as fifo:
        pickle.dump(msg, fifo)


def sync_msg(pid, msg, **kwargs):
    msg["r_pid"] = PID
    msg["sync"] = True
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    if "fifo_dir" in kwargs.keys():
        fifo_dir = kwargs["fifo_dir"]
    # create a pipe to block for sync msg
    r, w = os.pipe()
    msg["r_pipe"] = w
    with open(f"/tmp/{pid}", "a") as fifo:
        pickle.dump(msg, fifo)
    with open(r, "r") as r_pipe:
        data = pickle.load(r_pipe)
    return data


def spawn(actor):
    proc = subprocess.Popen(
        ["python", "-m", "actor", "--actor", actor, "--pid", PID], stdin=subprocess.PIPE
    )
    pass
