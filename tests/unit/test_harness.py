from actor.harness import Harness
import actor.utils
import actor.system.objects
import json
import pathlib
import time
import re
import atexit

actor.utils.load_env(None, "DEBUG")


def test_launch_harness():
    print(PID)
    tst_msg = info_msg(data={})
    pid = actor.utils.spawn("actor.actors.EchoActor", "debug")
    data = tst_msg >> pid
    # del data["ref"]
    assert PID != data["r_pid"]
    assert tst_msg["msg_type"] == actor.system.objects.INFO_MSG
    assert tst_msg["data"] == {}
    # ssert harn.actor.state['count'] == 3
    kill_msg() > pid


def test_link():
    pid = actor.utils.link("actor.actors.EchoActor", "debug")
    kill_msg() > pid
    msg = MAILBOX.get(block=True)
    assert msg["msg_type"] == actor.system.objects.DEATH_MSG
    assert MAILBOX.empty()


def test_code_reload():
    pid = actor.utils.spawn("tests.unit.actors.EchoActor", "debug")
    # have to wait otherwise we rewrite the code too quickly causing the first asswert to fail
    time.sleep(1)
    with open("tests/unit/actors.py", "r") as code_f:
        code = code_f.read()
    new_code = re.sub(
        r'            info_msg\(data=msg\["data"\], ref=ref\) > pid',
        r"            info_msg(reloaded=True, ref=ref, data={}) > pid",
        code,
    )
    def restore_code(old_code):
        with open("tests/unit/actors.py", "w") as f:
            f.write(old_code)
    atexit.register(restore_code, code)
    with open("tests/unit/actors.py", "w") as f:
            f.write(new_code)
    msg = info_msg(data={}) >> pid
    assert 'reloaded' not in msg.keys()
    reload_msg() > pid
    msg = info_msg(data={}) >> pid
    assert msg['reloaded']
    kill_msg() > pid
