import actor.utils as utils
from actor.actors import Actor
import actor.system.exceptions
import actor.system.objects
import os
import sys
import importlib
import threading
import traceback
import json
import copy
import atexit

# How to do we extract the state safely from a hung thread?
class Harness:
    links = []
    actor = None
    log_file = None
    thread = None

    def __init__(self, pid):
        # this is what we will use for our pids
        PROC_LOGGER.debug(f"HANDLER: {PID} started...")
        atexit.register(self.cleanup)
        print(PID)

    def __loop__(self):
        with FIFO.open(mode="rb") as fifo:
            self.thread = threading.Thread(target=self.actor.start, daemon=True)
            self.thread.start()
            while True:
                # if fifo.
                data = fifo.read()
                if data != b"":
                    data = json.loads(data)
                    data["r_pid"] = actor.system.objects.Pid(data["r_pid"])
                    PROC_LOGGER.debug(f"HANDLER: recieved message {data}")
                    MAILBOX.append(actor.system.objects.msg(data))
                # load data into list queue
                if len(MAILBOX) > 0:
                    # if our one thread is not active then pop the oldest item out and try and use it
                    match msg := MAILBOX.pop(0):
                        case {
                            "r_pid": _,
                            "msg_type": utils.STD_MSG,
                            "data": _,
                            "sync": _,
                        }:
                            # we cannot have this getting modified when we loop to another
                            # message. This might not be needed as TECHNICALLY only one bit of python code is running at a time
                            # but in theory if we cause a blocking operation then new messages are read in.
                            # This would cause the old message to contain the reference to this one
                            if not self.thread.is_alive():
                                self.thread = threading.Thread(
                                    target=self.actor.msg,
                                    args=(
                                        msg["r_pid"],
                                        msg["sync"],
                                        copy.deepcopy(msg["data"]),
                                    ),
                                    daemon=True,
                                )
                                self.thread.start()
                            else:
                                MAILBOX.append(msg)
                        case {
                            "r_pid": _,
                            "msg_type": utils.INFO_MSG,
                            "data": _,
                            "sync": _,
                        }:
                            if not self.thread.is_alive():
                                self.thread = threading.Thread(
                                    target=self.actor.info_msg,
                                    args=(
                                        msg["r_pid"],
                                        msg["sync"],
                                        copy.deepcopy(msg["data"]),
                                    ),
                                    daemon=True,
                                )
                                self.thread.start()
                            else:
                                MAILBOX.append(msg)
                        case {
                            "r_pid": _,
                            "msg_type": utils.ERROR_MSG,
                            "traceback": _,
                            "exception": _,
                        }:
                            if not self.thread.is_alive():
                                self.thread = threading.Thread(
                                    target=self.actor.error_msg,
                                    args=(
                                        msg["r_pid"],
                                        msg["traceback"],
                                        msg["exception"],
                                    ),
                                    daemon=True,
                                )
                                self.thread.start()
                            else:
                                MAILBOX.append(msg)
                        case {"r_pid": _, "msg_type": utils.KILL_MSG}:
                            actor.system.objects.msg(msg_type=utils.DEATH_MSG) > msg[
                                "r_pid"
                            ]
                            PROC_LOGGER.debug(
                                f"HANDLER: recieved kill msg from {msg['r_pid']}. Going down!"
                            )
                            PROC_LOGGER.debug(
                                f"HANDLER: Actor state at shutdown {self.actor.state}"
                            )
                            sys.exit(0)
                        case {"r_pid": _, "msg_type": utils.LINK_MSG}:
                            PROC_LOGGER.debug(
                                f"HANDLER: linking {msg['r_pid']} to process"
                            )
                            self.links.append(data["r_pid"])
                        case {"r_pid": _, "msg_type": utils.UNLINK_MSG}:
                            PROC_LOGGER.debug(
                                f"HANDLER: unlinking {msg['r_pid']} from process"
                            )
                            self.links = [
                                link for links in self.links if link != msg["r_pid"]
                            ]
                            PROC_LOGGER.debug(f"HANDLER: current links {self.links}")
                        case {"r_pid": _}:
                            PROC_LOGGER.debug(
                                f"HANDLER: unkown message recieved. {msg}"
                            )
                            actor.system.objects.msg(msg_type=utils.ERR_MSG)
                        case _:
                            PROC_LOGGER.debug(
                                f"HANDLER: invalid message recieved. {msg}"
                            )

    def cleanup(self):
        self.notify_of_death()

    def notify_of_death(self):
        for pid in self.links:
            actor.system.objects.msg(msg_type=DEATH_MSG) > pid

    def launch_actor(self, pkg, actor):
        self.actor = getattr(importlib.import_module(pkg), actor)()
        PROC_LOGGER.debug("HANDLER: Starting message processing loop.")
        while True:
            try:
                self.__loop__()
            except Exception:
                err = traceback.format_exc()
                PROC_LOGGER.error(f"HANDLER: Exception occured\n{err}")
                print(err)
