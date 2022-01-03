from uuid import UUID
import actor.utils

class Pid(UUID):

	def __repr__(self):
		return f"Pid('{self.__str__()}')"

	def __gt__(self, msg):
		actor.utils.async_msg(self, msg)

	def __rshift__(self, msg):
		return actor.utils.sync_msg(self, msg)