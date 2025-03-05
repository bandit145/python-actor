from uuid import UUID
import actor.utils
from actor.system.exceptions import InvalidMessage
import copy

INFO_MSG = 0
STD_MSG = 1
KILL_MSG = 2
DEATH_MSG = 3
UP_MSG = 4
ERR_MSG = 5
LINK_MSG = 6
UNLINK_MSG = 7
RELOAD_MSG = 8


class Pid(UUID):
    def __repr__(self):
        return f"Pid('{self.__str__()}')"


class Ref(UUID):
    def __repr__(self):
        return f"Ref('{self.__str__()}')"


class msg(dict):
    __required_format__ = {}

    def __init__(self, *args, **kwargs):
        if self.__required_format__ != {}:
            self.__required_format__["msg_type"] = int
            keys = kwargs.keys()
            for k, v in self.__required_format__.items():
                if k not in keys:
                    raise InvalidMessage(
                        f"Message missing one of required keys {list(self.__required_format__.keys())}"
                    )
                if not isinstance(kwargs[k], v):
                    raise (
                        InvalidMessage(
                            f"Message has a value that is not the proper type. {k} should be type: {v}"
                        )
                    )
        super().__init__(*args, **kwargs)

    def __gt__(self, pid):
        actor.utils.async_msg(pid, copy.deepcopy(self))

    def __rshift__(self, pid):
        return actor.utils.sync_msg(pid, copy.deepcopy(self))


class info_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = INFO_MSG
        super().__init__(**kwargs)


class std_msg(msg):
    __required_format__ = {"data": dict}

    def __init__(self, **kwargs):
        kwargs["msg_type"] = STD_MSG
        super().__init__(**kwargs)


class kill_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = KILL_MSG
        super().__init__(**kwargs)


class death_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = DEATH_MSG
        super().__init__(**kwargs)


class up_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = UP_MSG
        super().__init__(**kwargs)


class err_msg(msg):
    __required_format__ = {"traceback": str, "exception": Exception}

    def __init__(self, **kwargs):
        kwargs["msg_type"] = ERR_MSG
        super().__init__(**kwargs)


class link_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = LINK_MSG
        super().__init__(**kwargs)


class unlink_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = UNLINK_MSG
        super().__init__(**kwargs)


class reload_msg(msg):
    def __init__(self, **kwargs):
        kwargs["msg_type"] = RELOAD_MSG
        super().__init__(**kwargs)


ID_MSG_MAP = {
    0: info_msg,
    1: std_msg,
    2: kill_msg,
    3: death_msg,
    4: up_msg,
    5: err_msg,
    6: link_msg,
    7: unlink_msg,
    8: reload_msg,
}
