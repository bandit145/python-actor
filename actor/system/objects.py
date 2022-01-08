from uuid import UUID
import actor.utils
from actor.system.exceptions import InvalidMessage
import copy

INFO_MSG = "info_msg"
STD_MSG = "std_msg"
KILL_MSG = "kill_msg"
DEATH_MSG = "death_msg"
UP_MSG = "up_msg"
ERR_MSG = "err_msg"
LINK_MSG = "link_msg"
UNLINK_MSG = "unlink_msg"


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
            self.__required_format__["msg_type"] = str
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
    __required_format__ = {"data": dict}

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
