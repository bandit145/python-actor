import actor.utils


class Actor:

    state = {}

    def __init__(self):
        pass

    def __entry_point__(self, method, msg, event):
        getattr(self, method)(msg)

    def sync_msg(self, pid, msg):
        pass

    def async_msg(self, pid, msg):
        pass

    def info_msg(self, pid, msg):
        pass

    def stop_msg(self, pid, msg):
        pass
