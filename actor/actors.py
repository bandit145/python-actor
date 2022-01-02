from actor.utils import *


class Actor:

    state = {}

    def __init__(self):
        pass

    def __entry_point__(self, msg):
        print(msg)
        getattr(self, msg["method"])(msg["r_pid"], msg)

    def sync_msg(self, pid, msg):
        async_msg(msg["r_pid"], {"msg_type": INFO_MSG, "data": "recieved"})

    def async_msg(self, pid, msg):
        pass

    def info_msg(self, pid, msg):
        pass

    def stop_msg(self, pid, msg):
        pass
