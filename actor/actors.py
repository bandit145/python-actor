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
                case {"msg_type": actor.system.objects.DEATH_MSG}:
                    self.msg(msg["r_pid"], None, msg)
                case _:
                    PROC_LOGGER.debug(f"ACTOR: unrecognized msg type {msg}")

        except Exception:
            PROC_LOGGER.debug(f"ACTOR: UNCAUGHT ERROR:\n{traceback.format_exc()}")

    def start(self):
        pass

    def msg(self, pid, ref, msg):
        pass

    def reload(self, pid):
        pass

    def death_msg(self, pid):
        pass

    def info_msg(self, pid, ref, msg):
        pass

    def error_msg(self, pid, traceback, exec):
        pass

    def kill_msg(self, pid):
        pass

class Supervisor(Actor):
    #{type: {pids: [], desired: int, active: int}}
    state = {'processes': {}}

    def kill_msg(self, msg):
        [map(lambda p: kill_msg() > p, pids['pids']) for pids in self.state['processes'].values()]

    def msg(self, pid, ref, msg):
        match msg:
            case {'data':{'spawn': _}}:
                if msg['data']['spawn'] not in self.state['processes']:
                    pids = [link(data['spawn']) for x in range(0, msg['data']['desired'])]
                    self.state['processes'][msg['data']['spawn']] = {'pids': pids, 'desired': msg['data']['desired']}
                elif self.state['data']['desired'] != msg['data']['desired']:
                    desired = msg['data']['desired']
                    spawn = msg['data']['spawn']
                    if self.state['data']['processes'][spawn]['desired'] > desired:
                        num = self.state['processes'][spawn]['desired'] - desired
                        self.state['data']['processes'][spawn]['desired'] = desired
                        map(lambda p: kill_msg() > p, self.state['processes'][spawn]['pids'][num:])
                    else:
                        num = desired - self.state['processes'][spawn]['desired']
                        [self.state['processes'][spawn][pids].append(link(spawn)) for x in range(0, num)]

                else:
                    info_msg(data={'info':'Supervisor already has requested state'}, ref=ref) > pid
            case {'msg_type': actor.system.objects.DEATH_MSG}:
                spawn = msg['data']['type']
                self.state = [x for x in self.state['processes'][spawn['pids']] if x != pid]
                if len(self.state['processes'][spawn]['pids']) < self.state['processes'][spawn]['desired']:
                    std_msg(data=dict(reload=spawn)) > PID

    def info_msg(self, pid, ref, msg):
        match msg:
            case {'dump_state': _}:
                info_msg(state=self.state, ref=ref) > pid

#Actors for testing purposes


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
