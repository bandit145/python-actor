import actor.utils as utils
from actor.actors import Actor
import os
import pathlib
import pickle
import importlib
import threading
import traceback
import atexit


# How to do we extract the state safely from a hung thread?
class Harness:
    links = []
    thread = None

    def __init__(self, pid):
        # this is what we will use for our pids
        utils.load_env(pid)
        print(PID)

    def __loop__(self, actor):
        with FIFO.open(mode="rb") as fifo:
            while True:
                # if fifo.
                print(MAILBOX)
                MAILBOX.append(pickle.load(fifo))
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
                                    target=actor.__entry_point__,
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
                                    target=actor.__entry_point__,
                                    args=(msg,),
                                )
                                self.thread.run()
                        case {"r_pid": _, "msg_type": utils.KILL_MSG}:
                            actor.utils.async_msg(
                                data["r_pid"], {"msg_type": utils.DEATH_MSG}
                            )
                            sys.exit(0)
                        case {"r_pid": _, "msg_type": utils.LINK_MSG}:
                            self.links.append(data["r_pid"])
                        case _:
                            print("idk what this message is: ", data)

    def launch_actor(self, pkg, actor):
        actor = getattr(importlib.import_module(pkg), actor)()
        while True:
            try:
                self.__loop__(actor)

            except Exception:
                print(traceback.format_exc())
