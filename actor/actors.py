from actor.utils import *


class Actor:

    state = {}

    def __init__(self):
        pass

    def start(self):
        pass

    def msg(self, pid, sync, data):
        pass

    def info_msg(self, pid, sync, data):
        pass

    def error_msg(self, pid, traceback, exec):
        pass

    def kill_msg(self, pid):
        pass


class EchoActor(Actor):
    state = {"msg_cnt": 0}

    def start(self):
        print("test")

    def info_msg(self, pid, sync, data):
        self.state["msg_cnt"] += 1
        if sync:
            msg(data=data, msg_type=INFO_MSG) > pid
