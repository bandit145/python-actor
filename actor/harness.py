import actor.utils as utils
from actor.actors import Actor
import actor.system.objects
import os
import pathlib
import pickle
import importlib
import threading
import traceback
import json
import atexit
import logging


# How to do we extract the state safely from a hung thread?
class Harness:
    links = []
    thread = None
    actor = None
    logger = None

    def __init__(self, pid, log_level, log_file):
        # this is what we will use for our pids
        utils.load_env(pid)
        # atexit.register(self.cleanup())
        self.configure_logging(log_level, log_file)
        self.logger.debug(f"HANDLER: {PID} started...")
        print(PID)

    def __loop__(self):
        with FIFO.open(mode="rb") as fifo:
            while True:
                # if fifo.
                data = fifo.read()
                if data != b"":
                    self.logger.debug(f"HANDLER: recieved message {data}")
                    data = json.loads(data)
                    data["r_pid"] = actor.system.objects.Pid(data["r_pid"])
                    MAILBOX.append(actor.system.objects.msg(data))
                self.logger.debug(f"HANDLER: mailbox status {MAILBOX}")
                # load data into list queue
                if len(MAILBOX) > 0:
                    # if our one thread is not active then pop the oldest item out and try and use it
                    match msg := MAILBOX.pop(0):
                        case {
                            "r_pid": _,
                            "msg_type": utils.RCE_MSG,
                            "method": _,
                            "kwargs": _,
                            "args": _,
                            "sync": _,
                        }:
                            # actor.utils.async_msg(data['r_pid'], {'msg_type': actor.utils.INFO_MSG})
                            if self.thread and self.thread.is_alive():
                                self.__queue__.append()
                            else:
                                self.thread = threading.Thread(
                                    target=self.actor.__entry_point__,
                                    args=(msg,),
                                )
                                self.thread.run()
                        case {
                            "r_pid": _,
                            "msg_type": utils.INFO_MSG,
                            "data": _,
                            "sync": _,
                        }:
                            if self.thread and self.thread.is_alive():
                                self.__queue__.append()
                            else:
                                self.thread = threading.Thread(
                                    target=self.actor.info_msg,
                                    args=(
                                        msg["r_pid"],
                                        msg,
                                    ),
                                )
                                self.thread.run()
                        case {"r_pid": _, "msg_type": utils.KILL_MSG}:
                            self.actor.utils.async_msg(
                                data["r_pid"], {"msg_type": utils.DEATH_MSG}
                            )
                            sys.exit(0)
                        case {"r_pid": _, "msg_type": utils.LINK_MSG}:
                            self.links.append(data["r_pid"])
                        case _:
                            print("idk what this message is: ", data)

    def configure_logging(self, log_level, log_file):
        self.logger = logging.getLogger("harness_logger")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        fh = logging.FileHandler(f"{log_file}/{PID}.log")
        self.logger.addHandler(fh)

    def launch_actor(self, pkg, actor):
        self.actor = getattr(importlib.import_module(pkg), actor)()
        self.logger.debug("HANDLER: Starting message processing loop.")
        while True:
            try:
                self.__loop__()

            except Exception:
                err = traceback.format_exc()
                self.logger.error(f"HANDLER: \n{err}")
                print(err)
