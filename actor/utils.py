import uuid
import json
import os
import subprocess
import pathlib
import actor.system.objects
import atexit
import threading

INFO_MSG = 1
RCE_MSG = 2
KILL_MSG = 3
DEATH_MSG = 4
UP_MSG = 5
ERR_MSG = 6
LINK_MSG = 7

def cleanup():
    os.remove(FIFO)

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
    #atexit.register(cleanup)


def create_pipe():
    if not os.path.exists(FIFO_DIR):
        os.mkdir(FIFO_DIR)
    fifo = pathlib.Path(f"{FIFO_DIR}/{PID}")
    os.mkfifo(fifo)
    return fifo


def __msg_send__(pid, msg):
    with open(f"{FIFO_DIR}/{pid}", "w") as fifo:
        json.dump(msg, fifo)



def async_msg(pid, msg, **kwargs):
    msg["r_pid"] = str(PID)
    msg["sync"] = False
    if msg["msg_type"] == RCE_MSG:
        if "kwargs" not in msg.keys():
            msg["kwargs"] = None
        if "args" not in msg.keys():
            msg["args"] = None
    # we make this a daemon to avoid situations when a pipe will not be read. In these situations the IO operation will prevent 
    # you from going down which we do not want
    t = threading.Thread(target=__msg_send__, args=(pid, msg,), daemon=True)
    t.start()
    return t

def sync_msg(pid, msg, **kwargs):
    _ = async_msg(pid, msg, **kwargs)
    with FIFO.open(mode="rb") as r_pipe:
        data = json.load(r_pipe)
    data["r_pid"] = actor.system.objects.Pid(data["r_pid"])
    return actor.system.objects.msg(data)

def kill(pid):
    async_msg(pid, actor.system.objects.msg(msg_type=KILL_MSG, r_pid=PID))

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
