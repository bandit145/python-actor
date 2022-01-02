from actor import utils

utils.load_env()


def test_spawn():
    pid = utils.spawn("actor.actors.Actor")
    data = utils.sync_msg(
        pid, {"msg_type": utils.RCE_MSG, "method": "sync_msg"}, fifo_dir="/tmp/"
    )
    assert data == {
        "msg_type": INFO_MSG,
        "data": "recieved",
        "r_pid": pid,
        "sync": False,
    }
