from uuid import UUID
from dataclasses import dataclass
import actor.utils


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
