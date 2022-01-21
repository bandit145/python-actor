from actor.utils import *
import copy
import traceback


class Actor:

    state = {}

    def __init__(self):
        pass

    def __entrypoint__(self, msg: actor.system.objects.MSG) -> None:
        try:
            match msg:
                case {
                    "msg_type": actor.system.objects.STD_MSG,
                }:
                    self.std(msg["r_pid"], msg["ref"], msg)
                case {"msg_type": actor.system.objects.INFO_MSG}:
                    self.info(msg["r_pid"], msg["ref"], msg)
                case {"msg_type": actor.system.objects.ERR_MSG}:
                    self.error(msg["r_pid"], msg["ref"], msg)
                case {"msg_type": actor.system.objects.KILL_MSG}:
                    self.kill(msg["r_pid"])
                case {"msg_type": actor.system.objects.DEATH_MSG}:
                    self.death(msg["r_pid"], None, msg)
                case _:
                    PROC_LOGGER.debug(f"ACTOR: unrecognized msg type {msg}")

        except Exception:
            PROC_LOGGER.debug(f"ACTOR: UNCAUGHT ERROR:\n{traceback.format_exc()}")

    def start(self) -> None:
        pass

    def std(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        pass

    def reload(self, pid: actor.system.objects.Pid) -> None:
        pass

    def death(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        pass

    def info(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        pass

    def error(self, pid: actor.system.objects.Pid, traceback: str, exec: Exception) -> None:
        pass

    def kill(self, pid: actor.system.objects.Pid) -> None:
        pass


class Supervisor(Actor):
    # {type: {pids: [], desired: int}}
    state = {"processes": {}}

    def kill(self, pid: actor.system.objects.Pid) -> None:
        for _, v in self.state["processes"].items():
            for p in v["pids"]:
                PROC_LOGGER.debug(f"SUPERVISOR: going down and terminating {p}")
                kill_msg() > p

    def std(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        match msg:
            case {"data": {"spawn": _}}:
                if msg["data"]["spawn"] not in self.state["processes"]:
                    if "log_level" in msg["data"]:
                        log_level = msg["data"]["log_level"]
                    else:
                        log_level = "info"
                    pids = [
                        link(msg["data"]["spawn"], log_level)
                        for x in range(0, msg["data"]["desired"])
                    ]
                    self.state["processes"][msg["data"]["spawn"]] = {
                        "pids": pids,
                        "desired": msg["data"]["desired"],
                        "log_level": log_level,
                    }
                elif (
                    self.state["processes"][msg["data"]["spawn"]]["desired"]
                    != msg["data"]["desired"]
                ):
                    desired = msg["data"]["desired"]
                    spawn = msg["data"]["spawn"]
                    if self.state["processes"][spawn]["desired"] > desired:
                        num = self.state["processes"][spawn]["desired"] - desired
                        self.state["processes"][spawn]["desired"] = desired
                        PROC_LOGGER.debug(f"SUPERVISOR: reducing {spawn} by {num}")
                        for p in self.state["processes"][spawn]["pids"][:num]:
                            kill_msg() > p
                        # map(
                        #     lambda p: kill_msg() > p,
                        #     self.state["processes"][spawn]["pids"][:num],
                        # )
                    else:
                        num = desired - self.state["processes"][spawn]["desired"]
                        PROC_LOGGER.debug(f"SUPERVISOR: increasing {spawn} by {num}")
                        self.state["processes"][spawn]["desired"] = desired
                        [
                            self.state["processes"][spawn]["pids"].append(
                                link(spawn, self.state["processes"][spawn]["log_level"])
                            )
                            for x in range(0, num)
                        ]
                elif self.state["processes"][msg["data"]["spawn"]]["desired"] > len(
                    self.state["processes"][msg["data"]["spawn"]]["pids"]
                ):
                    spawn = msg["data"]["spawn"]
                    num = self.state["processes"][msg["data"]["spawn"]][
                        "desired"
                    ] - len(self.state["processes"][msg["data"]["spawn"]]["pids"])
                    [
                        self.state["processes"][spawn]["pids"].append(
                            link(spawn, self.state["processes"][spawn]["log_level"])
                        )
                        for x in range(0, num)
                    ]

                else:
                    info_msg(
                        data={"info": "Supervisor already has requested state"}, ref=ref
                    ) > pid

    def death(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        self.state["processes"][msg["type"]]["pids"] = [
            x for x in self.state["processes"][msg["type"]]["pids"] if x != pid
        ]
        if (
            len(self.state["processes"][msg["type"]]["pids"])
            < self.state["processes"][msg["type"]]["desired"]
        ):
            std_msg(
                data=dict(
                    spawn=msg["type"],
                    desired=self.state["processes"][msg["type"]]["desired"],
                )
            ) > PID

    def info(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        match msg:
            case {"dump_state": _}:
                PROC_LOGGER.debug(f"SUPERVISOR: dumping state to {pid}\n{msg}")
                info_msg(state=self.state, ref=ref) > pid


# Actors for testing purposes


class EchoActor(Actor):
    state = {"msg_cnt": 0}

    def start(self) -> None:
        print("test")

    def info(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        self.state["msg_cnt"] += 1
        if ref:
            info_msg(data=msg["data"], ref=ref) > pid


class SpamActor(Actor):
    state = {"msg_cnt": 500}

    def std(self, pid: actor.system.objects.Pid, ref: actor.system.objects.Ref, msg: actor.system.objects.Msg) -> None:
        if "begin" in msg["data"].keys():
            while self.state["msg_cnt"] > 0:
                std_msg(data={"spam_msg": True}) > pid
                self.state["msg_cnt"] -= 1
