from actor.utils import *


class Actor:

    state = {}

    def __init__(self):
        pass

    def start(self):
        pass

    def msg(self, pid, ref, msg):
        pass

    def info_msg(self, pid, ref, msg):
        pass

    def error_msg(self, pid, traceback, exec):
        pass

    def kill_msg(self, pid):
        pass


class EchoActor(Actor):
    state = {"msg_cnt": 0}

    def start(self):
        print("test")

    def info_msg(self, pid, ref, msg):
        self.state["msg_cnt"] += 1
        if ref:
            info_msg(data=msg["data"], ref=ref) > pid
