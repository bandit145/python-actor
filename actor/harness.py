import actor.util
from actor.actors import Actor
import importlib
import threading
import traceback


# How to do we extract the state safely from a hung thread?
class Harness:
    __queue__ = []
    __fifo_dir__ = "/tmp/"
    __fifo__ = None
    links = []
    thread = None

    def __init__(self):
        # this is what we will use for our pids
        self.__uuid__ = uuid.uuid4()
        global PID
        PID = self.__uuid__
        print(PID)
        self.__create_fifo__()

    def __loop__(self, actor):
        with self.__fifo__.open() as fifo:
            while True:
                self.__queue__.append(pickle.load(fifo))
                # load data into list queue
                if len(self.__queue__) > 0:
                    # if our one thread is not active then pop the oldest item out and try and use it
                    match self.__queue__.pop(0):
                        case {
                            "r_pid": _,
                            "msg_type": actor.utils.RCE_MSG,
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
                                    args=(
                                        data["method"],
                                        {
                                            "kwargs": data["kwargs"],
                                            "args": data["args"],
                                            "sync": data["sync"],
                                        },
                                    ),
                                )
                                self.thread.run()
                        case {
                            "r_pid": _,
                            "msg_type": actor.utils.INFO_MSG,
                            "data": _,
                            "sync": _,
                        }:
                            if self.thread and self.thread.is_alive():
                                self.__queue__.append()
                            else:
                                self.thread = threading.Thread(
                                    target=actor.__entry_point__,
                                    args=(
                                        data["method"],
                                        {
                                            "kwargs": data["kwargs"],
                                            "args": data["args"],
                                            "sync": data["sync"],
                                        },
                                    ),
                                )
                                self.thread.run()
                        case {"r_pid": _, "msg_type": actor.utils.KILL_MSG}:
                            actor.utils.async_msg(
                                data["r_pid"], {"msg_type": actor.utils.DEATH_MSG}
                            )
                            sys.exit(0)
                        case {"r_pid": _, "msg_type": actor.utils.LINK_MSG}:
                            self.links.append(data["r_pid"])
                        case _:
                            print("idk what this message is: ", data)

    def __create_fifo__(self):
        self.__fifo__ = pathlib.Path(f"{self.__fifo_dir__}/{self.__uuid__}")
        os.mkfifo(self.__fifo__)

    def launch_actor(self, pkg, actor):
        try:
            actor = getattr(getattrimportlib.import_module(pkg), actor)()
            self.__loop__(actor)

        except Exception:
            print(traceback.format_exc())
