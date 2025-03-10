import uuid
import json
import os
import subprocess
import pathlib
import actor.system.objects
import atexit
import threading
import logging
import queue
import traceback
import time
from actor.parsing import decode_object_hook, JSONEncoder
from actor.system.exceptions import SpawnException


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


def recv_msg():
    with FIFO.open(mode="rb") as fifo:
        while True:
            data = fifo.read()
            for line in data.split(b"\n"):
                try:
                    if line != b"":
                        PROC_LOGGER.debug(
                            f"MSG PROCESSING LOOP: recieved message (raw) {data}"
                        )
                        line = json.loads(line, object_hook=decode_object_hook)
                        PROC_LOGGER.debug(
                            f"MSG PROCESSING LOOP: received message {line}"
                        )
                        MAILBOX.put(
                            actor.system.objects.ID_MSG_MAP[line["msg_type"]](**line)
                        )
                except json.JSONDecodeError:
                    PROC_LOGGER.error(f"MSG PROCESSING LOOP: could not decode {line}")
                except Exception:
                    PROC_LOGGER.error(
                        f"MSG PROCESSING LOOP: unkown message proceesing issue occured\n {traceback.format_exc()}"
                    )


def load_env(pid=None, log_level="INFO", log_file="/var/log/pyactor"):
    import builtins

    if not hasattr(builtins, "FIFO_DIR"):
        builtins.FIFO_DIR = "/var/run/actor"
        builtins.MAILBOX = queue.Queue()
        builtins.info_msg = actor.system.objects.info_msg
        builtins.std_msg = actor.system.objects.std_msg
        builtins.kill_msg = actor.system.objects.kill_msg
        builtins.death_msg = actor.system.objects.death_msg
        builtins.up_msg = actor.system.objects.up_msg
        builtins.err_msg = actor.system.objects.err_msg
        builtins.link_msg = actor.system.objects.link_msg
        builtins.unlink_msg = actor.system.objects.unlink_msg
        builtins.reload_msg = actor.system.objects.reload_msg
        builtins.spawn = spawn
        builtins.link = link
        builtins.pop_mailbox = pop_mailbox
        if not pid:
            builtins.PID = actor.system.objects.Pid(int=uuid.uuid4().int)
        else:
            builtins.PID = pid
        builtins.FIFO = create_pipe()
        builtins.LOG_FILE = log_file
        configure_logging(builtins, log_level, log_file)
        builtins.RECV_MSG_THREAD = threading.Thread(target=recv_msg, daemon=True)
        builtins.RECV_MSG_THREAD.start()
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
    msg["r_pid"] = PID
    if not os.path.exists(f"{FIFO_DIR}/{pid}.dwn") and os.path.exists(
        f"{FIFO_DIR}/{pid}"
    ):
        with open(f"{FIFO_DIR}/{pid}", "w") as fifo:
            fifo.write(f"{json.dumps(msg, cls=JSONEncoder)}\n")


def async_msg(pid, msg):
    if "ref" not in msg.keys():
        msg["ref"] = None
    __send_msg__(pid, msg)


def sync_msg(pid, msg):
    ref = actor.system.objects.Ref(int=uuid.uuid4().int)
    msg["ref"] = ref
    __send_msg__(pid, msg)
    # TODO, put this in the mailbox if it does not have a ref
    while True:
        if not MAILBOX.empty():
            r_msg = MAILBOX.get()
            if "ref" in r_msg.keys():
                if ref == r_msg["ref"]:
                    return r_msg
            MAILBOX.put(r_msg)


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
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    start = time.time()
    while not os.path.exists(f"{FIFO_DIR}/{n_pid}"):
        if time.time() - start > 5:
            break
    proc.poll()
    if proc.returncode:
        out, _ = proc.communicate()
        raise SpawnException(f"{n_pid} died.\n{out}")
    PROC_LOGGER.debug(f"SPAWN: {PID} spawned {n_pid}")
    return n_pid


def pop_mailbox():
    if not MAILBOX.empty():
        return MAILBOX.get()


def link(actor_obj, log_level="info"):
    pid = spawn(actor_obj, log_level)
    actor.system.objects.link_msg() > pid
    return pid
