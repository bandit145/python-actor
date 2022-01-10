from actor.utils import *
import copy
import traceback


class Actor:

    state = {}

    def __init__(self):
        pass

    def __entrypoint__(self, msg):
        try:
            match msg:
                case {
                    "msg_type": actor.system.objects.STD_MSG,
                }:
                    self.msg(msg["r_pid"], msg["ref"], msg)
                case {"msg_type": actor.system.objects.INFO_MSG}:
                    self.info_msg(msg["r_pid"], msg["ref"], msg)
                case {"msg_type": actor.system.objects.ERR_MSG}:
                    self.error_msg(msg["r_pid"], msg["ref"], msg)
                case {"msg_type": actor.system.objects.KILL_MSG}:
                    self.kill_msg(msg["r_pid"])
                case _:
                    PROC_LOGGER.debug(f"ACTOR: unrecognized msg type {msg}")

        except Exception:
            PROC_LOGGER.debug(f"ACTOR: UNCAUGHT ERROR:\n{traceback.format_exc()}")

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


class SpamActor(Actor):
    state = {"msg_cnt": 500}

    def msg(self, pid, ref, msg):
        if "begin" in msg["data"].keys():
            while self.state["msg_cnt"] > 0:
                std_msg(data={"spam_msg": True}) > pid
                self.state["msg_cnt"] -= 1
