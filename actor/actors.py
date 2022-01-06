from actor.utils import *


class Actor:

    state = {}

    def __init__(self):
        pass

    def __entry_point__(self, msg):
        print(msg)
        getattr(self, msg["method"])(msg["r_pid"], msg)

    def sync_msg(self, pid, msg):
        async_msg(msg["r_pid"], {"msg_type": INFO_MSG, "data": "received"})

    def async_msg(self, pid, msg):
        pass

    def info_msg(self, pid, msg):
        pass

    def stop_msg(self, pid, msg):
        pass


class EchoActor:
    state = {"msg_cnt": 0}

    def __entry_point__(self, msg):
        getattr(self, msg["method"])(msg["r_pid"], msg)
        msg > msg["r_pid"]

    def info_msg(self, pid, msg):
        self.state["msg_cnt"] += 1
        msg > pid
