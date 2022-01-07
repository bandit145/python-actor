import uuid
import json
import os
import subprocess
import pathlib
import actor.system.objects
import atexit
import threading
import logging

INFO_MSG = 1
STD_MSG = 2
KILL_MSG = 3
DEATH_MSG = 4
UP_MSG = 5
ERR_MSG = 6
LINK_MSG = 7
UNLINK_MSG = 8


def cleanup():
    # create file to block any new messages being sent
    with open(f"{FIFO_DIR}/{PID}.dwn", mode="w"):
        pass

    def purge():
        with FIFO.open(mode="rb") as f:
            _ = f.read()

    # do a final read, purging the file of any latent messages that may be holding processes open
    threading.Thread(target=purge, daemon=True).start()
    os.remove(FIFO)
    os.remove(f"{FIFO_DIR}/{PID}.dwn")
    if (
        LOG_FILE
        and not os.getenv("NO_LOG_CLEANUP")
        and os.path.exists(f"{LOG_FILE}/{PID}.log")
    ):
        os.remove(f"{LOG_FILE}/{PID}.log")


def load_env(pid=None, log_level="INFO", log_file=None):
    import builtins

    builtins.FIFO_DIR = "/tmp/actor"
    builtins.MAILBOX = []
    builtins.msg = actor.system.objects.msg
    builtins.info_msg = actor.system.objects.info_msg
    builtins.std_msg = actor.system.objects.std_msg
    builtins.kill_msg = actor.system.objects.kill_msg
    builtins.death_msg = actor.system.objects.death_msg
    builtins.up_msg = actor.system.objects.up_msg
    builtins.err_msg = actor.system.objects.err_msg
    builtins.link_msg = actor.system.objects.link_msg
    builtins.unlink_msg = actor.system.objects.unlink_msg
    if not pid:
        builtins.PID = actor.system.objects.Pid(int=uuid.uuid4().int)
    else:
        builtins.PID = pid
    builtins.FIFO = create_pipe()
    builtins.LOG_FILE = log_file
    if log_file:
        configure_logging(builtins, log_level, log_file)
    atexit.register(cleanup)


def configure_logging(builtins, log_level, log_file):
    builtins.PROC_LOGGER = logging.getLogger("process_logger")
    builtins.PROC_LOGGER.setLevel(getattr(logging, log_level.upper()))
    fh = logging.FileHandler(f"{LOG_FILE}/{PID}.log")
    fmt = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    fh.setFormatter(fmt)
    builtins.PROC_LOGGER.addHandler(fh)


def create_pipe():
    if not os.path.exists(FIFO_DIR):
        os.mkdir(FIFO_DIR)
    fifo = pathlib.Path(f"{FIFO_DIR}/{PID}")
    os.mkfifo(fifo)
    return fifo


def __send_msg__(pid, msg):
    if not os.path.exists(f"{FIFO_DIR}/{pid}.dwn") and os.path.exists(
        f"{FIFO_DIR}/{pid}"
    ):
        with open(f"{FIFO_DIR}/{pid}", "w") as fifo:
            json.dump(msg, fifo)


def async_msg(pid, msg):
    msg["r_pid"] = str(PID)
    msg["sync"] = False
    __send_msg__(pid, msg)


def sync_msg(pid, msg):
    msg["r_pid"] = str(PID)
    msg["sync"] = True
    __send_msg__(pid, msg)
    with FIFO.open(mode="rb") as r_pipe:
        data = json.load(r_pipe)
    data["r_pid"] = actor.system.objects.Pid(data["r_pid"])
    data["sync"] = bool(data["sync"])
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
