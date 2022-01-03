import actor.utils as utils
from actor.actors import Actor
from actor.system.objects import Pid
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
    actor = None

    def __init__(self, pid):
        # this is what we will use for our pids
        utils.load_env(pid)
        print(PID)

    def __loop__(self):
        with FIFO.open(mode="rb") as fifo:
            while True:
                # if fifo.
                print(MAILBOX)
                data = fifo.read_text()
                if data != '':
                    data = json.loads(data)
                    if 'r_pid' in data.keys():
                        data['r_pid'] = Pid(data['r_pid'])
                    MAILBOX.append(data)

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
                                    args=(msg['r_pid'], msg,),
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

    def launch_actor(self, pkg, actor):
        self.actor = getattr(importlib.import_module(pkg), actor)()
        while True:
            try:
                self.__loop__()

            except Exception:
                print(traceback.format_exc())
