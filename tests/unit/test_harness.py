from actor.harness import Harness
import actor.utils
import json
import pathlib
import time

actor.utils.load_env()


def test_launch_harness():
    print(PID)
    tst_msg = msg({"r_pid": str(PID), "msg_type": actor.utils.INFO_MSG, "data": {}})
    pid = actor.utils.spawn("actor.actors.EchoActor", "debug")
    data = tst_msg >> pid
    print(data)
    tst_msg["r_pid"] = data["r_pid"]
    tst_msg["sync"] = False
    assert data == tst_msg
    # ssert harn.actor.state['count'] == 3
    actor.utils.kill(pid)

def test_link():
    pid = actor.utils.link("actor.actors.EchoActor", "debug")
    data = kill_msg() >> pid
    print(data)
    assert data['msg_type'] == actor.utils.DEATH_MSG

