from actor.system.objects import *
from actor.system.exceptions import InvalidMessage
import pytest
import uuid


def test_pid():
    uu = uuid.uuid4()
    pid = Pid(int=uu.int)
    assert str(uu) == str(pid)
    assert pid.__repr__() == f"Pid('{pid}')"

def test_msg():
    tst_msg = up_msg(data={})
    assert isinstance(tst_msg, dict)
    assert tst_msg['data'] == {}
    assert tst_msg['msg_type'] == UP_MSG

def test_msg_req():
    with pytest.raises(InvalidMessage):
        std_msg(weewoo=1)
    with pytest.raises(InvalidMessage):
        err_msg(traceback=1, exception=Exception('wat'))
    good_err_msg = err_msg(traceback='thing no worky :(', exception=InvalidMessage('Wrong!'))
