from uuid import UUID
import actor.utils

INFO_MSG = 1
RCE_MSG = 2
KILL_MSG = 3
DEATH_MSG = 4
UP_MSG = 5
ERR_MSG = 6
LINK_MSG = 7
UNLINK_MSG = 8


class Pid(UUID):
    def __repr__(self):
        return f"Pid('{self.__str__()}')"

    # def __gt__(self, msg):
    # 	actor.utils.async_msg(self, msg)

    # def __rshift__(self, msg):
    # 	return actor.utils.sync_msg(self, msg)


class msg(dict):
    def __gt__(self, pid):
        actor.utils.async_msg(pid, self)

    def __rshift__(self, pid):
        return actor.utils.sync_msg(pid, self)
