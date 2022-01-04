from actor.harness import Harness
import actor.utils
import json
import pathlib

actor.utils.load_env()


def test_launch_harness():
    print(PID)
    tst_msg = msg({"r_pid": str(PID), "msg_type": actor.utils.INFO_MSG})
    pid = actor.utils.spawn("actor.actors.EchoActor", "debug")
    data = tst_msg >> pid
    print(data)
    del tst_msg["r_pid"]
    del data["r_pid"]
    assert data == tst_msg
    # ssert harn.actor.state['count'] == 3
