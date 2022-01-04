import uuid
import json
import os
import subprocess
import pathlib
import actor.system.objects

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
    builtins.msg = actor.system.objects.msg
    if not pid:
        builtins.PID = actor.system.objects.Pid(int=uuid.uuid4().int)
    else:
        builtins.PID = pid
    builtins.FIFO = create_pipe()


def create_pipe():
    if not os.path.exists(FIFO_DIR):
        os.mkdir(FIFO_DIR)
    fifo = pathlib.Path(f"{FIFO_DIR}/{PID}")
    os.mkfifo(fifo)
    return fifo


def async_msg(pid, msg, **kwargs):
    msg["r_pid"] = str(PID)
    msg["sync"] = False
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    with open(f"{FIFO_DIR}/{pid}", "w") as fifo:
        json.dump(msg, fifo)


def sync_msg(pid, msg, **kwargs):
    msg["r_pid"] = str(PID)
    msg["sync"] = True
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    # create a pipe to block for sync msg
    with open(f"{FIFO_DIR}/{pid}", "w") as fifo:
        json.dump(msg, fifo)
    with FIFO.open(mode="rb") as r_pipe:
        data = json.load(r_pipe)
    data["r_pid"] = actor.system.objects.Pid(data["r_pid"])
    return actor.system.objects.msg(data)


def spawn(actor_obj, log_level="info"):
    n_pid = actor.system.objects.Pid(int=uuid.uuid4().int)
    proc = subprocess.Popen(
        [
            "python",
            "-m",
            "actor",
            "--actor",
            actor_obj,
            "--r_pid",
            str(PID),
            "--n_pid",
            str(n_pid),
            "--log_level",
            log_level,
        ]
    )
    while not os.path.exists(f"{FIFO_DIR}/{n_pid}"):
        pass
    return n_pid
