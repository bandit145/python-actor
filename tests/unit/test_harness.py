from actor.harness import Harness
import actor.utils
import actor.system.objects
import json
import pathlib
import time

actor.utils.load_env(None, "DEBUG")


def test_launch_harness():
    print(PID)
    tst_msg = info_msg(data={})
    pid = actor.utils.spawn("actor.actors.EchoActor", "debug")
    data = tst_msg >> pid
    #del data["ref"]
    assert PID != data['r_pid']
    assert tst_msg['msg_type'] == actor.system.objects.INFO_MSG
    assert tst_msg['data'] == {}
    # ssert harn.actor.state['count'] == 3
    kill_msg() > pid


def test_link():
    pid = actor.utils.link("actor.actors.EchoActor", "debug")
    kill_msg() > pid
    msg = MAILBOX.get(block=True)
    assert msg["msg_type"] == actor.system.objects.DEATH_MSG
    assert MAILBOX.empty()
