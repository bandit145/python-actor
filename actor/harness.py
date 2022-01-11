import actor.utils as utils
from actor.actors import Actor
import actor.system.exceptions
import actor.system.objects
import os
import sys
import importlib
import signal
import threading
import traceback
import json
import copy
import atexit
import time

# How to do we extract the state safely from a hung thread?
class Harness:
    links = []
    actor = None
    log_file = None
    thread = None
    module = None

    def __init__(self, pid):
        # this is what we will use for our pids
        PROC_LOGGER.debug(f"HANDLER: {PID} started...")
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.signal_kill)
        print(PID)

    def __loop__(self):
        self.thread = threading.Thread(target=self.actor.start, daemon=True)
        self.thread.start()
        while True:
            # load data into list queue
            if not MAILBOX.empty():
                # if our one thread is not active then pop the oldest item out and try and use it
                match msg := MAILBOX.get():
                    case {"r_pid": _, "msg_type": actor.system.objects.KILL_MSG}:
                        PROC_LOGGER.debug(
                            f"HANDLER: received kill msg from {msg['r_pid']}. Going down!"
                        )
                        PROC_LOGGER.debug(
                            f"HANDLER: Actor state at shutdown {self.actor.state}"
                        )
                        start = time.time()
                        #might add a configurable timeout thing for this
                        while time.time() - start < 60:
                            if self.thread.is_alive():
                                self.actor.__entrypoint__(msg)
                        sys.exit(0)
                    case {"r_pid": _, "msg_type": actor.system.objects.LINK_MSG}:
                        PROC_LOGGER.debug(f"HANDLER: linking {msg['r_pid']} to process")
                        if msg["r_pid"] not in self.links:
                            self.links.append(msg["r_pid"])
                            link_msg() > msg['r_pid']
                    case {"r_pid": _, "msg_type": actor.system.objects.UNLINK_MSG}:
                        PROC_LOGGER.debug(
                            f"HANDLER: unlinking {msg['r_pid']} from process"
                        )
                        self.links = [
                            link for links in self.links if link != msg["r_pid"]
                        ]
                        PROC_LOGGER.debug(f"HANDLER: current links {self.links}")
                    case {"r_pid": _, "msg_type": actor.system.objects.RELOAD_MSG}:
                        if not self.thread.is_alive():
                            self.actor.reload(msg["r_pid"])
                            self.module = importlib.reload(self.module)
                            self.actor = getattr(self.module, self.actor.__class__.__name__)()
                        else:
                            MAILBOX.append(msg)

                    case {
                        "r_pid": _,
                        "msg_type": _,
                        "data": _,
                        "ref": _,
                    }:
                        # we cannot have this getting modified when we loop to another
                        # message. This might not be needed as TECHNICALLY only one bit of python code is running at a time
                        # but in theory if we cause a blocking operation then new messages are read in.
                        # This would cause the old message to contain the reference to this one
                        if not self.thread.is_alive():
                            self.thread = threading.Thread(
                                target=self.actor.__entrypoint__,
                                args=(copy.deepcopy(msg),),
                                daemon=True,
                            )
                            self.thread.start()
                        else:
                            MAILBOX.append(msg)
                    case {"r_pid": _}:
                        PROC_LOGGER.debug(f"HANDLER: unknown message received. {msg}")
                        actor.system.objects.msg(msg_type=actor.system.objects.ERR_MSG)
                    case _:
                        PROC_LOGGER.debug(f"HANDLER: invalid message recieved. {msg}")

    def cleanup(self):
        self.notify_of_death()

    def signal_kill(self, num, stck_frame):
        sys.exit(0)

    def notify_of_death(self):
        for pid in self.links:
            death_msg() > pid

    def launch_actor(self, pkg, actor):
        self.module = importlib.import_module(pkg)
        self.actor = getattr(self.module, actor)()
        while True:
            try:
                self.__loop__()
            except Exception:
                err = traceback.format_exc()
                PROC_LOGGER.error(f"HANDLER: Exception occured\n{err}")
                print(err)
