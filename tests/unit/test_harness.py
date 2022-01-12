from actor.harness import Harness
import actor.utils
import actor.system.objects
import json
import pathlib
import queue
import time
import re
import atexit

actor.utils.load_env(None, "DEBUG")


def test_launch_harness():
    print(PID)
    tst_msg = info_msg(data={})
    pid = spawn("actor.actors.EchoActor", "debug")
    data = tst_msg >> pid
    # del data["ref"]
    assert PID != data["r_pid"]
    assert tst_msg["msg_type"] == actor.system.objects.INFO_MSG
    assert tst_msg["data"] == {}
    # ssert harn.actor.state['count'] == 3
    kill_msg() > pid


def test_link():
    pid = link("actor.actors.EchoActor", "debug")
    #A link is a two way linking therefore our process will receive a link message when our request to link is
    # received by the other process.
    start = time.time()
    while time.time() - start < 10:
        try:
            msg = MAILBOX.get(block=False)
            if msg['r_pid'] == pid:
                break
        except queue.Empty:
            pass
    assert msg["msg_type"] == actor.system.objects.LINK_MSG
    kill_msg() > pid
    start = time.time()
    while time.time() - start < 10:
        try:
            msg = MAILBOX.get(block=False)
            if msg['r_pid'] == pid:
                break
        except queue.Empty:
            pass
    assert msg["msg_type"] == actor.system.objects.DEATH_MSG
    assert MAILBOX.empty()


def test_code_reload():
    pid = spawn("tests.unit.actors.EchoActor", "debug")
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
    msg = info_msg(data={}) >> pid
    assert "reloaded" not in msg.keys()
    with open("tests/unit/actors.py", "w") as f:
        f.write(new_code)
    reload_msg() > pid
    msg = info_msg(data={}) >> pid
    assert msg["reloaded"]
    kill_msg() > pid
