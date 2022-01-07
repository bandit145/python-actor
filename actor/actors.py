from actor.utils import *


class Actor:

    state = {}

    def __init__(self):
        pass

    def start(self):
        pass

    def rce_msg(self, pid, msg):
        pass

    def async_msg(self, pid, msg):
        pass

    def info_msg(self, pid, msg):
        pass

    def error_msg(self, pid, traceback, exec):
        pass

    def kill_msg(self, pid):
        pass


class EchoActor(Actor):
    state = {"msg_cnt": 0}

    def info_msg(self, pid, msg):
        self.state["msg_cnt"] += 1
        msg > pid
